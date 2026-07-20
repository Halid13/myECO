"""Calculs financiers partagés entre plusieurs routers."""
from datetime import date
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.mouvement import Mouvement, TypeMouvement
from app.models.compte import Compte

# Palette de couleurs partagée pour tous les graphiques Chart.js du projet
# (donuts de répartition : abonnements par catégorie, épargne par projet, etc.)
CHART_COLORS = [
    "#f97316", "#ef4444", "#8b5cf6", "#3b82f6",
    "#10b981", "#eab308", "#ec4899", "#06b6d4",
    "#84cc16", "#f43f5e", "#6366f1", "#14b8a6",
]

MOIS_FR_COURT = [
    "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
    "Juil", "Août", "Sep", "Oct", "Nov", "Déc",
]


def mois_precedent(annee: int, mois: int) -> tuple[int, int]:
    """Retourne (année, mois) du mois précédent — gère le passage à l'année d'avant."""
    if mois == 1:
        return annee - 1, 12
    return annee, mois - 1


def calculer_mouvements_mois(db: Session, type_mouvement: TypeMouvement, id_utilisateur: int, today: date | None = None) -> dict:
    """Somme des mouvements d'un type donné (Entrée/Sortie), ce mois et le mois précédent,
    tous comptes de l'utilisateur confondus."""
    today = today or date.today()
    annee_prec, mois_prec = mois_precedent(today.year, today.month)
    mouvements = (
        db.query(Mouvement)
        .join(Compte)
        .filter(Mouvement.type == type_mouvement, Compte.id_utilisateur == id_utilisateur)
        .all()
    )
    mois = sum(
        m.montant for m in mouvements
        if m.date_mouvement.year == today.year and m.date_mouvement.month == today.month
    )
    mois_precedent_total = sum(
        m.montant for m in mouvements
        if m.date_mouvement.year == annee_prec and m.date_mouvement.month == mois_prec
    )
    return {"mois": round(mois, 2), "mois_precedent": round(mois_precedent_total, 2)}


def calculer_revenus_mois(db: Session, id_utilisateur: int, today: date | None = None) -> float:
    """Somme des mouvements de type Entrée du mois en cours, tous comptes de l'utilisateur confondus."""
    return calculer_mouvements_mois(db, TypeMouvement.entree, id_utilisateur, today)["mois"]


# Coefficients de conversion vers un équivalent mensuel, par fréquence d'abonnement
# (mêmes valeurs que app/routers/abonnements.py — dupliqué volontairement à l'identique
# pour ne pas re-brancher tout ce module dans cette passe)
COEFF_MENSUEL = {
    "Mensuelle": 1, "Trimestrielle": 1 / 3, "Semestrielle": 1 / 6, "Annuelle": 1 / 12
}


def calculer_charges_mensuelles(abonnements: list) -> float:
    """Coût mensuel équivalent de tous les abonnements actifs, toutes fréquences confondues."""
    return sum(
        a.montant * COEFF_MENSUEL.get(a.frequence.value, 1)
        for a in abonnements
    )


def evolution_cumulee(mouvements: list, nb_mois: int, today: date) -> list[dict]:
    """Total cumulé (net) par mois sur les N derniers mois, à partir d'une liste d'objets
    possédant `.montant` et `.date_operation` (ex: HistoriqueEpargne, HistoriqueInvestissement).
    Retourne [] si la liste est vide (pas encore d'historique)."""
    if not mouvements:
        return []

    mois_cibles = []
    annee, mois = today.year, today.month
    for _ in range(nb_mois):
        mois_cibles.append((annee, mois))
        annee, mois = mois_precedent(annee, mois)
    mois_cibles.reverse()

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
