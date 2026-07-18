from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.placement import Placement
from app.schemas.placement import PlacementCreate, PlacementUpdateValeur, PlacementRead

router = APIRouter(tags=["Investissements"])


@router.get("/api/v1/investissements", response_model=list[PlacementRead], summary="Lister les placements")
def lister_placements(db: Session = Depends(get_db)):
    return db.query(Placement).all()


@router.post("/api/v1/investissements", response_model=PlacementRead, status_code=201, summary="Déclarer un placement")
def creer_placement(payload: PlacementCreate, db: Session = Depends(get_db)):
    placement = Placement(**payload.model_dump())
    db.add(placement)
    db.commit()
    db.refresh(placement)
    return placement


@router.put("/api/v1/investissements/{placement_id}/value", response_model=PlacementRead, summary="Mettre à jour la valeur liquidative")
def update_valeur(placement_id: int, payload: PlacementUpdateValeur, db: Session = Depends(get_db)):
    placement = db.get(Placement, placement_id)
    if not placement:
        raise HTTPException(status_code=404, detail="Placement introuvable")
    placement.valeur_actuelle = payload.valeur_actuelle
    placement.date_valorisation = datetime.now(timezone.utc)
    db.commit()
    db.refresh(placement)
    return placement


@router.delete("/api/v1/investissements/{placement_id}", status_code=204, summary="Supprimer un placement")
def supprimer_placement(placement_id: int, db: Session = Depends(get_db)):
    placement = db.get(Placement, placement_id)
    if not placement:
        raise HTTPException(status_code=404, detail="Placement introuvable")
    db.delete(placement)
    db.commit()
