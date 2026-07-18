# PROJECT_CONTEXT.md — FinanSmart

**Document de référence complète pour le développement de FinanSmart**

---

## 1. Présentation Générale du Projet

### Nom du Projet
**FinanSmart** — Plateforme de gestion financière personnelle premium

### Objectif Principal
Offrir une interface intuitive, élégante et performante permettant aux utilisateurs de :
- Gérer leurs comptes bancaires et soldes
- Suivre leurs mouvements financiers (entrées/sorties)
- Gérer automatiquement leurs abonnements récurrents
- Visualiser leur patrimoine (épargne, investissements)
- Obtenir une vue d'ensemble de leur situation financière

### Problème Résolu
Les utilisateurs n'ont pas de solution simple et élégante pour :
- Centraliser la gestion de plusieurs comptes bancaires
- Automatiser les prélèvements d'abonnements sans saisie manuelle
- Visualiser rapidement leur situation financière
- Prévoir les prochains prélèvements

### Public Cible
- Particuliers sensibles à l'UX/UI
- Utilisateurs cherchant une alternative minimaliste aux applications bancaires lourdes
- Personnes avec plusieurs comptes et abonnements

### Philosophie Générale
**Simplicité, élégance, efficacité** — Chaque feature doit :
- Résoudre un problème réel
- Être intuitive sans tutoriel
- Respecter le design minimaliste et premium
- Fonctionner sans ralentissements

### Fonctionnalités Principales
1. **Dashboard** — Vue d'ensemble financière en temps réel
2. **Gestion des Comptes** — Ajout, modification, suivi des soldes
3. **Historique des Mouvements** — Enregistrement et filtrage
4. **Gestion des Abonnements** — CRUD avec prélèvements automatiques
5. **Prélèvements Automatiques** — Exécution quotidienne sans intervention
6. **Gestion du Patrimoine** — Épargne, investissements, objectifs
7. **Mode Discrétion** — Masquage des montants sensibles

---

## 2. Vision Produit

### Ce que l'Application Cherche à Accomplir
FinanSmart vise à transformer la gestion financière personnelle en :
- **Automatisant** ce qui peut l'être (prélèvements, calculs)
- **Simplifiant** l'interface pour que 80% des actions prennent <5 clics
- **Visualisant** la situation financière sans jargon technique
- **Rassemblant** tous les comptes en un seul endroit

### Principes UX/UI
1. **Design SaaS Premium** — Interface moderne, épurée, professionnelle
2. **Mode Sombre par Défaut** — Respecte les yeux, moderne
3. **Minimalisme** — Pas d'éléments superflus
4. **Compacité** — Spacing réduit, permet de voir plus d'infos
5. **Monochromes Heroicons** — Icônes cohérentes et professionnelles
6. **Animations Discrètes** — Fade-in, slide-in sans excès
7. **Hiérarchie Visuelle Claire** — Titre → Sous-titre → Donnée
8. **Excellente Lisibilité** — Contraste fort, police adaptée

### Contraintes du Projet
1. **Serveur limité** — 8 GB RAM, 250 GB stockage
2. **Base de données légère** — SQLite uniquement
3. **Aucune synchronisation bancaire** — Saisie manuelle des mouvements
4. **Performance prioritaire** — Pas de dépendances lourdes
5. **Maintenance simplifiée** — Code maintenable et documenté

### Choix Fonctionnels Importants
- **SQLite au lieu de PostgreSQL** → Simplicité, pas de serveur externe
- **FastAPI au lieu de Django** → Légèreté, rapidité, moderne
- **APScheduler pour l'automatisation** → Intégré, simple à maintenir
- **Tailwind CDN au lieu de build** → Zéro compilation
- **HTMX pour dynamique** → Évite SPA lourd, reste serveur-side
- **Chart.js pour les graphiques** → Léger, performant
- **Pas d'authentification multi-users** → Mono-user, simplifie tout

---

## 3. Architecture Générale

### Diagramme Architecturel

