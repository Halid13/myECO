from pydantic import BaseModel, field_validator
from datetime import datetime


class CompteBase(BaseModel):
    nom_banque: str
    solde: float = 0.0


class CompteCreate(CompteBase):
    pass


class CompteUpdate(BaseModel):
    """Utilisé uniquement pour l'ajustement du solde."""
    solde: float


class CompteRead(CompteBase):
    id: int
    date_maj: datetime

    model_config = {"from_attributes": True}
