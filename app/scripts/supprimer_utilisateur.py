"""Supprime un utilisateur et TOUTES ses données (comptes, mouvements, abonnements,
épargne, placements, recommandations) — action irréversible.

Usage :
    python -m app.scripts.supprimer_utilisateur
"""
from app.database import SessionLocal, init_db
from app.models.utilisateur import Utilisateur
from app.models.compte import Compte
from app.models.mouvement import Mouvement
from app.models.abonnement import Abonnement
from app.models.epargne import ObjectifEpargne, HistoriqueEpargne
from app.models.placement import Placement, HistoriqueInvestissement
from app.models.assistant import Recommandation


def main():
    init_db()
    db = SessionLocal()
    try:
        identifiant = input("Identifiant de l'utilisateur à supprimer : ").strip()
        utilisateur = db.query(Utilisateur).filter_by(identifiant=identifiant).first()
        if not utilisateur:
            print(f"Aucun utilisateur '{identifiant}' trouvé.")
            return

        comptes_ids = [c.id for c in db.query(Compte.id).filter(Compte.id_utilisateur == utilisateur.id)]
        objectifs_ids = [o.id for o in db.query(ObjectifEpargne.id).filter(ObjectifEpargne.id_utilisateur == utilisateur.id)]
        placements_ids = [p.id for p in db.query(Placement.id).filter(Placement.id_utilisateur == utilisateur.id)]

        print(f"\nCeci va supprimer définitivement l'utilisateur '{identifiant}' (id={utilisateur.id}) et :")
        print(f"  - {len(comptes_ids)} compte(s) bancaire(s), avec leurs mouvements et abonnements liés")
        print(f"  - {len(objectifs_ids)} objectif(s) d'épargne, avec leur historique")
        print(f"  - {len(placements_ids)} placement(s), avec leur historique")
        print("Cette action est irréversible.")
        confirmation = input(f"\nTaper l'identifiant '{identifiant}' pour confirmer : ").strip()
        if confirmation != identifiant:
            print("Confirmation incorrecte, abandon.")
            return

        if comptes_ids:
            db.query(Mouvement).filter(Mouvement.id_compte.in_(comptes_ids)).delete(synchronize_session=False)
            db.query(Abonnement).filter(Abonnement.id_compte.in_(comptes_ids)).delete(synchronize_session=False)
        if objectifs_ids:
            db.query(HistoriqueEpargne).filter(HistoriqueEpargne.id_objectif.in_(objectifs_ids)).delete(synchronize_session=False)
        if placements_ids:
            db.query(HistoriqueInvestissement).filter(HistoriqueInvestissement.id_placement.in_(placements_ids)).delete(synchronize_session=False)

        db.query(Compte).filter(Compte.id_utilisateur == utilisateur.id).delete(synchronize_session=False)
        db.query(ObjectifEpargne).filter(ObjectifEpargne.id_utilisateur == utilisateur.id).delete(synchronize_session=False)
        db.query(Placement).filter(Placement.id_utilisateur == utilisateur.id).delete(synchronize_session=False)
        db.query(Recommandation).filter(Recommandation.id_utilisateur == utilisateur.id).delete(synchronize_session=False)
        db.delete(utilisateur)
        db.commit()

        print(f"\nUtilisateur '{identifiant}' et toutes ses données ont été supprimés.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
