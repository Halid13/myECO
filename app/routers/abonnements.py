from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/abonnements", tags=["Abonnements"])


@router.post("/api/v1/abonnements", summary="Créer un abonnement")
def creer_abonnement(db: Session = Depends(get_db)):
    # TODO
    pass


@router.put("/api/v1/abonnements/{id}", summary="Modifier un abonnement")
def modifier_abonnement(id: int, db: Session = Depends(get_db)):
    # TODO
    pass


@router.delete("/api/v1/abonnements/{id}", summary="Supprimer un abonnement")
def supprimer_abonnement(id: int, db: Session = Depends(get_db)):
    # TODO
    pass
