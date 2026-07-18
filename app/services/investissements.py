"""Calculs liés au suivi du portefeuille d'investissements (Module 5 — Portefeuille)."""
from datetime import date
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.placement import Placement, HistoriqueInvestissement
from app.services.finances import mois_precedent, evolution_cumulee


def effort_investissement_mois(db: Session, today: date | None = None) -> dict:
    """Total versé (apports de capital) ce mois-ci et le mois précédent, tous placements confondus."""
    today = today or date.today()
    annee_prec, mois_prec = mois_precedent(today.year, today.month)

    versements = db.query(HistoriqueInvestissement).filter(
        HistoriqueInvestissement.type == "versement"
    ).all()

    effort_mois = sum(
        v.montant for v in versements
        if v.date_operation.year == today.year and v.date_operation.month == today.month
    )
    effort_mois_precedent = sum(
        v.montant for v in versements
        if v.date_operation.year == annee_prec and v.date_operation.month == mois_prec
    )

    if effort_mois_precedent > 0:
        delta_pct = round((effort_mois - effort_mois_precedent) / effort_mois_precedent * 100, 1)
    else:
        delta_pct = 100.0 if effort_mois > 0 else 0.0

    return {
        "mois": round(effort_mois, 2),
        "mois_precedent": round(effort_mois_precedent, 2),
        "delta_pct": delta_pct,
    }


def performance_globale(placements: list[Placement]) -> dict:
    """Capital total investi, valeur totale actuelle, plus-value € et performance % pondérée
    sur l'ensemble du portefeuille."""
    capital_total = sum(p.capital_investi for p in placements)
    valeur_total = sum(p.valeur_actuelle for p in placements)
    plus_value_totale = valeur_total - capital_total
    performance_pct = (plus_value_totale / capital_total * 100) if capital_total > 0 else 0.0

    return {
        "capital_total": round(capital_total, 2),
        "valeur_total": round(valeur_total, 2),
        "plus_value_totale": round(plus_value_totale, 2),
        "performance_pct": round(performance_pct, 2),
    }


def repartition_par_type(placements: list[Placement]) -> dict:
    """Valeur actuelle totale groupée par type d'actif."""
    repartition = defaultdict(float)
    for p in placements:
        repartition[p.type_actif] += p.valeur_actuelle
    return {k: round(v, 2) for k, v in repartition.items()}


def evolution_portefeuille(db: Session, nb_mois: int = 6, today: date | None = None) -> list[dict]:
    """Valeur cumulée du portefeuille par mois, sur les N derniers mois — combine versements
    (apports) et valorisations (variations de marché), toutes deux journalisées comme deltas."""
    today = today or date.today()
    mouvements = db.query(HistoriqueInvestissement).order_by(HistoriqueInvestissement.date_operation).all()
    return evolution_cumulee(mouvements, nb_mois, today)
