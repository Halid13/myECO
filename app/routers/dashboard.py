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
from app.services.assistant import generer_alertes

router = APIRouter(tags=["Dashboard"])
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

    # Prochains prélèvements (dans les 7 jours)
    today = date.today()
    prochains = [
        a for a in abonnements
        if abs(a.jour_prelevement - today.day) <= 7
        or (today.day > 24 and a.jour_prelevement <= 7)
    ]
    prochains.sort(key=lambda a: a.jour_prelevement)

    alertes = generer_alertes(db)

    return {
        "comptes": comptes,
        "mouvements": mouvements,
        "total_liquidites": round(total_liquidites, 2),
        "total_epargne": round(total_epargne, 2),
        "total_investissements": round(total_investissements, 2),
        "total_patrimoine": round(total_patrimoine, 2),
        "charges_mensuelles": round(charges_mensuelles, 2),
        "prochains_prelevements": prochains,
        "alertes": alertes,
    }


@router.get("/", summary="Page principale — Dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    context = _build_dashboard_context(db)
    context["request"] = request
    return templates.TemplateResponse("index.html", context)


@router.get("/api/v1/dashboard", summary="Données consolidées du dashboard (JSON)")
def get_dashboard_data(db: Session = Depends(get_db)):
    return _build_dashboard_context(db)
