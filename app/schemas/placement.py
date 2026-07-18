from pydantic import BaseModel, field_validator, computed_field
from datetime import datetime


class PlacementBase(BaseModel):
    type_actif: str
    nom_support: str
    capital_investi: float
    valeur_actuelle: float
    date_investissement: datetime | None = None
    description: str | None = None

    @field_validator("capital_investi", "valeur_actuelle")
    @classmethod
    def montant_positif(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Les montants ne peuvent pas être négatifs.")
        return v


class PlacementRead(PlacementBase):
    id: int
    date_valorisation: datetime

    @computed_field
    @property
    def plus_value(self) -> float:
        return round(self.valeur_actuelle - self.capital_investi, 2)

    @computed_field
    @property
    def performance_pct(self) -> float | None:
        if self.capital_investi == 0:
            return None
        return round((self.plus_value / self.capital_investi) * 100, 2)

    model_config = {"from_attributes": True}
