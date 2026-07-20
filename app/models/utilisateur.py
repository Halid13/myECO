from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id = Column(Integer, primary_key=True, index=True)
    identifiant = Column(String, nullable=False, unique=True)
    mot_de_passe_hash = Column(String, nullable=False)
    date_creation = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    derniere_connexion = Column(DateTime, nullable=True)