```
┌─────────────────────────────────────────────────────────────┐
│                    NAVIGATEUR (Client)                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Jinja2 Templates + Tailwind + HTMX + Chart.js      │   │
│  │  (index.html, mouvements.html, abonnements.html...) │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬──────────────────────────────────────┘
                      │ HTTP/HTMX
                      ↓
┌─────────────────────────────────────────────────────────────┐
│              FASTAPI (Backend - app/main.py)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Routers:                                             │   │
│  │ • dashboard.py    → GET /                           │   │
│  │ • comptes.py      → GET/POST /api/v1/comptes        │   │
│  │ • mouvements      → GET/POST /api/v1/mouvements     │   │
│  │ • abonnements.py  → GET/POST /api/v1/abonnements    │   │
│  │ • epargne.py      → GET/POST /api/v1/objectifs      │   │
│  │ • investissements → GET/POST /api/v1/placements     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Services:                                            │   │
│  │ • prelevements.py  → Gestion des prélèvements       │   │
│  │ • assistant.py     → Génération d'alertes           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ APScheduler (Automatisation):                       │   │
│  │ • Exécution quotidienne à 00:01                     │   │
│  │ • Prélèvements automatiques des abonnements         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────┬──────────────────────────────────────┘
                      │ SQLAlchemy ORM
                      ↓
┌─────────────────────────────────────────────────────────────┐
│         SQLite Database (app/database.db)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Tables:                                              │   │
│  │ • compte          (id, nom_banque, solde...)        │   │
│  │ • mouvement       (id, id_compte, type, montant...) │   │
│  │ • abonnement      (id, libelle, montant, frequence) │   │
│  │ • objectif_epargne (id, nom, montant_cible...)     │   │
│  │ • placement       (id, nom, type, valeur...)        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Front-end
- **Templating** : Jinja2 (rendu serveur)
- **Styling** : Tailwind CSS (CDN)
- **Dynamique** : HTMX + JavaScript vanilla
- **Graphiques** : Chart.js
- **Icônes** : Heroicons (SVG monochromes via macros)

### Back-end
- **Framework** : FastAPI (Uvicorn)
- **ORM** : SQLAlchemy
- **Base de données** : SQLite
- **Automatisation** : APScheduler
- **Validation** : Pydantic

### Base de Données
- **Type** : SQLite (fichier unique `app/database.db`)
- **ORM** : SQLAlchemy
- **Migrations** : Aucune (crée les tables au démarrage)
- **Relations** : One-to-Many (Compte → Mouvements, Abonnements, etc.)

### API
- **Protocole** : REST + Templating Jinja2
- **Authentification** : Aucune (mono-user)
- **Format** : JSON pour les API, HTML pour les pages
- **Status codes** : Respecte les standards HTTP (201, 204, 404, etc.)

### Organisation des Dossiers

```
myECO/
├── app/
│   ├── main.py                    # Point d'entrée FastAPI + scheduler
│   ├── database.py                # Configuration SQLAlchemy
│   ├── models/                    # ORM models
│   │   ├── compte.py
│   │   ├── mouvement.py
│   │   ├── abonnement.py
│   │   ├── epargne.py
│   │   └── placement.py
│   ├── schemas/                   # Pydantic schemas (validation)
│   │   ├── compte.py
│   │   ├── mouvement.py
│   │   ├── abonnement.py
│   │   ├── epargne.py
│   │   └── placement.py
│   ├── routers/                   # Endpoints FastAPI
│   │   ├── dashboard.py
│   │   ├── comptes.py
│   │   ├── abonnements.py
│   │   ├── epargne.py
│   │   ├── investissements.py
│   │   └── assistant.py
│   ├── services/                  # Logique métier
│   │   ├── prelevements.py        # Gestion prélèvements
│   │   └── assistant.py           # Génération alertes
│   └── templates/                 # Templates Jinja2
│       ├── base.html              # Layout principal
│       ├── index.html             # Dashboard
│       ├── mouvements.html        # Comptes & Liquidités
│       ├── abonnements.html       # Charges Fixes
│       ├── patrimoine.html        # Patrimoine
│       ├── components.html        # Macros réutilisables
│       └── icons.html             # Macros Heroicons
├── static/
│   └── css/
│       └── custom.css             # Styles custom (animations, etc.)
├── requirements.txt               # Dépendances Python
└── README.md                      # Documentation projet
```

---

## 4. Stack Technique

| Couche | Technologie | Version | Raison |
|--------|-------------|---------|--------|
| **Serveur Web** | Uvicorn | 0.29.0 | Serveur ASGI ultra-léger pour FastAPI |
| **Framework Backend** | FastAPI | 0.111.0 | Moderne, rapide, auto-documentation, type-hint |
| **ORM** | SQLAlchemy | 2.0.30 | Standard Python, flexible, robuste |
| **Base Données** | SQLite | - | Fichier unique, zéro config, suffisant pour le projet |
| **Validation** | Pydantic | (built-in) | Validation automatique, conversion types |
| **Templating** | Jinja2 | 3.1.4 | Standard Python, puissante |
| **CSS** | Tailwind CSS | (CDN) | Utility-first, rapide, personnalisable |
| **Interactivité** | HTMX | 1.9.12 | Requêtes AJAX sans JS, intégré Jinja2 |
| **Graphiques** | Chart.js | 4.x | Léger, responsive, performant |
| **Icônes** | Heroicons | (SVG) | Monochromes, 24+ icônes, cohérent |
| **Upload Fichiers** | python-multipart | 0.0.9 | Support MIME/form-data |
| **Fichiers Async** | aiofiles | 23.2.1 | I/O async pour les uploads |
| **Scheduling** | APScheduler | 3.10.4 | Tâches planifiées (prélèvements) |
| **JS Runtime** | Vanilla JS | - | Zéro framework JS, poids minimal |

### Choix Technologiques Justifiés

**Pas de SPA (React/Vue)** :
- Trop lourd pour cas d'usage simple
- HTMX suffit pour la dynamique
- Rendu serveur = meilleure performance

**Pas de PostreSQL** :
- SQLite assez puissant pour mono-user
- Zéro configuration, maintenance
- Fichier unique, backup simple

**APScheduler intégré** :
- Pas de dépendance externe (Celery/Redis)
- Suffisant pour les tâches quotidiennes
- Simple à monitorer

**Tailwind CDN** :
- Pas de build pipeline
- Chargement rapide, cache navigateur
- Suffisant pour projet stable

---

## 5. Architecture Fonctionnelle

### Module 1 : Dashboard (`dashboard.py`)
**Rôle** : Vue d'ensemble financière en temps réel

**Fonctionnement** :
- Agrège les données de tous les comptes
- Calcule les totaux (liquidités, épargne, investissements)
- Génère les alertes automatiques
- Prépare les données pour les graphiques

**Interactions** :
- Interroge : Compte, Mouvement, Abonnement, ObjectifEpargne, Placement
- Fournit données au template `index.html`
- Données recalculées à chaque visite (pas de cache)

**Données manipulées** :
```python
{
    "total_liquidites": sum(compte.solde),
    "total_epargne": sum(objectif.montant_actuel),
    "total_investissements": sum(placement.valeur_actuelle),
    "total_patrimoine": liquidités + épargne + investissements,
    "revenus_mois": sum(mouvement.montant où type=Entrée et mois=actuel),
    "charges_mensuelles": sum(abonnement.montant),
    "reste_a_vivre": revenus - charges,
    "prochains_prelevements": list[abonnements dans 7j],
    "alertes": list[alertes générées]
}
```

### Module 2 : Comptes & Liquidités (`comptes.py`)
**Rôle** : Gestion des comptes bancaires et mouvements

**Fonctionnement** :
- CRUD comptes bancaires
- Enregistrement des mouvements (entrées/sorties)
- Suivi du solde par compte
- Ajustement manuel du solde (synchronisation)

**Interactions** :
- Crée/modifie Comptes
- Crée Mouvements
- Met à jour soldes Comptes
- Fournit données à `mouvements.html`

**Endpoints** :
```
GET  /comptes/                          # Page
POST /api/v1/comptes                    # Créer compte
GET  /api/v1/comptes                    # Lister
PUT  /api/v1/comptes/{id}/solde         # Ajuster solde
GET  /api/v1/mouvements                 # Lister mouvements
POST /api/v1/mouvements                 # Enregistrer mouvement
DELETE /api/v1/mouvements/{id}          # Supprimer
```

### Module 3 : Abonnements (`abonnements.py`)
**Rôle** : Gestion des abonnements récurrents + prélèvements auto

**Fonctionnement** :
- CRUD abonnements
- Calcul des charges mensuelles/annuelles
- Génération timeline des prélèvements
- Intégration avec scheduler pour débits auto

**Interactions** :
- Crée Abonnements
- Déclenche Mouvements (via prelevements.py)
- Met à jour soldes Comptes
- Fournit données à `abonnements.html`

**Données manipulées** :
```python
{
    "total_mensuel": sum(abo.montant * coeff_mensuel),
    "total_annuel": sum(abo.montant * coeff_annuel),
    "par_jour": {jour: [abonnements du jour]},
    "par_categorie": {categorie: total_mensuel},
    "prochains": [abos dans 7j avec jours_restants],
    "nb_actifs": count(abo où actif=True)
}
```

### Module 4 : Patrimoine (`epargne.py`, `investissements.py`)
**Rôle** : Suivi épargne, objectifs et investissements

**Fonctionnement** :
- Gestion objectifs d'épargne
- Suivi placements (stocks, crypto, etc.)
- Calcul progression vs objectif
- Visualisation patrimoine global

**Interactions** :
- Crée ObjectifEpargne, Placement
- Fournit données au Dashboard
- Données pour `patrimoine.html`

### Module 5 : Prélèvements Automatiques (`prelevements.py`)
**Rôle** : Exécution automatique des débits d'abonnements

**Fonctionnement** :
```
[APScheduler 00:01 chaque jour]
  ↓
