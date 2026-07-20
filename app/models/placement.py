from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Placement(Base):
    __tablename__ = "placement"

    id = Column(Integer, primary_key=True, index=True)
    type_actif = Column(String, nullable=False)   # Actions, ETF, Crypto, Immo…
    nom_support = Column(String, nullable=False)
    capital_investi = Column(Float, default=0.0)
    valeur_actuelle = Column(Float, default=0.0)
    date_valorisation = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    date_investissement = Column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))
    description = Column(String, nullable=True)
    id_utilisateur = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)

    historique = relationship("HistoriqueInvestissement", back_populates="placement")


class HistoriqueInvestissement(Base):
    __tablename__ = "historique_investissement"

    id = Column(Integer, primary_key=True, index=True)
    id_placement = Column(Integer, ForeignKey("placement.id"), nullable=False)
    montant = Column(Float, nullable=False)  # delta : positif ou négatif
    type = Column(String, nullable=False)    # "versement" | "valorisation"
    date_operation = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    placement = relationship("Placement", back_populates="historique")
