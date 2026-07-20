from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.utilisateur import Utilisateur
from app.auth import verifier_mot_de_passe

router = APIRouter(tags=["Authentification"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", summary="Page de connexion")
def page_login(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/")
    return templates.TemplateResponse("login.html", {"request": request, "erreur": None})


@router.post("/login", summary="Traiter la connexion")
def traiter_login(
    request: Request,
    identifiant: str = Form(...),
    mot_de_passe: str = Form(...),
    db: Session = Depends(get_db),
):
    utilisateur = db.query(Utilisateur).filter_by(identifiant=identifiant).first()
    if not utilisateur or not verifier_mot_de_passe(mot_de_passe, utilisateur.mot_de_passe_hash):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "erreur": "Identifiant ou mot de passe incorrect.",
        }, status_code=401)

    request.session["user_id"] = utilisateur.id
    return RedirectResponse("/?connexion=1", status_code=303)


@router.get("/logout", summary="Déconnexion")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")