executer_prelevements()
  ├─ Récupère abonnements actifs
  ├─ Filtre : jour_prelevement == aujourd'hui
  ├─ Pour chaque abo :
  │  ├─ Vérifie compte existe
  │  ├─ Crée Mouvement (type: Sortie)
  │  ├─ Met à jour Compte.solde -= montant
  │  └─ Log résultat
  └─ Retour : {total, prelevements_executes[], erreurs[]}
```

**Synchronisation** :
- Toutes les modifications via cette fonction
- Atomicité : tout ou rollback
- Logging exhaustif

### Module 6 : Alertes (`assistant.py`)
**Rôle** : Génération alertes intelligentes

**Alertes possibles** :
- ⚠️ Solde faible (< 500€)
- 🔴 Solde critique (< 100€)
- ✓ Solde sain (> 2000€)
- 📅 Prélèvement imminent (demain)
- 📈 Objectif d'épargne atteint

---

## 6. Description Détaillée de Chaque Écran

### 6.1 Dashboard (`/`)
**Objectif** : Vue d'ensemble financière complète

**Sections** :
1. **EN-TÊTE** :
   - Titre "Tableau de bord"
   - Bouton "Mode discrétion" (toggle eye/eye-slash)
   - Liquidités totales en 4xl

2. **LIQUIDITÉS PRINCIPALES** :
   - Affiche total liquidités (vert émeraude)
   - Patrimoine total à droite
   - Gradient de fond

3. **COMPTES BANCAIRES** :
   - Grille 1-3 colonnes (responsive)
   - Cartes compact : nom, solde, date_maj
   - Hover effect, statut badge (Faible/OK/Surveiller)

4. **RÉPARTITION + RÉSUMÉ** :
   - Donut chart (liquidités/épargne/investissements)
   - 3 KPI : Revenus, Dépenses fixes, Reste à vivre
   - Prochains prélèvements (7j)

5. **ALERTES** :
   - Banners colorées avec icônes
   - Exclamation, check, info circles
   - Message + action

6. **ACTIVITÉ RÉCENTE** :
   - Derniers 5 mouvements
   - Icônes directionnelles + couleurs (vert/rouge)
   - Date, compte, montant

**Comportement** :
- Rechargement auto 0 fois (refresh manuel)
- Mode discrétion : blur-sm + select-none
- Clics sur comptes → filtre `/comptes/?compte_id=X`

### 6.2 Comptes & Liquidités (`/comptes/`)
**Objectif** : Gestion comptes + historique mouvements

**Sections** :
1. **EN-TÊTE** :
   - Titre, total liquidités
   - Grille comptes (ajouter via bouton +)

2. **FORMULAIRES (Colonne gauche)** :
   - Form 1 : Enregistrer flux (compte, type, montant, catégorie, description)
   - Form 2 : Ajuster solde (compte, nouveau solde)

3. **HISTORIQUE (Colonne droite)** :
   - Tableau mouvements
   - Colonnes : Date, Compte, Catégorie, Description, Montant
   - Filtres : compte, type
   - Icônes directionnelles colorées

**Actions** :
- Créer compte (HTMX POST, reload)
- Enregistrer mouvement (HTMX POST, reload)
- Ajuster solde (Fetch PUT Form, reload)
- Filtrer mouvements (JS client-side)

### 6.3 Abonnements (`/abonnements/`)
**Objectif** : Gestion charges récurrentes + vue timeline

**Sections** :
1. **EN-TÊTE** + Bouton "Nouvel abonnement"

2. **KPI CARDS (4 colonnes)** :
   - Charge mensuelle (orange)
   - Coût annuel (rouge)
   - Abonnements actifs (bleu)
   - Prochaine échéance (jaune)

3. **PRÉLÈVEMENTS IMMINENTS** :
   - Cards colorées par urgence (rouge/orange/yellow)
   - Jours restants badge
   - Nom abo, montant, jour

4. **FORMULAIRE NOUVEL ABO** :
   - Inputs : libelle, montant
   - Selects : categorie (custom possible), frequence, compte
   - Input : jour_prelevement (1-31)

5. **RÉPARTITION PAR CATÉGORIE** :
   - Donut chart
   - Tableau détail par catégorie
   - Montant mensuel estimé

6. **CALENDRIER DU MOIS** :
   - Timeline horizontale (jours 1-31)
   - Dots colorés pour prélèvements
   - Couleur : orange/blue/gray (imminent/future/past)

7. **LISTE ABONNEMENTS** :
   - Tableau avec : libelle, categorie badge, frequence, jour, compte, montant
   - Bouton delete (x-circle)

**Comportement** :
- Catégorie "Autre" → Input texte apparaît
- Delete → confirmation puis reload
- Création → reload auto

### 6.4 Patrimoine (`/patrimoine/`)
**Objectif** : Vue patrimoniale globale

**Sections** :
1. **KPI RÉPARTITION** :
   - Liquidités
   - Épargne (objectifs)
   - Investissements
   - Progression vs objectif

2. **OBJECTIFS D'ÉPARGNE** :
   - Tableau/cards objectifs
   - Barre progression
   - Actions : modifier, atteint, supprimer

3. **PLACEMENTS** :
   - Tableau placements
   - Type, valeur, +/- depuis achat
   - Actions : modifier, vendre

4. **PATRIMOINE GLOBAL** :
   - Doughnut chart
   - % répartition
   - Évolution sur 3/6/12 mois

---

## 7. Flux de Données

### Flux 1 : Enregistrement d'un Mouvement

```
[Utilisateur remplit formulaire]
           ↓
[HTMX POST /api/v1/mouvements]
           ↓
[FastAPI creer_mouvement()]
  ├─ Valide données (Pydantic)
  ├─ Récupère compte
  ├─ Crée Mouvement (ORM)
  ├─ Met à jour Compte.solde
  └─ Commit BD
           ↓
[Response: 201 + MouvementRead JSON]
           ↓
[HTMX location.reload()]
           ↓
[Page rafraîchie, affiche nouveaux mouvements + nouveau solde]
           ↓
[Dashboard reflect changements au prochain accès]
```

### Flux 2 : Prélèvement Automatique

```
[00:01 Scheduler déclenche]
           ↓
[executer_prelevements()]
  ├─ Boucle abonnements
  ├─ Filtre : jour_prelevement == 18 (ex)
  ├─ Pour Netflix (jour 18) :
  │  ├─ Créer Mouvement (Sortie, -15.99€)
  │  ├─ Compte.solde -= 15.99
  │  └─ Commit
  └─ Log succès/erreur
           ↓
[Aucune notification utilisateur (automatique)]
           ↓
[Dashboard affiche nouveau solde à la prochaine visite]
           ↓
[Mouvement visible dans /comptes/ avec libellé "Prélèvement auto"]
```

### Flux 3 : Mise à Jour Dashboard

```
[Utilisateur visite /]
           ↓
[FastAPI GET /]
  ├─ Charge tous les comptes
  ├─ Calcule total liquidités
  ├─ Calcule revenus du mois
  ├─ Calcule charges fixes
  ├─ Calcule patrimoine
  ├─ Génère alertes
  └─ Prépare contexte
           ↓
