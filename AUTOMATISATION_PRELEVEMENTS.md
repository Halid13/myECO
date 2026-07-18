# Système de Prélèvements Automatiques - Documentation

## Vue d'ensemble

Le système gère automatiquement les prélèvements des abonnements à leur date d'échéance. Chaque jour à minuit, l'application vérifie les abonnements arrivant à terme et exécute les débits correspondants.

## Architecture

### 1. **Scheduler (APScheduler)**
- **Fichier** : `app/main.py`
- **Exécution** : Quotidienne à 00:01 (minuit + 1 minute)
- **Fonction** : `executer_prelevements()`
- **Lifecycle** : Démarre au lancement de l'app, s'arrête à l'extinction

### 2. **Service de Prélèvements**
- **Fichier** : `app/services/prelevements.py`
- **Fonctions principales** :
  - `executer_prelevements()` : Exécute les prélèvements du jour
  - `obtenir_prochains_prelevements(nb_jours)` : Retourne les prélèvements à venir

### 3. **Endpoints API**
- `GET /api/v1/prelevements/prochains?jours=30` : Liste les prochains prélèvements
- `POST /api/v1/prelevements/executer-maintenant` : Force l'exécution (TEST uniquement)
- `GET /prelevements/` : Page de gestion des prélèvements

## Flux de Prélèvement

```
1. [00:01 Chaque jour] Scheduler déclenche executer_prelevements()
   ↓
2. Récupère tous les abonnements actifs
   ↓
3. Pour chaque abonnement où jour_prelevement = aujourd'hui :
   ├─ Vérifie que le compte existe
   ├─ Crée un Mouvement (type: Sortie)
   ├─ Déduit le montant du solde du compte
   └─ Enregistre en base de données
   ↓
4. Log du résumé (nombre de prélèvements réussis/erreurs)
   ↓
5. Dashboard et autres pages reflètent immédiatement les changements
```

## Structure des Données

### Mouvement généré automatiquement
```python
{
    "id_compte": <id du compte associé>,
    "type": "Sortie",
    "montant": <montant de l'abonnement>,
    "categorie": <categorie de l'abonnement>,
    "description": f"Prélèvement automatique: {libelle}",
    "date_mouvement": <datetime actuel>
}
```

### Prochains prélèvements retournés
```python
{
    "abonnement_id": <id>,
    "libelle": <nom de l'abo>,
    "montant": <montant>,
    "compte": <nom_banque>,
    "jour_prelevement": <1-31>,
    "jours_restants": <nombre de jours>,
    "date_prelevement": "05/07" (format JJ/MM)
}
```

## Pages et Interfaces

### Page Prélèvements (`/prelevements/`)
- **Section 1** : Prochains prélèvements (30 jours)
  - Affiche tous les abonnements à venir
  - Code couleur : rouge si aujourd'hui, orange si ≤3j, gris sinon
  - Trier par proximité

- **Section 2** : Historique du mois
  - Affiche tous les prélèvements exécutés ce mois
  - Récupère les mouvements avec `description` contenant "Prélèvement automatique"

- **Bouton "Déclencher maintenant"** : Force l'exécution (développement/test)

## Sécurité et Robustesse

✅ **Gestion des erreurs** :
- Try-catch autour de chaque prélèvement
- Rollback automatique en cas d'erreur
- Logging détaillé de chaque opération

✅ **Validation** :
- Vérifie que l'abonnement est actif
- Vérifie que le compte existe
- Vérifie les montants > 0

✅ **Synchronisation** :
- Les soldes sont mis à jour immédiatement
- Les mouvements sont enregistrés
- Le dashboard reflète les changements en temps réel

## Cas d'Usage et Exemples

### Exemple 1 : Prélèvement Netflix
```
Abonnement: Netflix
Montant: 15.99€
Compte: Revolut
Jour prélèvement: 5

→ Le 5 de chaque mois à 00:01 :
  - Détecte l'abonnement Netflix
  - Crée mouvement: Sortie -15.99€ sur Revolut
  - Met à jour solde Revolut: -15.99€
  - Enregistre: "Prélèvement automatique: Netflix"
```

### Exemple 2 : Erreur (compte supprimé)
```
→ Le prélèvement échoue
→ Raison enregistrée: "Compte introuvable"
→ L'abonnement ne change pas (toujours actif)
→ Pas de débit appliqué
→ Error loggé pour investigation
```

## Maintenance et Monitoring

### Logs
- Tous les prélèvements réussis/échoués sont loggés
- Format : `[Scheduler] Prélèvements du JJ/MM/YYYY: X réussis, Y erreurs`
- Localisation : stdout / fichier logs (selon configuration)

### Endpoint de test
```bash
# Forcer l'exécution maintenant (dev/test)
POST http://localhost:8000/api/v1/prelevements/executer-maintenant

Réponse :
{
    "date": "2026-07-18",
    "prelevements_executes": [
        {"abonnement_id": 1, "libelle": "Netflix", "montant": 15.99, ...}
    ],
    "erreurs": [],
    "total": 1
}
```

## À Noter

⚠️ **Production** :
- Adapter l'horaire du scheduler (actuellement 00:01)
- Mettre en place un vrai système de logging (fichiers, monitoring)
- Supprimer ou sécuriser l'endpoint `/executer-maintenant`
- Ajouter des alertes/notifications à l'utilisateur

⚠️ **Limitations actuelles** :
- APScheduler s'arrête quand l'app s'arrête (ok pour dev, besoin de worker en prod)
- Pas de persévérance si l'app crash entre deux exécutions
- Pas de notification utilisateur (à ajouter)

## Configuration Future

Pour la production, envisager :
- Celery + Redis pour les tâches persistantes
- Webhook/notification d'alerte utilisateur
- Interface de reporting (tableau prélèvements vs budget)
- Reschedule automatique en cas d'erreur
- Archivage des mouvements automatiques
