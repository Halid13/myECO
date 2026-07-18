from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.abonnement import Abonnement
from app.schemas.abonnement import AbonnementCreate, AbonnementUpdate, AbonnementRead

router = APIRouter(tags=["Abonnements"])


@router.get("/api/v1/abonnements", response_model=list[AbonnementRead], summary="Lister les abonnements")
def lister_abonnements(actif: bool | None = None, db: Session = Depends(get_db)):
    q = db.query(Abonnement)
    if actif is not None:
        q = q.filter(Abonnement.actif == actif)
    return q.order_by(Abonnement.jour_prelevement).all()


@router.post("/api/v1/abonnements", response_model=AbonnementRead, status_code=201, summary="Créer un abonnement")
def creer_abonnement(payload: AbonnementCreate, db: Session = Depends(get_db)):
    abonnement = Abonnement(**payload.model_dump())
    db.add(abonnement)
    db.commit()
    db.refresh(abonnement)
    return abonnement


@router.put("/api/v1/abonnements/{abonnement_id}", response_model=AbonnementRead, summary="Modifier un abonnement")
def modifier_abonnement(abonnement_id: int, payload: AbonnementUpdate, db: Session = Depends(get_db)):
    abonnement = db.get(Abonnement, abonnement_id)
    if not abonnement:
        raise HTTPException(status_code=404, detail="Abonnement introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(abonnement, field, value)
    db.commit()
    db.refresh(abonnement)
    return abonnement


@router.delete("/api/v1/abonnements/{abonnement_id}", status_code=204, summary="Supprimer un abonnement")
def supprimer_abonnement(abonnement_id: int, db: Session = Depends(get_db)):
    abonnement = db.get(Abonnement, abonnement_id)
    if not abonnement:
        raise HTTPException(status_code=404, detail="Abonnement introuvable")
    db.delete(abonnement)
    db.commit()
