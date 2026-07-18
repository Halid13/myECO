"""Calculs financiers partagés entre plusieurs routers."""
from datetime import date
from sqlalchemy.orm import Session
from app.models.mouvement import Mouvement, TypeMouvement

# Palette de couleurs partagée pour tous les graphiques Chart.js du projet
# (donuts de répartition : abonnements par catégorie, épargne par projet, etc.)
CHART_COLORS = [
    "#f97316", "#ef4444", "#8b5cf6", "#3b82f6",
    "#10b981", "#eab308", "#ec4899", "#06b6d4",
    "#84cc16", "#f43f5e", "#6366f1", "#14b8a6",
]


def calculer_revenus_mois(db: Session, today: date | None = None) -> float:
    """Somme des mouvements de type Entrée du mois en cours, tous comptes confondus."""
    today = today or date.today()
    mouvements = db.query(Mouvement).filter(Mouvement.type == TypeMouvement.entree).all()
    return sum(
        m.montant for m in mouvements
        if m.date_mouvement.month == today.month and m.date_mouvement.year == today.year
    )