[Jinja2 render index.html avec contexte]
           ↓
[Tailwind + HTMX + Chart.js appliquent styling/comportement]
           ↓
[Navigateur affiche Dashboard complet]
```

### Flux 4 : Modification Catégorie Abonnement (Custom)

```
[Utilisateur select "Autre (personnalisée)"]
           ↓
[onChange: toggleCustomCategorie() (JavaScript)]
           ↓
[Affiche input texte caché]
           ↓
[Utilisateur saisi "Freelance"]
           ↓
[Submit formulaire]
           ↓
[JavaScript remplace select.value par input.value]
           ↓
[HTMX POST /api/v1/abonnements avec categorie="Freelance"]
           ↓
[BD enregistre "Freelance" (nouvelle catégorie)]
           ↓
[Reload page → affiche dans liste + chart]
```

---

## 8. Base de Données

### Schéma Complet

#### Table `compte`
```sql
CREATE TABLE compte (
    id INTEGER PRIMARY KEY,
    nom_banque VARCHAR NOT NULL,
    solde FLOAT DEFAULT 0.0,
    date_maj DATETIME DEFAULT NOW()
);
```
**Relations** : 1 → N Mouvements, 1 → N Abonnements

#### Table `mouvement`
```sql
CREATE TABLE mouvement (
    id INTEGER PRIMARY KEY,
    id_compte INTEGER NOT NULL FK compte.id,
    type ENUM('Entrée', 'Sortie') NOT NULL,
    montant FLOAT NOT NULL,
    categorie VARCHAR,
    description VARCHAR,
    date_mouvement DATETIME DEFAULT NOW()
);
```
**Index** : date_mouvement, type (pour filtres rapides)

#### Table `abonnement`
```sql
CREATE TABLE abonnement (
    id INTEGER PRIMARY KEY,
    libelle VARCHAR NOT NULL,
    montant FLOAT NOT NULL,
    frequence ENUM('Mensuelle', 'Trimestrielle', 'Semestrielle', 'Annuelle') DEFAULT 'Mensuelle',
    jour_prelevement INTEGER (1-31) NOT NULL,
    id_compte INTEGER NOT NULL FK compte.id,
    actif BOOLEAN DEFAULT TRUE,
    categorie VARCHAR,
    date_debut DATETIME,
    date_fin DATETIME
);
```
**Index** : jour_prelevement, actif (pour scheduler)

#### Table `objectif_epargne`
```sql
CREATE TABLE objectif_epargne (
    id INTEGER PRIMARY KEY,
    nom VARCHAR NOT NULL,
    montant_cible FLOAT NOT NULL,
    montant_actuel FLOAT DEFAULT 0.0,
    date_debut DATETIME,
    date_fin DATETIME,
    actif BOOLEAN DEFAULT TRUE
);
```

#### Table `placement`
```sql
CREATE TABLE placement (
    id INTEGER PRIMARY KEY,
    nom VARCHAR NOT NULL,
    type VARCHAR (Stock, Crypto, Immobilier, etc.),
    valeur_achat FLOAT,
    valeur_actuelle FLOAT,
    quantite FLOAT,
    date_achat DATETIME
);
```

### Relations

```
compte (1) ──→ (N) mouvement
        ├──→ (N) abonnement

abonnement (1) ──→ (N) mouvement (via prélèvement auto)

objectif_epargne (standalone)
placement (standalone)
```

### Règles d'Intégrité

1. `compte.solde` peut être négatif (découvert permis)
2. `mouvement.montant` toujours > 0 (le type indique la direction)
3. `abonnement.jour_prelevement` : 1-31 (exécution si jour existe)
4. `objectif_epargne.montant_cible` >= `montant_actuel`
5. Suppression compte → cascade delete mouvements/abonnements

---

## 9. Logique Métier

### Calculs Automatiques

#### 1. Total Liquidités
```python
total_liquidites = sum(compte.solde for compte in comptes)
# Somme tous les soldes, même négatifs
```

#### 2. Revenus du Mois
```python
revenus_mois = sum(
    m.montant for m in mouvements
    if m.type == TypeMouvement.entree
    and m.date_mouvement.month == today.month
    and m.date_mouvement.year == today.year
)
```

#### 3. Charges Mensuelles (Estimées)
```python
charges_mensuelles = sum(
    a.montant for a in abonnements if a.frequence.value == "Mensuelle"
) + sum(
    a.montant / 12 for a in abonnements if a.frequence.value == "Annuelle"
) + sum(
    a.montant / 4 for a in abonnements if a.frequence.value == "Trimestrielle"
) + sum(
    a.montant / 2 for a in abonnements if a.frequence.value == "Semestrielle"
)
```

#### 4. Reste à Vivre
```python
reste_a_vivre = revenus_mois - charges_mensuelles
```

#### 5. Patrimoine Total
```python
total_patrimoine = (
    total_liquidites +
    sum(o.montant_actuel for o in objectifs_epargne) +
    sum(p.valeur_actuelle for p in placements)
)
```

### Synchronisations Automatiques

#### Lors d'un Prélèvement Automatique
1. **Créer Mouvement** (type: Sortie)
   ```python
   mouvement = Mouvement(
       id_compte=abo.id_compte,
       type=TypeMouvement.sortie,
       montant=abo.montant,
       categorie=abo.categorie,
       description=f"Prélèvement automatique: {abo.libelle}"
   )
   ```

2. **Mettre à jour Solde**
   ```python
   compte.solde -= abo.montant
   compte.date_maj = datetime.now(timezone.utc)
   ```

3. **Enregistrer en BD**
   ```python
   db.add(mouvement)
   db.commit()
   ```

4. **Logging**
   ```
   ✓ Prélèvement exécuté: Netflix (15.99€) sur Revolut
   Nouveau solde: 1234.56€
   ```

### Mise à Jour du Dashboard

Après chaque prélèvement, le dashboard (au prochain accès) affiche :
- ✓ Nouveau solde du compte
- ✓ Nouveau total liquidités
- ✓ Nouveau reste à vivre
- ✓ Mouvement dans historique
- ✓ Alertes recalculées

**Aucun cache** → Les données sont toujours fraîches

### Gestion des Erreurs Prélèvements

```python
try:
    # Exécuter prélèvement
except Exception as e:
    db.rollback()  # Annuler tout
    logger.error(f"✗ Prélèvement {abo.id}: {str(e)}")
    # Abo reste actif, prochaine tentative demain
