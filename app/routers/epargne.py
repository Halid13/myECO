from datetime import date, datetime, timezone
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.epargne import ObjectifEpargne, HistoriqueEpargne
from app.models.compte import Compte
from app.models.mouvement import Mouvement, TypeMouvement
from app.schemas.epargne import ObjectifEpargneRead
from app.services.finances import CHART_COLORS
from app.services.epargne import (
    effort_epargne_mois,
    estimation_mois_restants,
    evolution_epargne,
)
from app.routers.investissements import build_investissements_context

router = APIRouter(tags=["Épargne"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/patrimoine/", summary="Page Patrimoine (Épargne & Investissements)")
def page_patrimoine(request: Request, db: Session = Depends(get_db)):
    today = date.today()
    objectifs = db.query(ObjectifEpargne).filter(ObjectifEpargne.actif == True).all()
    comptes = db.query(Compte).all()

    for obj in objectifs:
        obj.progression_pct = round((obj.montant_actuel / obj.montant_cible) * 100, 1) if obj.montant_cible else 0.0
        obj.mois_restants_estimes = estimation_mois_restants(obj)
        obj.derniers_mouvements = sorted(
            obj.historique, key=lambda h: h.date_operation, reverse=True
        )[:3]

    total_epargne = round(sum(o.montant_actuel for o in objectifs), 2)
    effort = effort_epargne_mois(db, today)
    top_proches = sorted(
        [o for o in objectifs if o.progression_pct < 100],
        key=lambda o: o.progression_pct,
        reverse=True,
    )[:3]

    context = {
        "request": request,
        "objectifs": objectifs,
        "comptes": comptes,
        "total_epargne": total_epargne,
        "effort_mois": effort["mois"],
        "effort_mois_precedent": effort["mois_precedent"],
        "evolution": evolution_epargne(db, today=today),
        "top_proches": top_proches,
        "chart_colors": CHART_COLORS,
    }
    context.update(build_investissements_context(db, today))
    return templates.TemplateResponse("patrimoine.html", context)


@router.get("/api/v1/epargne", response_model=list[ObjectifEpargneRead], summary="Lister les objectifs d'épargne")
def lister_objectifs(db: Session = Depends(get_db)):
    objectifs = db.query(ObjectifEpargne).filter(ObjectifEpargne.actif == True).all()
    result = []
    for obj in objectifs:
        data = ObjectifEpargneRead.model_validate(obj)
        data.progression_pct = round((obj.montant_actuel / obj.montant_cible) * 100, 1) if obj.montant_cible else 0.0
        result.append(data)
    return result


@router.post("/api/v1/epargne", response_model=ObjectifEpargneRead, status_code=201, summary="Créer un objectif d'épargne")
def creer_objectif(
    nom: str = Form(...),
    montant_cible: float = Form(...),
    id_compte: int | None = Form(None),
    date_limite: str | None = Form(None),
    db: Session = Depends(get_db)
):
    if montant_cible <= 0:
        raise HTTPException(status_code=400, detail="Le montant cible doit être strictement positif.")

    date_limite_dt = None
    if date_limite:
        try:
            date_limite_dt = datetime.strptime(date_limite, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Date cible invalide.")

    if id_compte is not None and not db.get(Compte, id_compte):
        raise HTTPException(status_code=404, detail="Compte associé introuvable")

    objectif = ObjectifEpargne(
        nom=nom,
        montant_cible=montant_cible,
        id_compte=id_compte,
        date_limite=date_limite_dt,
    )
    db.add(objectif)
    db.commit()
    db.refresh(objectif)
    objectif.progression_pct = 0.0
    return objectif


@router.put("/api/v1/epargne/{objectif_id}/update", response_model=ObjectifEpargneRead, summary="Alimenter ou retirer d'une poche")
def update_epargne(
    objectif_id: int,
    montant: float = Form(...),
    deduire_compte: bool = Form(False),
    db: Session = Depends(get_db)
):
    objectif = db.get(ObjectifEpargne, objectif_id)
    if not objectif:
        raise HTTPException(status_code=404, detail="Objectif introuvable")
    objectif.montant_actuel = round(objectif.montant_actuel + montant, 2)
    if objectif.montant_actuel < 0:
        raise HTTPException(status_code=400, detail="Le solde de la poche ne peut pas être négatif")

    if deduire_compte and objectif.id_compte:
        compte = db.get(Compte, objectif.id_compte)
        if compte:
            compte.solde = round(compte.solde - montant, 2)
            compte.date_maj = datetime.now(timezone.utc)

            mouvement = Mouvement(
                id_compte=compte.id,
                type=TypeMouvement.sortie if montant > 0 else TypeMouvement.entree,
                montant=abs(montant),
                categorie="Épargne",
                description=f"{'Épargne vers' if montant > 0 else 'Retrait depuis'} \"{objectif.nom}\"",
            )
            db.add(mouvement)

    historique = HistoriqueEpargne(id_objectif=objectif_id, montant=montant)
    db.add(historique)
    db.commit()
    db.refresh(objectif)
    result = ObjectifEpargneRead.model_validate(objectif)
    result.progression_pct = round((objectif.montant_actuel / objectif.montant_cible) * 100, 1) if objectif.montant_cible else 0.0
    return result


@router.delete("/api/v1/epargne/{objectif_id}", status_code=204, summary="Clôturer un objectif d'épargne")
def cloturer_objectif(objectif_id: int, db: Session = Depends(get_db)):
    objectif = db.get(ObjectifEpargne, objectif_id)
    if not objectif:
        raise HTTPException(status_code=404, detail="Objectif introuvable")
    objectif.actif = False
    db.commit()
