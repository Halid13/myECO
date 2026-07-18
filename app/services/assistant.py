from sqlalchemy.orm import Session
from app.models.compte import Compte
from app.models.abonnement import Abonnement


def generer_alertes(db: Session) -> list[dict]:
    """
    Moteur de règles logiques — analyse les données et retourne
    une liste d'alertes contextuelles pour le Dashboard.

    Structure d'une alerte :
    {
        "niveau": "info" | "warning" | "success",
        "icone": str,
        "message": str,
        "lien": str | None   # URL de redirection optionnelle
    }
    """
    alertes = []

    # --- Règle 1 : Compte proche du découvert (solde < 100 €) ---
    comptes = db.query(Compte).all()
    for compte in comptes:
        if compte.solde < 100:
            alertes.append({
                "niveau": "warning",
                "icone": "⚠️",
                "message": f"Le compte {compte.nom_banque} est bas ({compte.solde:.2f} €). Pensez à effectuer un virement.",
                "lien": "/comptes/"
            })

    # --- Règle 2 : Ratio charges fixes / revenus (à compléter quand les revenus seront saisis) ---
    # TODO

    return alertes