```

---

## 10. Fonctionnalités Déjà Développées

### Phase 1 : Core (Complété)
- ✅ Dashboard avec KPI et alertes
- ✅ Gestion des comptes (CRUD)
- ✅ Enregistrement des mouvements
- ✅ Suivi des soldes en temps réel
- ✅ Filtrage par compte et type

### Phase 2 : Abonnements (Complété)
- ✅ CRUD Abonnements
- ✅ Calcul charges mensuelles/annuelles
- ✅ Catégorisation automatique
- ✅ Timeline calendaire (7 jours)
- ✅ Donut chart répartition

### Phase 3 : Automatisation (Complété)
- ✅ APScheduler intégré
- ✅ Prélèvements quotidiens automatiques
- ✅ Synchronisation soldes
- ✅ Enregistrement mouvements auto
- ✅ Logging exhaustif

### Phase 4 : Design (Complété)
- ✅ Design SaaS premium
- ✅ Mode sombre par défaut
- ✅ 30+ Heroicons monochromes
- ✅ Tailwind CSS optimisé
- ✅ Animations discrètes
- ✅ Responsive (mobile/tablet/desktop)
- ✅ Mode discrétion (eye toggle)

### Phase 5 : Patrimoine (Partiel)
- ✅ Modèles ObjectifEpargne et Placement
- ✅ Endpoints CRUD basiques
- ✅ Affichage dans Dashboard
- ⚠️ Logique avancée (progression, rendements) → À affiner

### Autres
- ✅ Validation Pydantic robuste
- ✅ Gestion erreurs complète
- ✅ Navigation 5 pages
- ✅ Actualisation auto des formulaires (location.reload)
- ✅ HTMX intégré pour dynamique
- ✅ Chart.js pour visualisations

---

## 11. Fonctionnalités Restantes

### P1 (Urgent)
- [ ] Authentification mono-user (optionnel pour l'instant, MVP sans)
- [ ] Export données (CSV/PDF)
- [ ] Recherche/filtrage avancé des mouvements
- [ ] Suppression de mouvements (avec re-sync solde)

### P2 (Important)
- [ ] Prévisions budgétaires (projection 3/6/12 mois)
- [ ] Alertes/notifications (email, push)
- [ ] Récurrence mouvements (e.g. salaire chaque mois)
- [ ] Catégories personnalisées (audit trail)
- [ ] Multi-devise (avec conversion)

### P3 (Améliorations)
- [ ] Dashboard customizable (drag-drop widgets)
- [ ] Historique des changements (audit log)
- [ ] Rapport mensuel/annuel (synthèse)
- [ ] Comparatif mois à mois
- [ ] Mode collaboratif (couples, familles)
- [ ] Budget par catégorie (avec alerte dépassement)
- [ ] Conversion devises automatique
- [ ] Intégration bancaire API (optionnel)

### P4 (UX)
- [ ] Dark/Light mode switcher
- [ ] Thème customizable (couleurs)
- [ ] Taille police ajustable
- [ ] Keyboard shortcuts
- [ ] Offline mode (service worker)

---

## 12. Roadmap

### Trim 1 (Q3 2026)
**MVP Stabilisation**
- Stabiliser prélèvements automatiques (monitoring 4 semaines)
- Tester avec 20+ comptes et 100+ abonnements
- Optimiser requêtes BD (index, N+1)
- Documenter API complètement

### Trim 2 (Q4 2026)
**Export & Alertes**
- Export CSV/PDF mouvements et bilan
- Système d'alertes (faible solde, dépassement budget)
- Prévisions simples (12 mois)

### Trim 3 (Q1 2027)
**Améliorations UX**
- Recherche mouvements avancée
- Dashboard customizable
- Rapports mensuels automatiques

### Trim 4+ (Q2 2027+)
**Extension Fonctionnelle**
- Multi-devise
- Budget par catégorie
- Intégration bancaire
- Mode collaboratif

---

## 13. Règles de Développement

### Style de Code

#### Python (Backend)
```python
# ✓ BON
def creer_mouvement(
    id_compte: int = Form(...),
    type: str = Form(...),
    montant: float = Form(...),
    db: Session = Depends(get_db)
) -> MouvementRead:
    """Enregistre un mouvement financier."""
    compte = db.get(Compte, id_compte)
    if not compte:
        raise HTTPException(status_code=404)
    # ...
    return mouvement

# ✗ MAUVAIS
def creer_mvt(idc, t, m, db):
    c = db.get(C, idc)
    if not c:
        raise Exception("Not found")
    # ...
```

**Conventions** :
- Noms explicites (creer_mouvement, pas cm)
- Type hints systématiques
- Docstrings pour fonctions publiques
- Max 100 caractères/ligne
- Espaces autour opérateurs
- Imports triés (stdlib, externes, locaux)

#### HTML/Jinja2 (Frontend)
```html
<!-- ✓ BON -->
<div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
    <p class="text-xs text-gray-500 uppercase tracking-widest">
        {{ icons.icon("banknotes", "16") }} Total Liquidités
    </p>
    <p class="valeur text-2xl font-bold text-emerald-400">
        {{ "%.2f"|format(total) }} €
    </p>
</div>

<!-- ✗ MAUVAIS -->
<div style="background: #111; border: 1px solid #333; padding: 10px">
    <p style="font-size: 12px">Liquides</p>
    <p>{{ total }}</p>
</div>
```

**Conventions** :
- Tailwind classes (jamais de style inline)
- Indentation 4 espaces
- Commentaires explicatifs avant sections
- Macros pour répétition
- Structure sémantique (section, article, div)

#### JavaScript (Vanilla)
```javascript
// ✓ BON
async function chargerMouvements() {
    try {
        const res = await fetch('/api/v1/mouvements');
        const data = await res.json();
        afficherMouvements(data);
    } catch (error) {
        console.error('Erreur:', error);
        afficherAlerte('Erreur chargement mouvements');
    }
}

// ✗ MAUVAIS
function load(){
  $.get('/api/mouvements',function(d){
    $('#list').html(d)
  })
}
```

**Conventions** :
- const/let (jamais var)
- Noms de fonctions explicites
- Try-catch pour async
- Pas de dépendances externes (sauf Chart.js)
- Event listeners explicites

### Organisation des Fichiers

```
app/
├── models/           → 1 fichier par modèle (compte.py, mouvement.py)
├── schemas/          → 1 fichier par schéma (matching models)
├── routers/          → 1 fichier par route (dashboard.py, comptes.py)
├── services/         → Logique métier (prelevements.py, assistant.py)
├── templates/        → Jinja2, organisé par feature
└── database.py       → Configuration unique
```

### Nommage

| Élément | Convention | Exemple |
|---------|------------|---------|
| Classe Python | PascalCase | `Mouvement`, `CompteCreate` |
| Fonction Python | snake_case | `executer_prelevements()` |
| Variable Python | snake_case | `total_liquidites` |
| Endpoint | kebab-case | `/api/v1/comptes/{id}/solde` |
| Template | kebab-case | `mouvements.html` |
| CSS Class | kebab-case | `.account-card`, `.kpi-mini` |
| Database Column | snake_case | `date_mouvement`, `id_compte` |
| Enum | PascalCase | `TypeMouvement`, `FrequenceAbonnement` |

### Composants Réutilisables

#### Macros Jinja2
- `icons.icon(name, size, class)` → Retourne SVG Heroicon
- `components.kpi_mini(titre, valeur, unite, icone, couleur)` → KPI compact
- `components.bank_card_compact(compte)` → Carte compte
- `components.section_card(titre, icone)` → Container section

#### Patterns Réutilisables
1. **CRUD Form** :
   ```html
   <form hx-post="/api/v1/entite" 
         hx-on::after-request="if(event.detail.xhr.status === 201) { location.reload(); }">
   ```

2. **Filtre Dropdown** :
   ```html
   <select onchange="filtrer()">
       <option value="">— Tous —</option>
   </select>
   ```

3. **Delete Confirmation** :
   ```javascript
   if (!confirm('Confirmer suppression ?')) return;
   ```

### Gestion des Erreurs

```python
# ✓ BON : Erreur utilisateur vs système
@router.post("/api/v1/comptes")
def creer_compte(payload: CompteCreate, db: Session) -> CompteRead:
    if payload.solde < 0:
        raise HTTPException(
            status_code=400,
            detail="Solde ne peut pas être négatif"
        )
    try:
        compte = Compte(**payload.model_dump())
        db.add(compte)
        db.commit()
        return compte
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur création compte: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur serveur"
        )
