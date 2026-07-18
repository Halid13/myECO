"""Calculs liés au suivi des objectifs d'épargne (Module 4 — Épargne & Projets)."""
import math
from datetime import date
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.epargne import ObjectifEpargne, HistoriqueEpargne

MOIS_FR_COURT = [
    "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
    "Juil", "Août", "Sep", "Oct", "Nov", "Déc",
]


def _mois_precedent(annee: int, mois: int) -> tuple[int, int]:
    if mois == 1:
        return annee - 1, 12
    return annee, mois - 1


def effort_epargne_mois(db: Session, today: date | None = None) -> dict:
    """Total épargné (dépôts positifs) ce mois-ci et le mois précédent, tous objectifs confondus."""
    today = today or date.today()
    annee_prec, mois_prec = _mois_precedent(today.year, today.month)

    depots = db.query(HistoriqueEpargne).filter(HistoriqueEpargne.montant > 0).all()

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


def taux_epargne_mensuel(effort_mois: float, revenus_mois: float) -> float:
    """Pourcentage des revenus du mois qui a été épargné."""
    if revenus_mois <= 0:
        return 0.0
    return round(effort_mois / revenus_mois * 100, 1)


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


def evolution_epargne(db: Session, nb_mois: int = 6, today: date | None = None) -> list[dict]:
    """Montant total épargné (cumulé, net) à la fin de chaque mois, sur les N derniers mois —
    approxime la trajectoire de croissance de l'épargne totale."""
    today = today or date.today()

    mois_cibles = []
    annee, mois = today.year, today.month
    for _ in range(nb_mois):
        mois_cibles.append((annee, mois))
        annee, mois = _mois_precedent(annee, mois)
    mois_cibles.reverse()

    mouvements = db.query(HistoriqueEpargne).order_by(HistoriqueEpargne.date_operation).all()
    if not mouvements:
        return []

    premiere_annee, premier_mois = mois_cibles[0]
    cumul = sum(
        m.montant for m in mouvements
        if (m.date_operation.year, m.date_operation.month) < (premiere_annee, premier_mois)
    )

    totaux_par_mois = defaultdict(float)
    for m in mouvements:
        cle = (m.date_operation.year, m.date_operation.month)
        totaux_par_mois[cle] += m.montant

    resultat = []
    for annee, mois in mois_cibles:
        cumul += totaux_par_mois.get((annee, mois), 0.0)
        resultat.append({"label": MOIS_FR_COURT[mois - 1], "total": round(cumul, 2)})
    return resultat
