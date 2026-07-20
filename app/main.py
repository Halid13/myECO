import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import time
import logging

from app.database import init_db
from app.routers import dashboard, comptes, abonnements, epargne, investissements, assistant, onboarding, auth, admin
from app.services.prelevements import executer_prelevements

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FinanSmart", version="1.0.0")

# Session de connexion (cookie signé, longue durée — pas de refresh token,
# pas d'expiration sophistiquée : voir CLAUDE.md, app auto-hébergée entre proches).
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-a-changer-en-production")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=60 * 60 * 24 * 365)

# Fichiers statiques (CSS Tailwind)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates Jinja2
templates = Jinja2Templates(directory="app/templates")

# === Configuration du Scheduler ===
scheduler = BackgroundScheduler()

def start_scheduler():
    """Démarrer le scheduler au démarrage de l'application."""
    scheduler.add_job(
        executer_prelevements,
        'cron',
        hour=0,  # Exécuter chaque jour à minuit
        minute=1,
        id='prelevements_quotidiens',
        name='Prélèvements automatiques d\'abonnements'
    )
    scheduler.start()
    logger.info("✓ Scheduler des prélèvements initialisé (exécution quotidienne à 00:01)")

def shutdown_scheduler():
    """Arrêter le scheduler à l'arrêt de l'application."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("✓ Scheduler arrêté")

# Enregistrer les événements de cycle de vie
@app.on_event("startup")
def on_startup():
    init_db()
    start_scheduler()

@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()

# Inclusion des routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(onboarding.router)
app.include_router(dashboard.router)
app.include_router(comptes.router)
app.include_router(abonnements.router)
app.include_router(epargne.router)
app.include_router(investissements.router)
app.include_router(assistant.router)
