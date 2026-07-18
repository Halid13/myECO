CAHIER DES CHARGES FONCTIONNEL : FINANSMART
PARTIE 1 : RÉSUMÉ SYNTHÉTIQUE DU PROJET
Contexte du projet
À l'ère de la numérisation des services financiers, la centralisation des données bancaires repose quasi exclusivement sur des applications tierces en mode SaaS (Software as a Service) ou des agrégateurs cloud. Ces solutions posent des risques majeurs en matière de souveraineté des données, de confidentialité et de dépendance à des infrastructures externes.
Le projet FinanSmart est né de la volonté de concevoir une alternative souveraine, développée from scratch et auto-hébergée. L'application s'exécute localement au sein d'une machine virtuelle Debian dédiée, garantissant à l'utilisateur un contrôle absolu sur son patrimoine informationnel sans aucune fuite de données vers l'extérieur.
Objectifs poursuivis
•	Souveraineté et sécurité : Supprimer tout intermédiaire ou API de synchronisation bancaire tierce en privilégiant une gestion locale et cloisonnée.
•	Performance et légèreté : Déployer une stack technique à très faible empreinte matérielle, optimisée pour s'exécuter de manière fluide sur un serveur local sans consommer de ressources superflues.
•	Centralisation patrimoniale : Offrir une vision unifiée, en temps réel, de la situation financière globale de l'utilisateur (comptes courants, épargne, investissements).
Besoins auxquels il répond
FinanSmart répond au besoin d'un utilisateur averti souhaitant piloter ses finances personnelles de manière rigoureuse sans concéder sa vie privée. Il comble l'absence d'outils d'agrégation simples qui soient à la fois graphiques, intelligents (moteur de règles d'aide à la décision) et entièrement déconnectés des réseaux cloud publics.
Principales fonctionnalités attendues
1.	Dashboard de synthèse : Vue consolidée multi-banques en mode sombre avec indicateurs clés (somme totale, reste à vivre, répartition d'actifs).
2.	Livre de comptes manuel : Enregistrement des flux financiers et ajustement des soldes par banque.
3.	Échéancier des charges fixes : Registre et alertes visuelles sur les abonnements et dépenses récurrentes.
4.	Suivi d'objectifs d'épargne : Visualisation de la progression des réserves financières par jauges de progression.
5.	Valorisation des investissements : Calcul automatique des performances (plus/moins-values) latentes du portefeuille.
6.	Moteur d'analyse local : Système d'alerte et de recommandation basée sur des règles logiques pour optimiser la distribution des liquidités.
Enjeux et valeur ajoutée
L'enjeu majeur réside dans le respect strict du paradigme "Local & Lightweight". La valeur ajoutée de la solution repose sur l'intégration d'un moteur de conseil intelligent fonctionnant en circuit fermé. L'application ne se contente pas d'afficher des données brutes : elle analyse l'équilibre des comptes et suggère des arbitrages financiers sans jamais exposer les données de l'utilisateur.
PARTIE 2 : DESCRIPTION DÉTAILLÉE DES MODULES FONCTIONNELS
MODULE 1 : Tableau de Bord Consolidé (Le "Dashboard")
Objectif et rôle dans l'application
Le Dashboard est le cœur visuel de FinanSmart. C’est l'écran d'accueil par défaut de l'utilisateur. Son rôle est de fournir une synthèse macroscopique instantanée de la santé financière globale sans obliger l'utilisateur à naviguer dans les sous-menus. Il agrège les données calculées par les autres modules pour les restituer de manière graphique et épurée.
Fonctionnalités regroupées
•	Affichage de la situation des liquidités (3 cartes bancaires distinctes).
•	Calcul et affichage de la somme globale consolidée.
•	Graphique de répartition patrimoniale (Liquidités vs Épargne vs Investissements).
•	Bloc des indicateurs mensuels (Revenus, Charges fixes, Reste à vivre).
•	Flux d'alertes à court terme (Abonnements imminents et conseils de l'assistant).
Déroulement du parcours utilisateur étape par étape
1.	L'utilisateur se connecte à l'application via son tunnel privé (VPN/Tailscale).
2.	La page d'accueil s'affiche immédiatement en mode sombre.
3.	L'utilisateur consulte d'un coup d'œil le montant total disponible et vérifie si une carte bancaire affiche un solde anormalement bas.
4.	Il regarde le graphique circulaire pour valider la répartition de ses actifs.
5.	Il prend connaissance des messages d'alerte ou de conseil affichés en bas du tableau de bord avant de décider d'effectuer une action de gestion.
Actions que l'utilisateur peut effectuer
•	Visualiser l'ensemble des données consolidées.
•	Cliquer sur une carte bancaire pour être redirigé vers l'onglet "Mouvements & Abonnements" avec un filtre pré-appliqué sur la banque sélectionnée.
•	Masquer/Afficher les valeurs numériques (mode discret pour préserver la confidentialité si un tiers regarde l'écran).
Données manipulées
•	En entrée (Read-only depuis la base de données) : Noms des banques, soldes courants, dates de mise à jour, montants des abonnements actifs, valeurs des investissements, montants des objectifs d'épargne.
•	En sortie (Calculées à la volée par le backend FastAPI) : Somme totale consolidée, somme des revenus mensuels, somme des charges fixes mensuelles, reste à vivre estimé, pourcentages d'allocation patrimoniale.
Interactions avec les autres modules
•	Module 2 (Comptes) : Reçoit les soldes à jour pour alimenter les cartes bancaires et le compteur de la somme totale.
•	Module 3 (Abonnements) : Reçoit la liste des prélèvements des 7 prochains jours pour l'affichage des alertes d'échéances et le calcul du résumé mensuel.
•	Modules 4 & 5 (Épargne & Investissements) : Récupère les totaux pour générer le graphique de répartition patrimoniale.
•	Module 6 (Assistant) : Récupère les chaînes de texte des conseils générés pour les afficher dans l'encadré dédié.
MODULE 2 : Gestion des Comptes & Liquidités
Objectif et rôle dans l'application
Ce module fait office de livre de comptes et de registre des liquidités. Son rôle est de permettre le suivi rigoureux de l'argent disponible sur les comptes courants. C'est l'outil de saisie principal qui remplace la synchronisation bancaire automatique par une gestion humaine, volontaire et précise.
Fonctionnalités regroupées
•	Tableau historique des mouvements financiers (entrées et sorties).
•	Système de filtrage et de tri des mouvements par banque et par catégorie.
•	Formulaire d'ajustement rapide des soldes bancaires.
•	Formulaire d'enregistrement d'un flux financier ponctuel (salaire, virement, achat).
Déroulement du parcours utilisateur étape par étape
1.	L'utilisateur accède à l'onglet "Mouvements & Abonnements".
2.	Il visualise le tableau récapitulatif des derniers mouvements saisis.
3.	Pour mettre à jour son solde après consultation de son application bancaire réelle, il clique sur "Ajuster un solde".
4.	Il sélectionne la banque concernée dans une liste déroulante, saisit le nouveau montant exact, puis valide.
5.	S'il veut ajouter un mouvement précis (ex: réception du salaire), il ouvre le formulaire de saisie de flux, remplit les champs obligatoires, et valide. Le tableau se rafraîchit instantanément via HTMX sans rechargement de page.
Actions que l'utilisateur peut effectuer
•	Ajouter, modifier ou supprimer un mouvement financier (crédit/débit).
•	Forcer la mise à jour du solde d'un compte courant à une valeur T précise.
•	Filtrer l'historique par banque pour pointer ses comptes.
Données manipulées
•	compte : ID, Nom de la banque, Solde actuel, Date de dernière mise à jour.
•	mouvement : ID, ID_Compte, Type (Entrée/Sortie), Montant, Catégorie (Salaire, Courses, etc.), Date du mouvement, Description/Libellé.
Interactions avec les autres modules
•	Module 1 (Dashboard) : Met à jour instantanément les cartes bancaires et le solde global dès qu'un solde ou un mouvement est validé.
•	Module 6 (Assistant) : Fournit l'historique des flux et l'état des soldes pour alimenter les algorithmes de détection d'anomalies (ex: compte proche du découvert).
MODULE 3 : Module Dépenses Fixes & Abonnements
Objectif et rôle dans l'application
Ce module est un outil de planification budgétaire spécialisé dans la gestion des charges récurrentes. Son rôle est d'isoler les dépenses incompressibles (abonnements, factures régulières) afin de sécuriser le calcul du reste à vivre et d'éviter les surprises de trésorerie en cours de mois.
Fonctionnalités regroupées
•	Registre d'enregistrement des abonnements et charges fixes.
•	Calculateur automatisé du coût mensuel cumulé des charges fixes.
•	Générateur d'échéancier (Timeline chronologique des prélèvements du mois).
Déroulement du parcours utilisateur étape par étape
1.	L'utilisateur se rend dans la section dédiée aux abonnements.
2.	Il consulte la liste de ses engagements actifs triés par ordre chronologique de prélèvement dans le mois.
3.	Pour ajouter une nouvelle charge (ex : un abonnement de streaming), il clique sur "Ajouter un abonnement".
4.	Il renseigne le nom, le montant, le jour du prélèvement (ex: le 5 du mois) et le compte bancaire associé.
5.	Le système recalcule immédiatement la "Charge Fixe Mensuelle" et met à jour l'échéancier visuel.
Actions que l'utilisateur peut effectuer
•	Créer, modifier les paramètres ou résilier (supprimer) un abonnement dans le registre.
•	Visualiser sous forme de liste chronologique les prélèvements à venir.
Données manipulées
•	abonnement : ID, Libellé, Montant, Fréquence (Mensuelle, Annuelle), Jour du prélèvement (entier entre 1 et 31), ID_Compte_Associé, Statut (Actif/Inactif).
Interactions avec les autres modules
•	Module 1 (Dashboard) : Injecte la somme totale des abonnements dans le bloc "Résumé Mensuel" pour soustraire ce montant des revenus et afficher le "Reste à vivre". Alimente l'encadré "Prochains prélèvements".
•	Module 6 (Assistant) : Transmet le montant total des charges fixes pour que l'assistant puisse évaluer le ratio charges/revenus.
MODULE 4 : Épargne & Projets
Objectif et rôle dans l'application
Ce module est orienté vers le suivi des objectifs financiers à moyen et long termes. Son rôle est de matérialiser visuellement les efforts d'épargne non investis sur les marchés (livrets de précaution, fonds de réserve pour des projets spécifiques comme l'achat de matériel ou les vacances). Il permet de sanctuariser cet argent pour éviter qu'il ne soit confondu avec les liquidités du quotidien.
Fonctionnalités regroupées
•	Création de projets ou de "poches" d'épargne ciblées.
•	Suivi de la progression vers un objectif financier défini avec barres de progression CSS dynamiques.
•	Historique des efforts d'épargne mensuels (comparatif M / M-1).
Déroulement du parcours utilisateur étape par étape
1.	L'utilisateur bascule sur l'onglet "Patrimoine".
2.	La section supérieure lui présente ses différents livrets sous forme de jauges (ex : "Épargne de précaution : 4500 € / 10 000 €", jauge remplie à 45%).
3.	S'il effectue un virement réel de son compte courant vers son livret, il clique sur la jauge correspondante dans FinanSmart.
4.	Il saisit le montant ajouté (ex: +250 €) et valide.
5.	La jauge progresse visuellement et le système enregistre la date de l'effort d'épargne.
Actions que l'utilisateur peut effectuer
•	Créer un nouvel objectif d'épargne avec un montant cible.
•	Alimenter ou vider (en cas de coup dur) une poche d'épargne.
•	Éditer ou clôturer un projet d'épargne.
Données manipulées
•	objectif_epargne : ID, Nom du projet, Montant actuel, Montant cible, Date limite (optionnelle), Statut.
•	historique_epargne : ID, ID_Objectif, Montant transité, Date de l'opération.
Interactions avec les autres modules
•	Module 1 (Dashboard) : Fournit la valeur cumulée de toutes les poches d'épargne pour alimenter la section "Épargne %" du graphique de répartition patrimoniale.
•	Module 2 (Comptes) : Si l'utilisateur le configure, l'alimentation d'une poche d'épargne peut être liée graphiquement à une baisse équivalente sur le solde d'une des cartes bancaires (virement interne).
MODULE 5 : Suivi des Investissements (Portefeuille)
Objectif et rôle dans l'application
Ce module s'adresse au suivi des actifs volatils ou bloqués (Bourse, Crypto, Plan d'Épargne Entreprise, etc.). Son rôle n'est pas de faire du trading en direct, mais d'offrir un outil de valorisation périodique pour mesurer l'évolution de la valeur nette des investissements et calculer les performances réelles du capital injecté.
Fonctionnalités regroupées
•	Registre des lignes d'investissement (par support ou plateforme).
•	Historique des injections de capital (le "Capital Investi").
•	Calculateur automatique de performance brute (plus-value/moins-value en euros et en pourcentage).
•	Code couleur dynamique pour l'affichage des performances (Vert si positif, Rouge si négatif).
Déroulement du parcours utilisateur étape par étape
1.	L'utilisateur navigue vers l'onglet "Patrimoine" et descend sur la section "Investissements".
2.	Il visualise un tableau contenant ses différents placements, le capital qu'il a injecté de sa poche, la dernière valeur estimée qu'il a renseignée, et la performance calculée.
3.	Une fois par semaine ou par mois, il consulte la valeur réelle de ses placements sur ses plateformes externes.
4.	Il clique sur "Mettre à jour la valeur" sur la ligne correspondante dans FinanSmart, saisit la nouvelle valeur totale et valide.
5.	Le backend recalcule instantanément la plus-value latente et applique la couleur adéquate (ex: +12.5% affiché en vert fluo sur fond sombre).
Actions que l'utilisateur peut effectuer
•	Déclarer un nouveau support d'investissement.
•	Enregistrer une nouvelle injection de fonds (achat d'actifs).
•	Mettre à jour la valeur liquidative actuelle d'un placement.
Données manipulées
•	placement : ID, Type d'actif (Actions, Crypto, Immo, etc.), Nom du support, Capital_Total_Investi, Valeur_Actuelle_Estimee, Date_Derniere_Valorisation.
Interactions avec les autres modules
•	Module 1 (Dashboard) : Transmet la Valeur_Actuelle_Estimee globale cumulée de tous les placements pour alimenter la section "Investissements %" du graphique de répartition patrimoniale.
•	Module 6 (Assistant) : Permet à l'assistant d'analyser si le portefeuille d'investissement est sous-performant ou si la part d'investissements est trop ou pas assez importante par rapport aux liquidités disponibles.
MODULE 6 : Moteur de Conseils & Analyse ("L'Assistant Intelligent")
Objectif et rôle dans l'application
L'Assistant Intelligent agit comme un conseiller financier automatisé, bienveillant et totalement privé. Son rôle est de valoriser la donnée brute saisie par l'utilisateur en y appliquant un moteur de règles logiques codé en Python. Il transforme l'application d'un simple tableau de suivi passif en un outil d'aide à la décision proactif.
Fonctionnalités regroupées
•	Analyseur de structure budgétaire (vérification du ratio des charges fixes).
•	Détecteur de déséquilibre de trésorerie inter-comptes.
•	Alerte de stagnation des liquidités (détection des capitaux dormants).
•	Générateur de notifications contextuelles textuelles sur le Dashboard.
Déroulement du parcours utilisateur étape par étape
1.	Le moteur de règles s'exécute silencieusement en tâche de fond à chaque fois que l'utilisateur charge le Dashboard ou modifie une donnée dans l'application.
2.	Le script Python balaie les tables de la base de données SQLite et applique les règles logiques définies.
3.	Si une règle est enfreinte (ex: le compte de la Banque A est à 45 € alors que celui de la Banque B est à 4000 €), le moteur génère une entrée d'avertissement.
4.	L'utilisateur ouvre son Dashboard et voit apparaître une carte d'alerte orange : "Le compte Banque A approche de 0 €. Pensez à faire un virement interne depuis Banque B pour éviter les frais."
5.	Une fois le virement effectué et les soldes ajustés dans le Module 2, l'alerte disparaît d'elle-même au rechargement suivant.
Actions que l'utilisateur peut effectuer
•	Prendre connaissance des recommandations affichées.
•	Cliquer sur une recommandation pour être redirigé vers l'écran permettant de résoudre le problème (ex: cliquer sur l'alerte d'ajustement des comptes redirige vers le formulaire de virement/mouvement du Module 2).
Données manipulées
•	En entrée (Données analysées) : L'intégralité des tables SQLite (compte, mouvement, abonnement, objectif_epargne, placement).
•	En sortie (Données produites) : Un objet JSON ou une liste d'alertes contenant un niveau de sévérité (Info, Warning, Succès), une icône associée, et le texte du conseil formaté.
Interactions avec les autres modules
•	Tous les modules : Ce module est transverse. Il extrait ses données de tous les autres modules de l'application.
•	Module 1 (Dashboard) : C'est le récepteur exclusif des messages produits par l'assistant. Les conseils sont injectés dynamiquement dans le composant d'affichage dédié sur l'écran d'accueil.

ModuleTable SQLite ImpactéeVue FrontendType d'opération HTTPDéclenchement HTMXM1 : DashboardAucune (Lecture seule)index.html (Onglet 1)GET /api/v1/dashboardAu chargement initial de la pageM2 : Comptescompte, mouvementmouvements.html (Onglet 2)POST /api/v1/mouvementsPUT /api/v1/comptes/soldehx-post à la soumission du formulaireM3 : Abonnementsabonnementmouvements.html (Onglet 2)POST /api/v1/abonnementshx-target rafraîchit la liste chronologiqueM4 : Épargneobjectif_epargnepatrimoine.html (Onglet 3)PUT /api/v1/epargne/updateMet à jour la largeur de la progress bar CSSM5 : Investissementsplacementpatrimoine.html (Onglet 3)PUT /api/v1/investissements/valueRecalcule la couleur du badge de performanceM6 : AssistantAucune (Logique pure)index.html (Onglet 1)GET /api/v1/assistant/alertsInclus dans le payload de rafraîchissement du Dashboard

Voici la liste de la stack technique ultra-légère retenue pour FinanSmart :
Backend : Python avec FastAPI (rapide, asynchrone et très sobre en RAM).
Frontend : HTML5 + Tailwind CSS (design moderne) + HTMX (pour rendre la page dynamique en AJAX sans framework JavaScript lourd).
Base de Données : SQLite (un simple fichier local, zéro configuration, performance maximale pour un utilisateur unique).
Infrastructure / OS : Machine Virtuelle (VM) Debian (hébergement local).