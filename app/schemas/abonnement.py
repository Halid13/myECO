from pydantic import BaseModel, field_validator
from app.models.abonnement import FrequenceAbonnement


class AbonnementBase(BaseModel):
    libelle: str
    montant: float
    frequence: FrequenceAbonnement = FrequenceAbonnement.mensuelle
    jour_prelevement: int
    id_compte: int
    actif: bool = True

    @field_validator("jour_prelevement")
    @classmethod
    def jour_valide(cls, v: int) -> int:
        if not 1 <= v <= 31:
            raise ValueError("Le jour de prélèvement doit être compris entre 1 et 31.")
        return v

    @field_validator("montant")
    @classmethod
    def montant_positif(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Le montant doit être strictement positif.")
        return v


class AbonnementCreate(AbonnementBase):
    pass


class AbonnementUpdate(BaseModel):
    libelle: str | None = None
    montant: float | None = None
    jour_prelevement: int | None = None
    actif: bool | None = None


class AbonnementRead(AbonnementBase):
    id: int

    model_config = {"from_attributes": True}
