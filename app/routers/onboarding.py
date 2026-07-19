from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.compte import Compte

router = APIRouter(tags=["Onboarding"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/onboarding", summary="Assistant de configuration initiale")
def page_onboarding(request: Request, db: Session = Depends(get_db)):
    if db.query(Compte).count() > 0:
        return RedirectResponse("/")
    return templates.TemplateResponse("onboarding.html", {"request": request})
