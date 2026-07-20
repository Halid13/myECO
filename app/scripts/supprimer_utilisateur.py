"""Supprime un utilisateur et TOUTES ses données (comptes, mouvements, abonnements,
épargne, placements, recommandations) — action irréversible.

Usage :
    python -m app.scripts.supprimer_utilisateur
"""
from app.database import SessionLocal, init_db
from app.models.utilisateur import Utilisateur
from app.models.compte import Compte
from app.models.epargne import ObjectifEpargne
from app.models.placement import Placement
from app.services.utilisateurs import supprimer_utilisateur_et_donnees


def main():
    init_db()
    db = SessionLocal()
    try:
        identifiant = input("Identifiant de l'utilisateur à supprimer : ").strip()
        utilisateur = db.query(Utilisateur).filter_by(identifiant=identifiant).first()
        if not utilisateur:
            print(f"Aucun utilisateur '{identifiant}' trouvé.")
            return

        nb_comptes = db.query(Compte).filter(Compte.id_utilisateur == utilisateur.id).count()
        nb_objectifs = db.query(ObjectifEpargne).filter(ObjectifEpargne.id_utilisateur == utilisateur.id).count()
        nb_placements = db.query(Placement).filter(Placement.id_utilisateur == utilisateur.id).count()

        print(f"\nCeci va supprimer définitivement l'utilisateur '{identifiant}' (id={utilisateur.id}) et :")
        print(f"  - {nb_comptes} compte(s) bancaire(s), avec leurs mouvements et abonnements liés")
        print(f"  - {nb_objectifs} objectif(s) d'épargne, avec leur historique")
        print(f"  - {nb_placements} placement(s), avec leur historique")
        print("Cette action est irréversible.")
        confirmation = input(f"\nTaper l'identifiant '{identifiant}' pour confirmer : ").strip()
        if confirmation != identifiant:
            print("Confirmation incorrecte, abandon.")
            return

        supprimer_utilisateur_et_donnees(db, utilisateur)
        db.commit()

        print(f"\nUtilisateur '{identifiant}' et toutes ses données ont été supprimés.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
