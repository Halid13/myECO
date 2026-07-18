from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.epargne import ObjectifEpargne, HistoriqueEpargne
from app.schemas.epargne import ObjectifEpargneCreate, ObjectifEpargneRead, MouvementEpargne

router = APIRouter(tags=["Épargne"])


@router.get("/api/v1/epargne", response_model=list[ObjectifEpargneRead], summary="Lister les objectifs d'épargne")
def lister_objectifs(db: Session = Depends(get_db)):
    objectifs = db.query(ObjectifEpargne).filter(ObjectifEpargne.actif == True).all()
    result = []
    for obj in objectifs:
        data = ObjectifEpargneRead.model_validate(obj)
        data.progression_pct = round((obj.montant_actuel / obj.montant_cible) * 100, 1) if obj.montant_cible else 0.0
        result.append(data)
    return result


@router.post("/api/v1/epargne", response_model=ObjectifEpargneRead, status_code=201, summary="Créer un objectif d'épargne")
def creer_objectif(payload: ObjectifEpargneCreate, db: Session = Depends(get_db)):
    objectif = ObjectifEpargne(**payload.model_dump())
    db.add(objectif)
    db.commit()
    db.refresh(objectif)
    return objectif


@router.put("/api/v1/epargne/{objectif_id}/update", response_model=ObjectifEpargneRead, summary="Alimenter ou retirer d'une poche")
def update_epargne(objectif_id: int, payload: MouvementEpargne, db: Session = Depends(get_db)):
    objectif = db.get(ObjectifEpargne, objectif_id)
    if not objectif:
        raise HTTPException(status_code=404, detail="Objectif introuvable")
    objectif.montant_actuel = round(objectif.montant_actuel + payload.montant, 2)
    if objectif.montant_actuel < 0:
        raise HTTPException(status_code=400, detail="Le solde de la poche ne peut pas être négatif")
    historique = HistoriqueEpargne(id_objectif=objectif_id, montant=payload.montant)
    db.add(historique)
    db.commit()
    db.refresh(objectif)
    result = ObjectifEpargneRead.model_validate(objectif)
    result.progression_pct = round((objectif.montant_actuel / objectif.montant_cible) * 100, 1) if objectif.montant_cible else 0.0
    return result


@router.delete("/api/v1/epargne/{objectif_id}", status_code=204, summary="Clôturer un objectif d'épargne")
def cloturer_objectif(objectif_id: int, db: Session = Depends(get_db)):
    objectif = db.get(ObjectifEpargne, objectif_id)
    if not objectif:
        raise HTTPException(status_code=404, detail="Objectif introuvable")
    objectif.actif = False
    db.commit()
