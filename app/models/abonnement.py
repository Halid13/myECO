from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class FrequenceAbonnement(str, enum.Enum):
    mensuelle = "Mensuelle"
    annuelle = "Annuelle"


class Abonnement(Base):
    __tablename__ = "abonnement"

    id = Column(Integer, primary_key=True, index=True)
    libelle = Column(String, nullable=False)
    montant = Column(Float, nullable=False)
    frequence = Column(Enum(FrequenceAbonnement), default=FrequenceAbonnement.mensuelle)
    jour_prelevement = Column(Integer, nullable=False)  # 1 à 31
    id_compte = Column(Integer, ForeignKey("compte.id"), nullable=False)
    actif = Column(Boolean, default=True)

    compte = relationship("Compte", back_populates="abonnements")
