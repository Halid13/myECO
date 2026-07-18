from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", summary="Page principale — Dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    # TODO : agrégation des données (comptes, abonnements, épargne, placements)
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/api/v1/dashboard", summary="Données consolidées du dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    # TODO : retourner les données JSON pour les mises à jour HTMX
    return {"status": "ok"}
