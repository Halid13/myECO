from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/epargne", tags=["Épargne"])


@router.put("/api/v1/epargne/update", summary="Alimenter / retirer d'une poche d'épargne")
def update_epargne(db: Session = Depends(get_db)):
    # TODO
    pass
