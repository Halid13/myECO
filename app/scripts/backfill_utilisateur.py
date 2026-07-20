"""À exécuter une seule fois après la mise à jour vers le multi-utilisateur :
crée un utilisateur admin par défaut et rattache toutes les données existantes à ce compte.

Usage :
    python -m app.scripts.backfill_utilisateur
"""
import getpass
from passlib.hash import bcrypt
from app.database import SessionLocal, init_db
from app.models.utilisateur import Utilisateur
from app.models.compte import Compte
from app.models.placement import Placement
from app.models.assistant import Recommandation
from app.models.epargne import ObjectifEpargne


def main():
    init_db()
    db = SessionLocal()
    try:
        admin = db.query(Utilisateur).filter_by(identifiant="admin").first()
        if not admin:
            mot_de_passe = getpass.getpass("Mot de passe pour le compte admin : ")
            admin = Utilisateur(identifiant="admin", mot_de_passe_hash=bcrypt.hash(mot_de_passe))
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Utilisateur 'admin' créé (id={admin.id}).")
        else:
            print(f"Utilisateur 'admin' déjà existant (id={admin.id}).")

        for modele in (Compte, Placement, Recommandation, ObjectifEpargne):
            nb = db.query(modele).filter(modele.id_utilisateur.is_(None)).update({"id_utilisateur": admin.id})
            print(f"{modele.__tablename__} : {nb} ligne(s) rattachée(s) à 'admin'.")

        db.commit()
        print("Backfill terminé.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
