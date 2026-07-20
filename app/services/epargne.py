"""Calculs liés au suivi des objectifs d'épargne (Module 4 — Épargne & Projets)."""
import math
from datetime import date
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.epargne import ObjectifEpargne, HistoriqueEpargne
from app.services.finances import mois_precedent, evolution_cumulee


def effort_epargne_mois(db: Session, id_utilisateur: int, today: date | None = None) -> dict:
    """Total épargné (dépôts positifs) ce mois-ci et le mois précédent, tous objectifs
    de l'utilisateur confondus."""
    today = today or date.today()
    annee_prec, mois_prec = mois_precedent(today.year, today.month)

    depots = (
        db.query(HistoriqueEpargne)
        .join(ObjectifEpargne)
        .filter(HistoriqueEpargne.montant > 0, ObjectifEpargne.id_utilisateur == id_utilisateur)
        .all()
    )

    effort_mois = sum(
        m.montant for m in depots
        if m.date_operation.year == today.year and m.date_operation.month == today.month
    )
    effort_mois_precedent = sum(
        m.montant for m in depots
        if m.date_operation.year == annee_prec and m.date_operation.month == mois_prec
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


def estimation_mois_restants(objectif: ObjectifEpargne) -> int | None:
    """Nombre de mois estimé pour atteindre la cible, au rythme net moyen des 3 derniers
    mois d'activité (ou de tout l'historique si moins de 3 mois de données).
    None si déjà atteint, sans historique, ou si le rythme actuel n'y mènera jamais."""
    reste = objectif.montant_cible - objectif.montant_actuel
    if reste <= 0:
        return None

    historique = sorted(objectif.historique, key=lambda h: h.date_operation)
    if not historique:
        return None

    totaux_par_mois = defaultdict(float)
    for h in historique:
        cle = (h.date_operation.year, h.date_operation.month)
        totaux_par_mois[cle] += h.montant

    derniers_totaux = list(totaux_par_mois.values())[-3:]
    rythme_moyen = sum(derniers_totaux) / len(derniers_totaux)

    if rythme_moyen <= 0:
        return None

    return math.ceil(reste / rythme_moyen)


def evolution_epargne(db: Session, id_utilisateur: int, nb_mois: int = 6, today: date | None = None) -> list[dict]:
    """Montant total épargné (cumulé, net) à la fin de chaque mois, sur les N derniers mois —
    approxime la trajectoire de croissance de l'épargne totale de l'utilisateur."""
    today = today or date.today()
    mouvements = (
        db.query(HistoriqueEpargne)
        .join(ObjectifEpargne)
        .filter(ObjectifEpargne.id_utilisateur == id_utilisateur)
        .order_by(HistoriqueEpargne.date_operation)
        .all()
    )
    return evolution_cumulee(mouvements, nb_mois, today)
