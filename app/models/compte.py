from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Compte(Base):
    __tablename__ = "compte"

    id = Column(Integer, primary_key=True, index=True)
    nom_banque = Column(String, nullable=False)
    solde = Column(Float, nullable=False, default=0.0)
    date_maj = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    id_utilisateur = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)

    mouvements = relationship("Mouvement", back_populates="compte")
    abonnements = relationship("Abonnement", back_populates="compte")
