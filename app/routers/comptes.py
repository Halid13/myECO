from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/comptes", tags=["Comptes"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", summary="Page Mouvements & Comptes")
def page_comptes(request: Request, db: Session = Depends(get_db)):
    # TODO : charger les comptes et mouvements
    return templates.TemplateResponse("mouvements.html", {"request": request})


@router.post("/api/v1/mouvements", summary="Enregistrer un mouvement")
def creer_mouvement(db: Session = Depends(get_db)):
    # TODO
    pass


@router.put("/api/v1/comptes/solde", summary="Ajuster le solde d'un compte")
def ajuster_solde(db: Session = Depends(get_db)):
    # TODO
    pass
