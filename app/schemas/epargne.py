from pydantic import BaseModel, field_validator
from datetime import datetime


class ObjectifEpargneBase(BaseModel):
    nom: str
    montant_cible: float
    date_limite: datetime | None = None
    id_compte: int | None = None

    @field_validator("montant_cible")
    @classmethod
    def cible_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Le montant cible doit être strictement positif.")
        return v


class ObjectifEpargneRead(ObjectifEpargneBase):
    id: int
    montant_actuel: float
    actif: bool
    progression_pct: float = 0.0  # calculé à la volée par le router

    model_config = {"from_attributes": True}
