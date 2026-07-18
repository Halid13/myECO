from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.database import Base


class Placement(Base):
    __tablename__ = "placement"

    id = Column(Integer, primary_key=True, index=True)
    type_actif = Column(String, nullable=False)   # Actions, Crypto, Immo…
    nom_support = Column(String, nullable=False)
    capital_investi = Column(Float, default=0.0)
    valeur_actuelle = Column(Float, default=0.0)
    date_valorisation = Column(DateTime, default=lambda: datetime.now(timezone.utc))
