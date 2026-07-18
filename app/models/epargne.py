from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class ObjectifEpargne(Base):
    __tablename__ = "objectif_epargne"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    montant_actuel = Column(Float, default=0.0)
    montant_cible = Column(Float, nullable=False)
    date_limite = Column(DateTime, nullable=True)
    actif = Column(Boolean, default=True)

    historique = relationship("HistoriqueEpargne", back_populates="objectif")


class HistoriqueEpargne(Base):
    __tablename__ = "historique_epargne"

    id = Column(Integer, primary_key=True, index=True)
    id_objectif = Column(Integer, ForeignKey("objectif_epargne.id"), nullable=False)
    montant = Column(Float, nullable=False)
    date_operation = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    objectif = relationship("ObjectifEpargne", back_populates="historique")
