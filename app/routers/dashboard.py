from datetime import date
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.compte import Compte
from app.models.mouvement import Mouvement
from app.models.abonnement import Abonnement
from app.models.epargne import ObjectifEpargne
from app.models.placement import Placement
from app.models.mouvement import TypeMouvement

router = APIRouter(tags=["Dashboard"])

# Seuils de statut du "reste à vivre" mensuel
SEUIL_FAIBLE = 50
SEUIL_SURVEILLER = 150


def _statut_reste_a_vivre(montant: float) -> dict:
    if montant < SEUIL_FAIBLE:
        return {"label": "Faible", "color": "red"}
    if montant < SEUIL_SURVEILLER:
        return {"label": "Surveiller", "color": "orange"}
    return {"label": "Stable", "color": "emerald"}


templates = Jinja2Templates(directory="app/templates")


def _build_dashboard_context(db: Session) -> dict:
    comptes = db.query(Compte).all()
    abonnements = db.query(Abonnement).filter(Abonnement.actif == True).all()
    objectifs = db.query(ObjectifEpargne).filter(ObjectifEpargne.actif == True).all()
    placements = db.query(Placement).all()
    mouvements = db.query(Mouvement).order_by(Mouvement.date_mouvement.desc()).limit(20).all()

    total_liquidites = sum(c.solde for c in comptes)
    total_epargne = sum(o.montant_actuel for o in objectifs)
    total_investissements = sum(p.valeur_actuelle for p in placements)
    total_patrimoine = total_liquidites + total_epargne + total_investissements

    charges_mensuelles = sum(
        a.montant for a in abonnements if a.frequence.value == "Mensuelle"
    ) + sum(
        a.montant / 12 for a in abonnements if a.frequence.value == "Annuelle"
    )

    # Revenus du mois courant (mouvements de type "Entrée" du mois)
    today = date.today()
    revenus_mois = sum(
        m.montant for m in mouvements
        if m.type == TypeMouvement.entree
        and m.date_mouvement.month == today.month
        and m.date_mouvement.year == today.year
    )

    # Reste à vivre = Revenus - Dépenses fixes
    reste_a_vivre = revenus_mois - charges_mensuelles
    from calendar import monthrange
    jours_dans_mois = monthrange(today.year, today.month)[1]
    prochains = []
    for a in abonnements:
        if a.jour_prelevement >= today.day:
            jours_restants = a.jour_prelevement - today.day
        else:
            jours_restants = (jours_dans_mois - today.day) + a.jour_prelevement
        if jours_restants <= 7:
            a.jours_restants = jours_restants
            prochains.append(a)
    prochains.sort(key=lambda a: a.jours_restants)

    return {
        "comptes": comptes,
        "abonnements": abonnements,
        "mouvements": mouvements,
        "total_liquidites": round(total_liquidites, 2),
        "total_epargne": round(total_epargne, 2),
        "total_investissements": round(total_investissements, 2),
        "total_patrimoine": round(total_patrimoine, 2),
        "revenus_mois": round(revenus_mois, 2),
        "charges_mensuelles": round(charges_mensuelles, 2),
        "reste_a_vivre": round(reste_a_vivre, 2),
        "statut_reste_a_vivre": _statut_reste_a_vivre(reste_a_vivre),
        "prochains_prelevements": prochains,
    }


@router.get("/", summary="Page principale — Dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    context = _build_dashboard_context(db)
    context["request"] = request
    return templates.TemplateResponse("index.html", context)


@router.get("/api/v1/dashboard", summary="Données consolidées du dashboard (JSON)")
def get_dashboard_data(db: Session = Depends(get_db)):
    return _build_dashboard_context(db)
