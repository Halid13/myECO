from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database import Base


class Recommandation(Base):
    """Une recommandation générée par le moteur de règles (Module 6 — Assistant Intelligent).

    Persistée pour permettre l'historique et le suivi de statut : sans ça, une recommandation
    recalculée à chaque page vue ne peut jamais être "lue", "ignorée" ni conservée en historique.
    """
    __tablename__ = "recommandation"

    id = Column(Integer, primary_key=True, index=True)
    type_regle = Column(String, nullable=False)       # ex: "charges_fixes_elevees"
    cle_contexte = Column(String, nullable=False)      # dédup : "global", "compte:3", "objectif:5"...
    niveau = Column(String, nullable=False)            # "info" | "warning" | "success"
    icone = Column(String, nullable=True)               # nom d'icône optionnel (sinon déduit du niveau)
    titre = Column(String, nullable=False)
    message = Column(String, nullable=False)
    lien = Column(String, nullable=True)
    statut = Column(String, nullable=False, default="nouveau")  # nouveau | lu | ignore | resolu

    date_creation = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    date_derniere_detection = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    date_resolution = Column(DateTime, nullable=True)
