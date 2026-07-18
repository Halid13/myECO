from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/investissements", tags=["Investissements"])


@router.put("/api/v1/investissements/value", summary="Mettre à jour la valeur d'un placement")
def update_valeur(db: Session = Depends(get_db)):
    # TODO
    pass
