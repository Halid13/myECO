from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.routers import dashboard, comptes, abonnements, epargne, investissements, assistant

app = FastAPI(title="FinanSmart", version="1.0.0")

# Fichiers statiques (CSS Tailwind)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates Jinja2
templates = Jinja2Templates(directory="app/templates")

# Inclusion des routers
app.include_router(dashboard.router)
app.include_router(comptes.router)
app.include_router(abonnements.router)
app.include_router(epargne.router)
app.include_router(investissements.router)
app.include_router(assistant.router)


@app.on_event("startup")
def on_startup():
    """Initialise la base de données au démarrage."""
    init_db()
