"""Crée un nouvel utilisateur (compte de connexion) sans passer par une page d'inscription
publique — volontairement un script à lancer à la main sur le serveur.

Usage :
    python -m app.scripts.creer_utilisateur
"""
import getpass
from passlib.hash import bcrypt
from app.database import SessionLocal, init_db
from app.models.utilisateur import Utilisateur


def main():
    init_db()
    db = SessionLocal()
    try:
        identifiant = input("Identifiant du nouvel utilisateur : ").strip()
        if not identifiant:
            print("Identifiant vide, abandon.")
            return
        if db.query(Utilisateur).filter_by(identifiant=identifiant).first():
            print(f"Un utilisateur '{identifiant}' existe déjà.")
            return

        mot_de_passe = getpass.getpass("Mot de passe : ")
        confirmation = getpass.getpass("Confirmer le mot de passe : ")
        if mot_de_passe != confirmation:
            print("Les mots de passe ne correspondent pas, abandon.")
            return

        utilisateur = Utilisateur(identifiant=identifiant, mot_de_passe_hash=bcrypt.hash(mot_de_passe))
        db.add(utilisateur)
        db.commit()
        db.refresh(utilisateur)
        print(f"Utilisateur '{identifiant}' créé (id={utilisateur.id}).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
