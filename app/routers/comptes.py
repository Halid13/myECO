from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.compte import Compte
from app.models.mouvement import Mouvement
from app.models.abonnement import Abonnement
from app.schemas.compte import CompteCreate, CompteRead, CompteUpdate
from app.schemas.mouvement import MouvementCreate, MouvementRead

router = APIRouter(tags=["Comptes"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/comptes/", summary="Page Mouvements & Comptes")
def page_comptes(request: Request, compte_id: int | None = None, db: Session = Depends(get_db)):
    comptes = db.query(Compte).all()
    q = db.query(Mouvement)
    if compte_id:
        q = q.filter(Mouvement.id_compte == compte_id)
    mouvements = q.order_by(Mouvement.date_mouvement.desc()).limit(100).all()
    abonnements = db.query(Abonnement).filter(Abonnement.actif == True).order_by(Abonnement.jour_prelevement).all()
    total_liquidites = sum(c.solde for c in comptes)
    return templates.TemplateResponse("mouvements.html", {
        "request": request,
        "comptes": comptes,
        "mouvements": mouvements,
        "abonnements": abonnements,
        "total_liquidites": round(total_liquidites, 2),
        "filtre_compte_id": compte_id,
    })


# --- Comptes ---

@router.get("/api/v1/comptes", response_model=list[CompteRead], summary="Lister les comptes")
def lister_comptes(db: Session = Depends(get_db)):
    return db.query(Compte).all()


@router.post("/api/v1/comptes", response_model=CompteRead, status_code=201, summary="Créer un compte")
def creer_compte(
    nom_banque: str = Form(...),
    solde: float = Form(0.0),
    db: Session = Depends(get_db)
):
    compte = Compte(nom_banque=nom_banque, solde=solde, date_maj=datetime.now(timezone.utc))
    db.add(compte)
    db.commit()
    db.refresh(compte)
    return compte


@router.put("/api/v1/comptes/{compte_id}/solde", response_model=CompteRead, summary="Ajuster le solde")
def ajuster_solde(
    compte_id: int,
    solde: float = Form(...),
    db: Session = Depends(get_db)
):
    compte = db.get(Compte, compte_id)
    if not compte:
        raise HTTPException(status_code=404, detail="Compte introuvable")
    compte.solde = solde
    compte.date_maj = datetime.now(timezone.utc)
    db.commit()
    db.refresh(compte)
    return compte


@router.delete("/api/v1/comptes/{compte_id}", status_code=204, summary="Supprimer un compte")
def supprimer_compte(compte_id: int, db: Session = Depends(get_db)):
    compte = db.get(Compte, compte_id)
    if not compte:
        raise HTTPException(status_code=404, detail="Compte introuvable")
    db.delete(compte)
    db.commit()


# --- Mouvements ---

@router.get("/api/v1/mouvements", response_model=list[MouvementRead], summary="Lister les mouvements")
def lister_mouvements(compte_id: int | None = None, db: Session = Depends(get_db)):
    q = db.query(Mouvement)
    if compte_id:
        q = q.filter(Mouvement.id_compte == compte_id)
    return q.order_by(Mouvement.date_mouvement.desc()).all()


@router.post("/api/v1/mouvements", response_model=MouvementRead, status_code=201, summary="Enregistrer un mouvement")
def creer_mouvement(
    id_compte: int = Form(...),
    type: str = Form(...),
    montant: float = Form(...),
    categorie: str = Form(None),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    compte = db.get(Compte, id_compte)
    if not compte:
        raise HTTPException(status_code=404, detail="Compte introuvable")
    mouvement = Mouvement(
        id_compte=id_compte,
        type=type,
        montant=montant,
        categorie=categorie,
        description=description,
        date_mouvement=datetime.now(timezone.utc)
    )
    # Mise à jour du solde du compte
    if mouvement.type.value == "Entrée":
        compte.solde += mouvement.montant
    else:
        compte.solde -= mouvement.montant
    compte.date_maj = datetime.now(timezone.utc)
    db.add(mouvement)
    db.commit()
    db.refresh(mouvement)
    return mouvement


@router.delete("/api/v1/mouvements/{mouvement_id}", status_code=204, summary="Supprimer un mouvement")
def supprimer_mouvement(mouvement_id: int, db: Session = Depends(get_db)):
    mouvement = db.get(Mouvement, mouvement_id)
    if not mouvement:
        raise HTTPException(status_code=404, detail="Mouvement introuvable")
    db.delete(mouvement)
    db.commit()