```

### Gestion des États (Frontend)

**State Management Simple** :
- Variables globales JS `const` pour config
- LocalStorage pour user prefs (mode discrétion)
- Pas de flux Redux/Vuex complexe
- HTMX pour sync serveur

```javascript
// ✓ BON : State simple + localStorage
const modeDiscretion = localStorage.getItem('mode_discretion') === 'true';

function toggleDiscretion() {
    const newMode = !modeDiscretion;
    localStorage.setItem('mode_discretion', newMode);
    location.reload();
}

// ✗ MAUVAIS : State dans Global
window.state = { discretion: false };  // Faut pas
```

### Responsive Design

**Breakpoints Tailwind** :
```html
<!-- Mobile first + Tailwind breakpoints -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
    <!-- 1 col mobile, 2 tablet, 3 desktop -->
</div>

<!-- Masquer/Montrer -->
<td class="hidden md:table-cell">Desktop only</td>
```

**Testée sur** :
- Mobile (375px - iPhone SE)
- Tablet (768px - iPad)
- Desktop (1024px+)

### Accessibilité

```html
<!-- ✓ BON : Sémantique + ARIA -->
<button aria-label="Activer mode discrétion" onclick="toggle()">
    <span id="icone-discretion">{{ icons.icon("eye", "16") }}</span>
</button>

