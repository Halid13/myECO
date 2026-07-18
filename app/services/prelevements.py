"""Service de gestion automatique des prélèvements d'abonnements."""
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.abonnement import Abonnement
from app.models.compte import Compte
from app.models.mouvement import Mouvement, TypeMouvement
import logging

logger = logging.getLogger(__name__)


def executer_prelevements():
    """
    Exécute automatiquement les prélèvements des abonnements arrivant à échéance.
    Cette fonction est appelée quotidiennement par le scheduler.
    """
    db = SessionLocal()
    today = date.today()
    
    try:
        # Récupérer tous les abonnements actifs
        abonnements = db.query(Abonnement).filter(Abonnement.actif == True).all()
        
        prelevements_executes = []
        erreurs = []
        
        for abo in abonnements:
            try:
                # Vérifier si le prélèvement est aujourd'hui
                if abo.jour_prelevement != today.day:
                    continue
                
                # Vérifier que le compte existe
                compte = db.get(Compte, abo.id_compte)
                if not compte:
                    erreurs.append(f"Abonnement {abo.id} ({abo.libelle}): Compte introuvable")
                    continue
                
                # Créer le mouvement de prélèvement
                mouvement = Mouvement(
                    id_compte=abo.id_compte,
                    type=TypeMouvement.sortie,
                    montant=abo.montant,
                    categorie=abo.categorie or "Abonnement",
                    description=f"Prélèvement automatique: {abo.libelle}",
                    date_mouvement=datetime.now(timezone.utc)
                )
                
                # Mettre à jour le solde du compte
                compte.solde -= abo.montant
                compte.date_maj = datetime.now(timezone.utc)
                
                # Enregistrer les changements
                db.add(mouvement)
                db.commit()
                db.refresh(mouvement)
                
                prelevements_executes.append({
                    "abonnement_id": abo.id,
                    "libelle": abo.libelle,
                    "montant": abo.montant,
                    "compte": compte.nom_banque,
                    "nouveau_solde": compte.solde,
                    "mouvement_id": mouvement.id
                })
                
                logger.info(
                    f"✓ Prélèvement exécuté: {abo.libelle} ({abo.montant}€) sur {compte.nom_banque}"
                )
                
            except Exception as e:
                db.rollback()
                erreurs.append(f"Abonnement {abo.id} ({abo.libelle}): {str(e)}")
                logger.error(f"✗ Erreur prélèvement {abo.id}: {str(e)}")
        
        db.close()
        
        # Log du résumé
        logger.info(
            f"[Scheduler] Prélèvements du {today.strftime('%d/%m/%Y')}: "
            f"{len(prelevements_executes)} réussis, {len(erreurs)} erreurs"
        )
        
        return {
            "date": today.isoformat(),
            "prelevements_executes": prelevements_executes,
            "erreurs": erreurs,
            "total": len(prelevements_executes)
        }
        
    except Exception as e:
        db.close()
        logger.error(f"[Scheduler] Erreur générale prélèvements: {str(e)}")
        return {
            "date": today.isoformat(),
            "prelevements_executes": [],
            "erreurs": [str(e)],
            "total": 0
        }


def obtenir_prochains_prelevements(nb_jours: int = 30) -> dict:
    """
    Retourne les prochains prélèvements à venir dans les N prochains jours.
    Utile pour afficher une prévision.
    """
    db = SessionLocal()
    today = date.today()
    
    try:
        abonnements = db.query(Abonnement).filter(Abonnement.actif == True).all()
        prochains = []
        
        for abo in abonnements:
            # Calculer les jours jusqu'au prochain prélèvement
            if abo.jour_prelevement >= today.day:
                jours_restants = abo.jour_prelevement - today.day
            else:
                # Le prélèvement est le mois prochain
                from calendar import monthrange
                jours_dans_mois = monthrange(today.year, today.month)[1]
                jours_restants = (jours_dans_mois - today.day) + abo.jour_prelevement
            
            if jours_restants <= nb_jours:
                prochains.append({
                    "abonnement_id": abo.id,
                    "libelle": abo.libelle,
                    "montant": abo.montant,
                    "compte": abo.compte.nom_banque if abo.compte else "N/A",
                    "jour_prelevement": abo.jour_prelevement,
                    "jours_restants": jours_restants,
                    "date_prelevement": f"{abo.jour_prelevement:02d}/{(today.month if abo.jour_prelevement > today.day else today.month + 1):02d}"
                })
        
        db.close()
        return sorted(prochains, key=lambda x: x["jours_restants"])
        
    except Exception as e:
        db.close()
        logger.error(f"Erreur obtention prochains prélèvements: {str(e)}")
        return []
