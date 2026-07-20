from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from app.database import get_db
from app.auth import utilisateur_connecte, require_admin, IDENTIFIANT_ADMIN
from app.models.utilisateur import Utilisateur
from app.models.compte import Compte
from app.models.epargne import ObjectifEpargne
from app.models.placement import Placement
from app.services.utilisateurs import supprimer_utilisateur_et_donnees

router = APIRouter(tags=["Administration"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin", summary="Page d'administration des utilisateurs")
def page_admin(request: Request, db: Session = Depends(get_db)):
    user = utilisateur_connecte(request, db)
    if not user:
        return RedirectResponse("/login")
    if user.identifiant != IDENTIFIANT_ADMIN:
        return RedirectResponse("/")

    utilisateurs = db.query(Utilisateur).order_by(Utilisateur.date_creation).all()
    for u in utilisateurs:
        u.nb_comptes = db.query(Compte).filter(Compte.id_utilisateur == u.id).count()

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "utilisateurs": utilisateurs,
        "identifiant_admin": IDENTIFIANT_ADMIN,
    })


@router.post("/api/v1/admin/utilisateurs", status_code=201, summary="Créer un utilisateur")
def creer_utilisateur(
    identifiant: str = Form(...),
    mot_de_passe: str = Form(...),
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_admin),
):
    identifiant = identifiant.strip()
    if not identifiant:
        raise HTTPException(status_code=400, detail="Identifiant vide.")
    if db.query(Utilisateur).filter_by(identifiant=identifiant).first():
        raise HTTPException(status_code=400, detail=f"Un utilisateur '{identifiant}' existe déjà.")
    if len(mot_de_passe) < 4:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 4 caractères.")

    utilisateur = Utilisateur(identifiant=identifiant, mot_de_passe_hash=bcrypt.hash(mot_de_passe))
    db.add(utilisateur)
    db.commit()
    return {"id": utilisateur.id, "identifiant": utilisateur.identifiant}


@router.put("/api/v1/admin/utilisateurs/{utilisateur_id}/mot-de-passe", summary="Réinitialiser le mot de passe")
def reinitialiser_mot_de_passe(
    utilisateur_id: int,
    mot_de_passe: str = Form(...),
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_admin),
):
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if len(mot_de_passe) < 4:
        raise HTTPException(status_code=400, detail="Le mot de passe doit contenir au moins 4 caractères.")

    utilisateur.mot_de_passe_hash = bcrypt.hash(mot_de_passe)
    db.commit()
    return {"ok": True}


@router.put("/api/v1/admin/utilisateurs/{utilisateur_id}/identifiant", summary="Renommer un utilisateur")
def renommer_utilisateur(
    utilisateur_id: int,
    identifiant: str = Form(...),
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_admin),
):
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if utilisateur.identifiant == IDENTIFIANT_ADMIN:
        raise HTTPException(status_code=400, detail="Impossible de renommer le compte administrateur.")

    identifiant = identifiant.strip()
    if not identifiant:
        raise HTTPException(status_code=400, detail="Identifiant vide.")
    if identifiant == IDENTIFIANT_ADMIN:
        raise HTTPException(status_code=400, detail="Cet identifiant est réservé.")
    if db.query(Utilisateur).filter(Utilisateur.identifiant == identifiant, Utilisateur.id != utilisateur_id).first():
        raise HTTPException(status_code=400, detail=f"Un utilisateur '{identifiant}' existe déjà.")

    utilisateur.identifiant = identifiant
    db.commit()
    return {"id": utilisateur.id, "identifiant": utilisateur.identifiant}


@router.get("/api/v1/admin/utilisateurs/{utilisateur_id}/resume", summary="Résumé des données avant suppression")
def resume_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_admin),
):
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    return {
        "identifiant": utilisateur.identifiant,
        "nb_comptes": db.query(Compte).filter(Compte.id_utilisateur == utilisateur.id).count(),
        "nb_objectifs": db.query(ObjectifEpargne).filter(ObjectifEpargne.id_utilisateur == utilisateur.id).count(),
        "nb_placements": db.query(Placement).filter(Placement.id_utilisateur == utilisateur.id).count(),
    }


@router.delete("/api/v1/admin/utilisateurs/{utilisateur_id}", status_code=204, summary="Supprimer un utilisateur")
def supprimer_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db),
    admin: Utilisateur = Depends(require_admin),
):
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    if utilisateur.identifiant == IDENTIFIANT_ADMIN:
        raise HTTPException(status_code=400, detail="Impossible de supprimer le compte administrateur.")

    supprimer_utilisateur_et_donnees(db, utilisateur)
    db.commit()
