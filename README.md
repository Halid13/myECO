# FinanSmart — Application locale de gestion financière personnelle

## Stack technique
- **Backend** : Python + FastAPI
- **Frontend** : HTML5 + Tailwind CSS + HTMX
- **Base de données** : SQLite
- **Infrastructure** : VM Debian (auto-hébergé)

## Lancer l'application

```bash
# Installer les dépendances
pip install -r requirements.txt

# Démarrer le serveur
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

L'application est ensuite accessible sur `http://<IP_VM>:8000`

## Structure du projet

```
finansmart/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── database.py          # Connexion SQLite + SQLAlchemy
│   ├── models/              # Modèles ORM (tables SQLite)
│   ├── routers/             # Routes API par module
│   ├── schemas/             # Schémas Pydantic (validation)
│   ├── services/            # Logique métier (moteur assistant)
│   └── templates/           # Templates HTML (Jinja2 + HTMX)
├── static/
│   └── css/                 # Feuilles de style Tailwind
├── data/                    # Fichier SQLite (gitignored)
└── requirements.txt
```

cd ~/myECO && source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Arrêtez le serveur uvicorn en cours (Ctrl+C dans le terminal où il tourne).

Supprimez complètement le fichier de base de données :


cd ~/myECO
rm data/finansmart.db
Relancez le serveur :

source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Ouvrez http://100.113.39.5:8000/ dans votre navigateur.

Lancer python -m app.scripts.backfill_utilisateur (te demandera un mot de passe pour "admin").
Lancer python -m app.scripts.creer_utilisateur autant de fois que de personnes à ajouter.
python -m app.scripts.supprimer_utilisateur
