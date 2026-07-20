from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import utilisateur_connecte
from app.models.compte import Compte

router = APIRouter(tags=["Onboarding"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/onboarding", summary="Assistant de configuration initiale")
def page_onboarding(request: Request, db: Session = Depends(get_db)):
    user = utilisateur_connecte(request, db)
    if not user:
        return RedirectResponse("/login")
    if db.query(Compte).filter(Compte.id_utilisateur == user.id).count() > 0:
        return RedirectResponse("/")
    return templates.TemplateResponse("onboarding.html", {"request": request})
