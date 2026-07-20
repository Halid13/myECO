"""Gestion des comptes utilisateurs (création, suppression en cascade) — partagé entre
les scripts CLI (app/scripts/) et la page d'administration (/admin)."""
from sqlalchemy.orm import Session
from app.models.utilisateur import Utilisateur
from app.models.compte import Compte
from app.models.mouvement import Mouvement
from app.models.abonnement import Abonnement
from app.models.epargne import ObjectifEpargne, HistoriqueEpargne
from app.models.placement import Placement, HistoriqueInvestissement
from app.models.assistant import Recommandation


def supprimer_utilisateur_et_donnees(db: Session, utilisateur: Utilisateur) -> None:
    """Supprime un utilisateur et toutes ses données liées (comptes, mouvements,
    abonnements, épargne, placements, recommandations). Ne fait pas le commit final."""
    comptes_ids = [c.id for c in db.query(Compte.id).filter(Compte.id_utilisateur == utilisateur.id)]
    objectifs_ids = [o.id for o in db.query(ObjectifEpargne.id).filter(ObjectifEpargne.id_utilisateur == utilisateur.id)]
    placements_ids = [p.id for p in db.query(Placement.id).filter(Placement.id_utilisateur == utilisateur.id)]

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
