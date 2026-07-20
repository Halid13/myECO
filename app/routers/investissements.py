from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.placement import Placement, HistoriqueInvestissement
from app.schemas.placement import PlacementRead
from app.services.investissements import (
    effort_investissement_mois,
    performance_globale,
    repartition_par_type,
    evolution_portefeuille,
)

router = APIRouter(tags=["Investissements"])

TYPES_ACTIFS = [
    "Actions", "ETF", "Crypto", "Obligations", "Immobilier",
    "Assurance-vie", "PEA", "PEE/PER", "Autre",
]

# Couleur fixe par type d'actif — cohérente entre le tableau (badges) et le donut de répartition
TYPE_COLORS = {
    "Actions": "#3b82f6",
    "ETF": "#06b6d4",
    "Crypto": "#f97316",
    "Obligations": "#8b5cf6",
    "Immobilier": "#10b981",
    "Assurance-vie": "#ec4899",
    "PEA": "#6366f1",
    "PEE/PER": "#14b8a6",
    "Autre": "#6b7280",
}


def build_investissements_context(db: Session, today: date) -> dict:
    """Prépare tout le contexte du Module 5, fusionné dans /patrimoine/ par epargne.py."""
    placements = db.query(Placement).order_by(Placement.date_investissement.desc()).all()
    for p in placements:
        p.plus_value = round(p.valeur_actuelle - p.capital_investi, 2)
        p.performance_pct = round((p.plus_value / p.capital_investi) * 100, 2) if p.capital_investi else None

    perf = performance_globale(placements)
    effort = effort_investissement_mois(db, today)

    return {
        "placements": placements,
        "types_actifs": TYPES_ACTIFS,
        "type_colors": TYPE_COLORS,
        "portefeuille_valeur": perf["valeur_total"],
        "portefeuille_capital": perf["capital_total"],
        "portefeuille_plus_value": perf["plus_value_totale"],
        "portefeuille_performance_pct": perf["performance_pct"],
        "investi_mois": effort["mois"],
        "investi_mois_precedent": effort["mois_precedent"],
        "delta_investi_pct": effort["delta_pct"],
        "repartition_investissements": repartition_par_type(placements),
        "evolution_investissements": evolution_portefeuille(db, today=today),
    }


@router.get("/api/v1/investissements", response_model=list[PlacementRead], summary="Lister les placements")
def lister_placements(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Placement).all()


@router.post("/api/v1/investissements", response_model=PlacementRead, status_code=201, summary="Déclarer un placement")
def creer_placement(
    nom_support: str = Form(...),
    type_actif: str = Form(...),
    capital_investi: float = Form(...),
    valeur_actuelle: float = Form(...),
    date_investissement: str = Form(None),
    description: str = Form(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if capital_investi < 0 or valeur_actuelle < 0:
        raise HTTPException(status_code=400, detail="Les montants ne peuvent pas être négatifs.")

    date_investissement_dt = None
    if date_investissement:
        try:
            date_investissement_dt = datetime.strptime(date_investissement, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Date d'investissement invalide.")

    placement = Placement(
        nom_support=nom_support,
        type_actif=type_actif,
        capital_investi=capital_investi,
        valeur_actuelle=valeur_actuelle,
        date_investissement=date_investissement_dt or datetime.now(timezone.utc),
        description=description,
    )
    db.add(placement)
    db.commit()
    db.refresh(placement)

    if capital_investi > 0:
        db.add(HistoriqueInvestissement(id_placement=placement.id, montant=capital_investi, type="versement"))
        db.commit()

    return placement


@router.put("/api/v1/investissements/{placement_id}", response_model=PlacementRead, summary="Modifier un placement")
def modifier_placement(
    placement_id: int,
    nom_support: str = Form(None),
    type_actif: str = Form(None),
    description: str = Form(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    placement = db.get(Placement, placement_id)
    if not placement:
        raise HTTPException(status_code=404, detail="Placement introuvable")
    if nom_support is not None:
        placement.nom_support = nom_support
    if type_actif is not None:
        placement.type_actif = type_actif
    if description is not None:
        placement.description = description
    db.commit()
    db.refresh(placement)
    return placement


@router.put("/api/v1/investissements/{placement_id}/value", response_model=PlacementRead, summary="Mettre à jour la valeur liquidative")
def update_valeur(placement_id: int, valeur_actuelle: float = Form(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    placement = db.get(Placement, placement_id)
    if not placement:
        raise HTTPException(status_code=404, detail="Placement introuvable")
    if valeur_actuelle < 0:
        raise HTTPException(status_code=400, detail="La valeur ne peut pas être négative.")

    delta = round(valeur_actuelle - placement.valeur_actuelle, 2)
    placement.valeur_actuelle = valeur_actuelle
    placement.date_valorisation = datetime.now(timezone.utc)
    db.commit()

    if delta != 0:
        db.add(HistoriqueInvestissement(id_placement=placement_id, montant=delta, type="valorisation"))
        db.commit()

    db.refresh(placement)
    return placement


@router.put("/api/v1/investissements/{placement_id}/versement", response_model=PlacementRead, summary="Ajouter un versement complémentaire")
def ajouter_versement(placement_id: int, montant: float = Form(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    placement = db.get(Placement, placement_id)
    if not placement:
        raise HTTPException(status_code=404, detail="Placement introuvable")
    if montant <= 0:
        raise HTTPException(status_code=400, detail="Le montant du versement doit être strictement positif.")

    placement.capital_investi = round(placement.capital_investi + montant, 2)
    placement.valeur_actuelle = round(placement.valeur_actuelle + montant, 2)
    db.add(HistoriqueInvestissement(id_placement=placement_id, montant=montant, type="versement"))
    db.commit()
    db.refresh(placement)
    return placement


@router.delete("/api/v1/investissements/{placement_id}", status_code=204, summary="Supprimer un placement")
def supprimer_placement(placement_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    placement = db.get(Placement, placement_id)
    if not placement:
        raise HTTPException(status_code=404, detail="Placement introuvable")
    db.query(HistoriqueInvestissement).filter(HistoriqueInvestissement.id_placement == placement_id).delete()
    db.delete(placement)
    db.commit()
