from pydantic import BaseModel, field_validator
from datetime import datetime
from app.models.mouvement import TypeMouvement


class MouvementBase(BaseModel):
    id_compte: int
    type: TypeMouvement
    montant: float
    categorie: str | None = None
    description: str | None = None
    date_mouvement: datetime | None = None

    @field_validator("montant")
    @classmethod
    def montant_positif(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Le montant doit être strictement positif.")
        return v


class MouvementCreate(MouvementBase):
    pass


class MouvementRead(MouvementBase):
    id: int
    date_mouvement: datetime

    model_config = {"from_attributes": True}