<!-- ✗ MAUVAIS -->
<div onclick="toggle()">👁️</div>
```

**Standards minimums** :
- Labels explicites
- Alt text pour images
- Contraste ≥ 4.5:1
- Keyboard navigation (Tab)
- Sémantique HTML5

---

## 14. Principes UX/UI

### Ligne Directrice de Design

```
FinanSmart = SaaS Premium + Minimalisme + Efficacité
```

### Palette Couleurs

```
Arrière-plan : #020817 (slate-975)
Cartes       : #111827 (gray-950) et #1f2937 (gray-900)
Bordures     : #1f2937 (gray-800)
Texte Primaire : #ffffff
Texte Secondaire : #9ca3af (gray-400)
Accent Primaire : #10b981 (emerald-600) - Actions, success
Accent Secondaire :
  - Orange (#f97316) - Charges, warning
  - Red (#ef4444) - Critique
  - Blue (#3b82f6) - Info
  - Purple (#8b5cf6) - Épargne
```

### Typographie

| Usage | Police | Taille | Poids | Classe Tailwind |
|-------|--------|--------|-------|-----------------|
| Titre Page | Inter/Poppins | 1.875rem | Bold | text-3xl font-bold |
| Sous-titre | Inter/Poppins | 0.875rem | Medium | text-sm font-medium |
| Body Text | Inter/Poppins | 0.875rem | Normal | text-sm |
| Small Text | Inter/Poppins | 0.75rem | Normal | text-xs |
| Nombres | JetBrains Mono | 1.125rem | Semibold | text-lg font-semibold |
| Caption | Inter/Poppins | 0.75rem | Normal | text-xs text-gray-500 |

**Règle** : Nombres avec `font-variant-numeric: tabular-nums` (chiffres alignés)

### Spacing (Compact Intentionnel)

```css
/* Tailwind spacing réduit */
p-3  /* 12px vertical */
p-4  /* 16px vertical */
gap-2 gap-3 /* Espacements réduits entre éléments */
mb-6 /* Espacement section */

/* Théorie : Permet afficher plus d'infos sans scroller */
```

### Composants

#### Cards
```html
<div class="bg-gray-900 border border-gray-800 rounded-lg p-4">
    <!-- Contenu -->
</div>
```
**Propriétés** :
- Fond gris foncé
- Bordure subtile
- Padding 16px
- Radius 8px
- Ombre subtile au hover

#### Boutons
```html
<!-- Primary (Émeraude) -->
<button class="bg-emerald-600 hover:bg-emerald-500 text-white">

<!-- Secondary (Gris) -->
<button class="bg-gray-800 hover:bg-gray-700 text-gray-300">

<!-- Outline -->
<button class="border border-gray-700 text-gray-400 hover:border-emerald-600">
```

#### Inputs
```html
<input class="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 
            text-white placeholder-gray-600 
            focus:outline-none focus:border-emerald-500">
```

### Icônes

**Heroicons Monochromes** (30+ définies) :
- Format : `{{ icons.icon("name", "16/20/24", "class") }}`
- Stroke-width : 2
- Couleur : `currentColor` (héritée)
- Exemples : banknotes, minus-circle, calculator, chart-pie, etc.

**Utilisation** :
```html
{{ icons.icon("banknotes", "16", class="text-emerald-400") }}
```

### Animations

```css
/* Définies dans custom.css */
.fade-in-up { animation: fadeInUp 0.4s ease-out; }
.slide-in-right { animation: slideInRight 0.3s ease-out; }
.pulse-subtle { animation: pulseSubtil 2s ease-in-out infinite; }
```

**Utilisation minimale** :
- Transitions au hover (color, opacity)
- Pas d'animations de page entière
- Durée : 200-400ms

### Hiérarchie Visuelle

1. **Très important** : Large, bold, accent color
   ```html
   <p class="text-2xl font-bold text-emerald-400">1234.56 €</p>
   ```

2. **Important** : Normal size, white, semibold
   ```html
   <p class="text-sm font-semibold text-white">Netflix</p>
   ```

3. **Support** : Small, gray, normal
   ```html
   <p class="text-xs text-gray-500">Le 5 de chaque mois</p>
   ```

### Mode Discrétion

```javascript
// Toggle : localStorage + blur
if (modeDiscretion) {
    document.body.classList.add('blur-mode');
    // Tous les .valeur deviennent blur-sm + select-none
}
```

### Responsive Design Appliqué

**Mobile-first** :
```html
<!-- 1 colonnes mobile → 2 tablet → 3 desktop -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">

<!-- Masquer sur mobile -->
<td class="hidden md:table-cell">

<!-- Stack vertical mobile -->
<div class="flex flex-col md:flex-row">
```

---

## 15. Contraintes Techniques

### Serveur / Infrastructure

| Contrainte | Détail | Impact |
|-----------|--------|--------|
| **RAM** | 8 GB | Pas de cache agressif, pas de ML |
| **Stockage** | 250 GB | BD SQLite suffisante, aucun fichier volumineux |
| **OS** | Linux (Ubuntu/Debian) | Scripts shell pour déploiement |
| **Processeur** | Standard | Pas de calculs lourds |
| **Bande passante** | Supposée limitée | Zéro streaming, API minimaliste |
| **Uptime** | 99.5% (objectif) | Logs robustes, alertes critiques |

### Base de Données

| Contrainte | Détail | Impact |
|-----------|--------|--------|
| **Type** | SQLite (fichier unique) | Pas de réplication, backup facile |
| **Taille Max Estimée** | 100 MB | Suffisant pour 10 ans de données |
| **Backups** | Copie fichier .db quotidienne | Via cron job |
| **Optimisations** | Index sur colonnes filtrées | Queries < 100ms |
| **Multi-access** | WAL mode (Write-Ahead Logging) | Lectures + écritures simultanées |

### Performances

| Cible | Métrique | Target |
|-------|----------|--------|
| **Charge page** | FCP (First Contentful Paint) | < 500ms |
| **Dashboard** | Temps du rendu Jinja2 | < 200ms |
| **API moyenne** | Réponse query | < 50ms |
| **Prélèvements** | 100 abon./jour | < 1s total |
| **Tailwind CSS** | Fichier gzippé | ~ 30-40 KB |
| **JS Vanilla** | Code total | < 50 KB |

### Dépendances

| Dépendance | Version | Justification | Critique |
|-----------|---------|---------------|----------|
| FastAPI | 0.111.0 | Framework moderne, rapide | ✓ |
| Uvicorn | 0.29.0 | Serveur ASGI performant | ✓ |
| SQLAlchemy | 2.0.30 | ORM standard Python | ✓ |
| Jinja2 | 3.1.4 | Templating serveur | ✓ |
| APScheduler | 3.10.4 | Scheduler intégré | ✓ |
| Pydantic | (built-in) | Validation fastapi | ✓ |
| Tailwind CSS | (CDN) | Styling utility-first | ✓ |
| HTMX | 1.9.12 | Dynamique légère | ○ (remplaçable) |
| Chart.js | 4.x | Graphiques | ○ (optionnel) |
| Heroicons | (SVG) | Icônes | ○ (remplaçable) |

**Legend** : ✓ Critique (jamais enlever), ○ Optionnel (remplac easy)

### Limitations Volontaires

1. **Pas d'authentification multi-users** → Mono-user, gain de complexité énorme
2. **Pas de synchronisation bancaire** → Saisie manuelle, privacy garantie
3. **Pas de mobile app native** → Progressive Web App future
4. **Pas de notifications temps réel** → Batch quotidienne suffisante
5. **Pas de reporting BI** → Tableaux simples pour MVP
6. **Pas d'intégration API tierce** → Extensibilité minimale pour MVP

---

## 16. Philosophie de Développement

### Principes Fondamentaux

#### 1. Simplicité D'Abord
```
"Choisissez la solution la plus simple qui fonctionne"

✓ SQLite > PostreSQL (pour ce projet)
✓ HTMX + Jinja2 > React SPA
✓ Procs serveur > Message queue
✗ N'ajoutez pas de lib "au cas où"
```

#### 2. Cohérence
```
"Maintenez la même approche partout"

✓ Tous les formulaires avec HTMX
✓ Tous les KPI avec même styling
✓ Toutes les listes avec mêmes colonnes
✓ Tous les erreurs avec même format
```

#### 3. Modularité
```
"Une fonction = Une responsabilité"

✓ creer_abonnement() : crée et valide
✓ executer_prelevements() : débite seulement
✓ Logique métier séparée du transport HTTP
```

#### 4. Maintenabilité
```
"Facilitez les modifications futures"

✓ Noms explicites (pas de abrévs)
✓ Docstrings sur fonctions publiques
✓ Types hints partout
✓ Tests unitaires pour logique
✓ Pas de "hack" ou code "magique"
```

#### 5. Performances
```
"Rapide par défaut, optimisez seulement si nécessaire"

✓ Indexes sur colonnes filtrées
✓ Pas de N+1 queries
✓ Caching HTTP (headers)
✓ Lazy loading images (future)
```

#### 6. Expérience Utilisateur
```
"L'user avant la technique"

✓ Actions sans rafraîchissement manuel
✓ Feedback immédiat (validation client)
✓ Libellés explicites, pas de jargon
✓ Erreurs claires, pas de codes HTTP raw
```

### Approche Incrémentale

```
Phase 1: MVP Fonctionnel
  ├─ Core 3 modules (Dashboard, Comptes, Abonnements)
  ├─ Design cohérent
  └─ Automatisation basique

Phase 2: Stabilisation
  ├─ Bugs fixes
  ├─ Performances
  └─ Documentation

Phase 3: Améliorations UX
  ├─ Nouvelle features mineure
  ├─ Refinement design
  └─ Feedback utilisateur

Phase 4: Extensibilité
  ├─ API documentée
  ├─ Plugins/extensions
  └─ Intégrations externes
```

### Éviter les Anti-Patterns

```python
# ✗ ANTI-PATTERN 1 : God Classes
class Dashboard:
    def creer_compte(self): ...
    def enregistrer_mouvement(self): ...
    def generer_alertes(self): ...
    def tout_faire_dans_classe(self): ...

# ✓ MIEUX : Séparation des responsabilités
# dashboard.py → aggregation
# comptes.py → gestion comptes
# services/ → logique métier

# ✗ ANTI-PATTERN 2 : Query N+1
for compte in comptes:
    print(compte.mouvements)  # ← N+1 queries!

# ✓ MIEUX : Eager loading
comptes = db.query(Compte).options(
    selectinload(Compte.mouvements)
).all()

# ✗ ANTI-PATTERN 3 : Magic strings
if type == "Entrée":  # magic string partout

# ✓ MIEUX : Enums
if type == TypeMouvement.entree:  # typage fort

# ✗ ANTI-PATTERN 4 : Validation partout
def creer(data):
    if not data["libelle"]: raise Error
    if data["montant"] < 0: raise Error
    # Validation manuelle partout

# ✓ MIEUX : Pydantic schemas
def creer(payload: AbonnementCreate):
    # Pydantic valide automatiquement
    abonnement = Abonnement(**payload.model_dump())
```

---

## 17. Consignes pour Claude Code

### Comment Travailler sur ce Projet

#### 1. Avant Chaque Modification

```
[ ] Lire le contexte du projet (ce document)
[ ] Identifier le module affecté
[ ] Vérifier les dépendances existantes
[ ] Évaluer l'impact sur d'autres modules
[ ] Valider avec la philosophy du projet
```

#### 2. Architecture First

```
✓ Respectez la structure existante
  app/models/*.py → ORM models uniquement
  app/schemas/*.py → Pydantic validation uniquement
  app/routers/*.py → Endpoints HTTP uniquement
  app/services/*.py → Logique métier uniquement

✗ Ne mélangez pas les responsabilités
  Ne mettez pas de logique métier dans les routers
  Ne mettez pas de validation dans les models
```

#### 3. Ne Jamais Casser une Fonctionnalité

```
[ ] Avant de modifier: tester l'existant
[ ] Après modification: re-tester la feature
[ ] Si breaking change: communiquer et mettre à jour doc
[ ] Garder backward compatibility si possible
```

#### 4. Réutilisabilité

```
✓ Créez des macros Jinja2 pour l'HTML répété
✓ Créez des schemas Pydantic réutilisables
✓ Extrayez la logique métier en services
✓ Nommez explicitement

✗ Ne dupliquez jamais de code
✗ Ne créez pas de "code one-off"
```

#### 5. Proposez des Améliorations Cohérentes

```
Avant d'ajouter une feature:

[ ] Est-ce que ça s'intègre au design existant ?
[ ] Ça réutilise les patterns existants ?
[ ] C'est simple à maintenir ?
[ ] Ça peut être testé ?
[ ] Ça aide vraiment l'user ?

Si NON à une question → Refactorisez d'abord
```

#### 6. Documentation à Jour

```
[ ] Commentez les parties complexes
[ ] Mettez à jour PROJECT_CONTEXT.md si breaking change
[ ] Documentez les nouvelles fonctionnalités
[ ] Fournissez des exemples de code
[ ] Expliquez les choix techniques (Pourquoi pas X ?)
```

#### 7. Testabilité

```python
# ✓ BON : Facile à tester
def calculer_charges(abonnements: list[Abonnement]) -> float:
    return sum(a.montant * coeffs[a.frequence] for a in abonnements)

# Testable : def test_calculer_charges(): ...

# ✗ MAUVAIS : Difficile à tester
def calculer():
    abos = db.query(Abonnement).all()
    # Dépendance DB implicite, impossible à mocker
    return sum(...)
```

#### 8. Logging & Monitoring

```python
# ✓ BON : Logs utiles
logger.info(f"✓ Prélèvement exécuté: {abo.libelle} ({abo.montant}€)")
logger.error(f"✗ Erreur prélèvement {abo.id}: {str(e)}")

# ✗ MAUVAIS : Logs inutiles
print("OK")  # Pas de contexte
logger.debug("Function called")  # Trop verbose
```

#### 9. Validation & Erreurs

```python
# ✓ BON : Erreurs utilisateur claires
if payload.montant <= 0:
    raise HTTPException(
        status_code=400,
        detail="Le montant doit être supérieur à 0"
    )

# ✗ MAUVAIS : Erreurs vagues
if not payload.montant:
    raise Exception("Invalid input")
```

#### 10. Performance First

```
[ ] Avez-vous testé la requête BD ?
[ ] Y a-t-il un index sur les colonnes filtrées ?
[ ] Y a-t-il du N+1 query ?
[ ] Le rendu Jinja2 est rapide (< 200ms) ?
[ ] Le CSS Tailwind inclut que ce qui est utilisé ?
```

#### 11. Checkliste Avant Commit

```
Code:
  [ ] Suit les conventions du projet
  [ ] Pas de code mort ou console.log()
  [ ] Type hints sur Python
  [ ] Classes/functions bien nommées
  [ ] Tests existants passent

Design:
  [ ] UI cohérente avec le projet
  [ ] Responsive (mobile/tablet/desktop)
  [ ] Contraste ≥ 4.5:1
  [ ] Icônes Heroicons utilisées

Documentation:
  [ ] Docstring sur functions publiques
  [ ] Commentaires sur logique complexe
  [ ] PROJECT_CONTEXT.md mis à jour si besoin
  [ ] README reflète l'état actuel

Performance:
  [ ] Pas de regression (FCP < 500ms)
  [ ] BD queries optimisées (< 50ms)
  [ ] Assets minifiés
```

#### 12. Quand Vous Êtes Bloqué

```
1. Relisez le contexte (ce doc)
2. Cherchez un pattern similaire dans le code
3. Questionnez les assumptions (vs les contraintes réelles)
4. Proposez la solution la plus simple
5. Demandez feedback avant d'implémenter
```

#### 13. Contacter le Product Owner

```
Communiquez si:
- Breaking change architecture
- Nouvelle feature majeure
- Dépendance externe nécessaire
- Modification budget/perf
- Changement dans les règles métier
```

### Workflow Idéal

```
1. [PLAN] Lire contexte, identifier module
2. [DESIGN] Sketch la solution (pseudocode, flux)
3. [IMPLEMENT] Coder en respectant patterns
4. [TEST] Valider fonctionnalité + pas de regression
5. [DOCUMENT] Mettre à jour PROJECT_CONTEXT.md
6. [REVIEW] Self-review avant commit
7. [DEPLOY] Tester en staging avant prod
```

---

## 18. Notes Finales & Ressources

### Fichiers Clés à Consulter

1. **`app/main.py`** → Point d'entrée, scheduler
2. **`app/services/prelevements.py`** → Logique automatisation
3. **`app/templates/index.html`** → Dashboard référence de design
4. **`app/models/`** → Schéma BD complet
5. **`requirements.txt`** → Stack technique complet

### Documentation Générée

- `PROJECT_CONTEXT.md` ← Vous êtes ici
- `AUTOMATISATION_PRELEVEMENTS.md` ← Prélèvements spécifiquement
- Docstrings dans les fonctions publiques
- Types hints comme documentation

### Ressources Externes

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [HTMX](https://htmx.org/)
- [Chart.js](https://www.chartjs.org/)
- [Heroicons](https://heroicons.com/)

### Questions Fréquentes

**Q: Comment ajouter un nouvel abonnement ?**
A: Via POST `/api/v1/abonnements` avec les champs requis. Voir `abonnements.py`.

**Q: Pourquoi SQLite et pas PostgreSQL ?**
A: Mono-user, zéro config, backups faciles, 8GB RAM suffisent.

**Q: Comment modifier le schedule des prélèvements ?**
A: Fichier `app/main.py`, ligne du scheduler. Actuellement 00:01 chaque jour.

**Q: Où sont les logs des prélèvements ?**
A: stdout/stderr (voir logs Uvicorn). Considérez un fichier de log en prod.

**Q: Comment tester les prélèvements ?**
A: Créer abonnement avec jour_prelevement = aujourd'hui, puis le scheduler l'exécutera demain à 00:01 (ou testez en modifiant la date système).

---

## Conclusion

**FinanSmart** est une application financière minimaliste, performante et automatisée. Elle repose sur une architecture simple mais robuste, des choix technologiques justifiés, et une philosophie de développement axée sur la simplicité et la maintenabilité.

Chaque modification doit respecter cette philosophie, la cohérence du design et l'architecture existante. En suivant ce contexte, tout développeur peut contribuer efficacement sans rompre la philosophie du projet.

Bienvenue dans l'équipe FinanSmart ! 🚀

---

**Document Version** : 1.0  
**Date** : 2026-07-18  
**Auteur** : AI Assistant (Claude)  
**État** : Production-Ready MVP
