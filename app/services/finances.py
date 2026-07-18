"""Calculs financiers partagés entre plusieurs routers."""
from datetime import date
from sqlalchemy.orm import Session
from app.models.mouvement import Mouvement, TypeMouvement


def calculer_revenus_mois(db: Session, today: date | None = None) -> float:
    """Somme des mouvements de type Entrée du mois en cours, tous comptes confondus."""
    today = today or date.today()
    mouvements = db.query(Mouvement).filter(Mouvement.type == TypeMouvement.entree).all()
    return sum(
        m.montant for m in mouvements
        if m.date_mouvement.month == today.month and m.date_mouvement.year == today.year
    )
