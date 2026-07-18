"""Moteur de règles de l'Assistant Intelligent (Module 6 — Conseils & Analyse).

Le moteur se ré-évalue à la lecture (à chaque appel), pas sur événement de mutation —
cohérent avec le reste de l'app ("aucun cache, données toujours fraîches"). Les résultats
sont persistés et dédupliqués par (type_regle, cle_contexte) : une situation qui perdure ne
crée pas de doublons, et une situation résolue passe automatiquement au statut "resolu" au
cycle suivant.
"""
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.models.compte import Compte
from app.models.abonnement import Abonnement
from app.models.epargne import ObjectifEpargne
from app.models.placement import Placement
from app.models.mouvement import TypeMouvement
from app.models.assistant import Recommandation
from app.services.finances import calculer_revenus_mois, calculer_charges_mensuelles, calculer_mouvements_mois
from app.services.epargne import effort_epargne_mois
from app.services.regles_assistant import REGLES

STATUTS_ACTIFS = ["nouveau", "lu"]
PRIORITE_NIVEAU = {"warning": 0, "info": 1, "success": 2}


def construire_contexte(db: Session, today: date | None = None) -> dict:
    """Un seul passage de requêtes, partagé par toutes les règles."""
    today = today or date.today()
    comptes = db.query(Compte).all()
    abonnements = db.query(Abonnement).filter(Abonnement.actif == True).all()
    objectifs = db.query(ObjectifEpargne).filter(ObjectifEpargne.actif == True).all()
    placements = db.query(Placement).all()

    return {
        "today": today,
        "comptes": comptes,
        "abonnements": abonnements,
        "objectifs": objectifs,
        "placements": placements,
        "revenus_mois": calculer_revenus_mois(db, today),
        "charges_mensuelles": calculer_charges_mensuelles(abonnements),
        "effort_epargne": effort_epargne_mois(db, today),
        "depenses_mois": calculer_mouvements_mois(db, TypeMouvement.sortie, today),
    }


def executer_moteur(db: Session, today: date | None = None) -> list[Recommandation]:
    """Exécute toutes les règles, réconcilie avec les recommandations déjà en base
    (dédup / auto-résolution), et retourne les recommandations actives."""
    today = today or date.today()
    ctx = construire_contexte(db, today)

    candidats = []
    for regle in REGLES:
        candidats.extend(regle(ctx))

    maintenant = datetime.now(timezone.utc)
    cles_actives = set()

    for candidat in candidats:
        cle = (candidat["type_regle"], candidat["cle_contexte"])
        cles_actives.add(cle)

        existante = (
            db.query(Recommandation)
            .filter(
                Recommandation.type_regle == candidat["type_regle"],
                Recommandation.cle_contexte == candidat["cle_contexte"],
                Recommandation.statut.in_(STATUTS_ACTIFS),
            )
            .first()
        )
        if existante:
            existante.titre = candidat["titre"]
            existante.message = candidat["message"]
            existante.niveau = candidat["niveau"]
            existante.icone = candidat.get("icone")
            existante.lien = candidat.get("lien")
            existante.date_derniere_detection = maintenant
        else:
            db.add(Recommandation(
                type_regle=candidat["type_regle"],
                cle_contexte=candidat["cle_contexte"],
                niveau=candidat["niveau"],
                icone=candidat.get("icone"),
                titre=candidat["titre"],
                message=candidat["message"],
                lien=candidat.get("lien"),
                statut="nouveau",
                date_creation=maintenant,
                date_derniere_detection=maintenant,
            ))

    # Auto-résolution : toute recommandation active dont la règle ne se déclenche plus
    actives_en_base = (
        db.query(Recommandation)
        .filter(Recommandation.statut.in_(STATUTS_ACTIFS))
        .all()
    )
    for reco in actives_en_base:
        if (reco.type_regle, reco.cle_contexte) not in cles_actives:
            reco.statut = "resolu"
            reco.date_resolution = maintenant

    db.commit()

    actives = (
        db.query(Recommandation)
        .filter(Recommandation.statut.in_(STATUTS_ACTIFS))
        .order_by(Recommandation.date_creation.desc())
        .all()
    )
    actives.sort(key=lambda r: PRIORITE_NIVEAU.get(r.niveau, 1))
    return actives


def obtenir_historique(db: Session, limite: int = 50) -> list[Recommandation]:
    """Toutes les recommandations (actives, ignorées, résolues), les plus récentes d'abord."""
    return (
        db.query(Recommandation)
        .order_by(Recommandation.date_creation.desc())
        .limit(limite)
        .all()
    )
