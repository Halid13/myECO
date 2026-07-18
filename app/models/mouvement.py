from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database import Base


class TypeMouvement(str, enum.Enum):
    entree = "Entrée"
    sortie = "Sortie"


class Mouvement(Base):
    __tablename__ = "mouvement"

    id = Column(Integer, primary_key=True, index=True)
    id_compte = Column(Integer, ForeignKey("compte.id"), nullable=False)
    type = Column(Enum(TypeMouvement), nullable=False)
    montant = Column(Float, nullable=False)
    categorie = Column(String, nullable=True)
    description = Column(String, nullable=True)
    date_mouvement = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    compte = relationship("Compte", back_populates="mouvements")
