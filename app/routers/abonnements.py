from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
import calendar
from app.database import get_db
from app.auth import get_current_user, utilisateur_connecte
from app.models.abonnement import Abonnement
from app.models.compte import Compte
from app.schemas.abonnement import AbonnementCreate, AbonnementUpdate, AbonnementRead
from app.services.finances import CHART_COLORS

router = APIRouter(tags=["Abonnements"])
templates = Jinja2Templates(directory="app/templates")

CATEGORIES = [
    "Streaming", "Musique", "Sport & Bien-être", "Santé & Mutuelle",
    "Assurances", "Énergie & Eau", "Téléphonie & Internet", "Logement",
    "Transport", "Logiciels & Outils", "Alimentation", "Autre"
]

COEFF_MENSUEL = {
    "Mensuelle": 1, "Trimestrielle": 1/3, "Semestrielle": 1/6, "Annuelle": 1/12
}
COEFF_ANNUEL = {
    "Mensuelle": 12, "Trimestrielle": 4, "Semestrielle": 2, "Annuelle": 1
}

MOIS_FR = [
    "janvier", "février", "mars", "avril", "mai", "juin",
    "juillet", "août", "septembre", "octobre", "novembre", "décembre",
]
JOURS_SEMAINE_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]


PAGE_SIZE = 6


@router.get("/abonnements/", summary="Page Charges Fixes & Abonnements")
def page_abonnements(request: Request, page: int = 1, db: Session = Depends(get_db)):
    if not utilisateur_connecte(request, db):
        return RedirectResponse("/login")
    abonnements = (
        db.query(Abonnement)
        .filter(Abonnement.actif == True)
        .order_by(Abonnement.jour_prelevement)
        .all()
    )

    nb_pages = max(1, -(-len(abonnements) // PAGE_SIZE))
    page = min(max(1, page), nb_pages)
    debut = (page - 1) * PAGE_SIZE
    abonnements_page = abonnements[debut:debut + PAGE_SIZE]

    today = date.today()
    premier_jour_semaine, days_in_month = calendar.monthrange(today.year, today.month)
    mois_annee_fr = f"{MOIS_FR[today.month - 1].capitalize()} {today.year}"

    total_mensuel = round(sum(
        a.montant * COEFF_MENSUEL.get(a.frequence.value, 1)
        for a in abonnements
    ), 2)
    total_annuel = round(sum(
        a.montant * COEFF_ANNUEL.get(a.frequence.value, 12)
        for a in abonnements
    ), 2)

    # Prochains 7 jours avec jours_restants
    prochains = []
    for a in abonnements:
        j = a.jour_prelevement
        jr = j - today.day if j >= today.day else days_in_month - today.day + j
        if 0 <= jr <= 7:
            a.jours_restants = jr
            prochains.append(a)

    # Répartition par catégorie
    categories = {}
    for a in abonnements:
        cat = a.categorie or "Autre"
        categories[cat] = round(
            categories.get(cat, 0) + a.montant * COEFF_MENSUEL.get(a.frequence.value, 1), 2
        )

    # Timeline : abonnements par jour du mois
    par_jour = {}
    for a in abonnements:
        j = a.jour_prelevement
        par_jour.setdefault(j, []).append(a)

    return templates.TemplateResponse("abonnements.html", {
        "request": request,
        "abonnements": abonnements_page,
        "page": page,
        "nb_pages": nb_pages,
        "comptes_list": db.query(Compte).all(),
        "prochains": prochains,
        "total_mensuel": total_mensuel,
        "total_annuel": total_annuel,
        "nb_actifs": len(abonnements),
        "categories": categories,
        "par_jour": par_jour,
        "today": today,
        "categories_liste": CATEGORIES,
        "days_in_month": days_in_month,
        "premier_jour_semaine": premier_jour_semaine,
        "mois_annee_fr": mois_annee_fr,
        "jours_semaine_fr": JOURS_SEMAINE_FR,
        "chart_colors": CHART_COLORS,
    })


@router.post("/api/v1/abonnements", response_model=AbonnementRead, status_code=201, summary="Créer un abonnement")
def creer_abonnement(
    libelle: str = Form(...),
    montant: float = Form(...),
    frequence: str = Form("Mensuelle"),
    jour_prelevement: int = Form(...),
    id_compte: int = Form(...),
    categorie: str = Form(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    from app.models.abonnement import FrequenceAbonnement
    
    # Convertir string en Enum
    frequence_enum = FrequenceAbonnement(frequence)
    
    abonnement = Abonnement(
        libelle=libelle,
        montant=montant,
        frequence=frequence_enum,
        jour_prelevement=jour_prelevement,
        id_compte=id_compte,
        categorie=categorie,
        actif=True
    )
    db.add(abonnement)
    db.commit()
    db.refresh(abonnement)
    return abonnement


@router.get("/api/v1/abonnements", response_model=list[AbonnementRead], summary="Lister les abonnements")
def lister_abonnements(actif: bool | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(Abonnement)
    if actif is not None:
        q = q.filter(Abonnement.actif == actif)
    return q.order_by(Abonnement.jour_prelevement).all()


@router.put("/api/v1/abonnements/{abonnement_id}", response_model=AbonnementRead, summary="Modifier un abonnement")
def modifier_abonnement(abonnement_id: int, payload: AbonnementUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    abonnement = db.get(Abonnement, abonnement_id)
    if not abonnement:
        raise HTTPException(status_code=404, detail="Abonnement introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(abonnement, field, value)
    db.commit()
    db.refresh(abonnement)
    return abonnement


@router.delete("/api/v1/abonnements/{abonnement_id}", status_code=204, summary="Supprimer un abonnement")
def supprimer_abonnement(abonnement_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    abonnement = db.get(Abonnement, abonnement_id)
    if not abonnement:
        raise HTTPException(status_code=404, detail="Abonnement introuvable")
    db.delete(abonnement)
    db.commit()


# ==================== ENDPOINTS PRÉLÈVEMENTS AUTOMATIQUES ====================

@router.get("/api/v1/prelevements/prochains", summary="Lister les prochains prélèvements")
def get_prochains_prelevements(jours: int = 30, user=Depends(get_current_user)):
    """Retourne la liste des prochains prélèvements dans N jours (info uniquement)."""
    from app.services.prelevements import obtenir_prochains_prelevements
    return obtenir_prochains_prelevements(jours)
