from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from app.database import get_db
from app.models.utilisateur import Utilisateur

# Identifiant considéré comme administrateur — pas de colonne "rôle" en base,
# volontairement simple pour un usage familial (voir CLAUDE.md).
IDENTIFIANT_ADMIN = "admin"


def verifier_mot_de_passe(mot_de_passe: str, hash_stocke: str) -> bool:
    return bcrypt.verify(mot_de_passe, hash_stocke)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> Utilisateur:
    """Pour les routes API (/api/v1/...) : renvoie 401 si non connecté."""
    user_id = request.session.get("user_id")
    user = db.get(Utilisateur, user_id) if user_id else None
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    return user


def utilisateur_connecte(request: Request, db: Session) -> Utilisateur | None:
    """Pour les routes de page HTML : renvoie None si non connecté (la route fait
    alors elle-même `return RedirectResponse('/login')`)."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.get(Utilisateur, user_id)


def require_admin(user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
    """Pour les routes API d'administration : 403 si l'utilisateur connecté n'est pas admin."""
    if user.identifiant != IDENTIFIANT_ADMIN:
        raise HTTPException(status_code=403, detail="Réservé à l'administrateur")
    return user
