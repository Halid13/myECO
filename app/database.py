from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./data/finansmart.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dépendance FastAPI : fournit une session DB et la ferme après usage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crée toutes les tables si elles n'existent pas encore."""
    import app.models  # noqa : importe tous les modèles pour les enregistrer
    Base.metadata.create_all(bind=engine)
    _appliquer_migrations_legeres()


def _appliquer_migrations_legeres():
    """ALTER TABLE défensif : create_all() ne modifie jamais les tables déjà existantes,
    donc l'ajout d'une colonne à un modèle existant ne se propage pas seul à la DB."""
    inspector = inspect(engine)
    colonnes_attendues = {
        "objectif_epargne": [
            ("id_compte", "INTEGER REFERENCES compte(id)"),
            ("id_utilisateur", "INTEGER REFERENCES utilisateur(id)"),
        ],
        "placement": [
            ("date_investissement", "DATETIME"),
            ("description", "TEXT"),
            ("id_utilisateur", "INTEGER REFERENCES utilisateur(id)"),
        ],
        "compte": [("id_utilisateur", "INTEGER REFERENCES utilisateur(id)")],
        "recommandation": [("id_utilisateur", "INTEGER REFERENCES utilisateur(id)")],
    }
    with engine.begin() as conn:
        for table, colonnes in colonnes_attendues.items():
            if table not in inspector.get_table_names():
                continue
            existantes = {c["name"] for c in inspector.get_columns(table)}
            for nom, ddl_type in colonnes:
                if nom not in existantes:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {nom} {ddl_type}"))
