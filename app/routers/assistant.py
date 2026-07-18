from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.assistant import Recommandation
from app.services.assistant import executer_moteur, obtenir_historique

router = APIRouter(tags=["Assistant"])

STATUTS_MODIFIABLES = ["lu", "ignore"]


def _serialiser(r: Recommandation) -> dict:
    return {
        "id": r.id,
        "type_regle": r.type_regle,
        "niveau": r.niveau,
        "icone": r.icone,
        "titre": r.titre,
        "message": r.message,
        "lien": r.lien,
        "statut": r.statut,
        "date_creation": r.date_creation,
        "date_derniere_detection": r.date_derniere_detection,
        "date_resolution": r.date_resolution,
    }


@router.get("/api/v1/assistant/alerts", summary="Récupérer les recommandations actives")
def get_alertes(db: Session = Depends(get_db)):
    recommandations = executer_moteur(db, date.today())
    return {"alertes": [_serialiser(r) for r in recommandations]}


@router.get("/api/v1/assistant/historique", summary="Historique des recommandations")
def get_historique(db: Session = Depends(get_db)):
    return {"historique": [_serialiser(r) for r in obtenir_historique(db)]}


@router.put("/api/v1/assistant/{recommandation_id}/statut", summary="Marquer une recommandation comme lue/ignorée")
def modifier_statut(recommandation_id: int, statut: str = Form(...), db: Session = Depends(get_db)):
    if statut not in STATUTS_MODIFIABLES:
        raise HTTPException(status_code=400, detail=f"Statut invalide. Valeurs possibles : {STATUTS_MODIFIABLES}")
    recommandation = db.get(Recommandation, recommandation_id)
    if not recommandation:
        raise HTTPException(status_code=404, detail="Recommandation introuvable")
    recommandation.statut = statut
    db.commit()
    db.refresh(recommandation)
    return _serialiser(recommandation)
