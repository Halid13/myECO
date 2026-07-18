from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.assistant import generer_alertes

router = APIRouter(prefix="/assistant", tags=["Assistant"])


@router.get("/api/v1/assistant/alerts", summary="Récupérer les alertes et conseils")
def get_alertes(db: Session = Depends(get_db)):
    alertes = generer_alertes(db)
    return {"alertes": alertes}
