"""Règles métier du moteur de l'Assistant Intelligent (Module 6).

Chaque règle est une fonction pure `(ctx: dict) -> list[dict]` : elle reçoit le contexte
partagé construit par `services.assistant.construire_contexte` et retourne zéro ou plusieurs
recommandations candidates. Ajouter une règle = écrire une fonction ci-dessous et l'ajouter
à la liste REGLES — aucune autre modification n'est nécessaire (services/assistant.py et les
routes restent inchangés).

Chaque candidat a la forme :
{
    "type_regle": str,        # identifiant stable de la règle (clé de déduplication)
    "cle_contexte": str,      # "global" ou "compte:3", "objectif:5"... (dédup par instance)
    "niveau": "info" | "warning" | "success",
    "icone": str | None,      # optionnel, sinon déduit du niveau à l'affichage
    "titre": str,
    "message": str,
    "lien": str | None,
}
"""

SEUIL_CHARGES_RATIO = 0.40
SEUIL_COMPTE_FAIBLE = 100
SEUIL_COMPTE_SAIN = 500
MOIS_TAMPON_RECOMMANDE = 6
SEUIL_OBJECTIF_PROCHE_PCT = 90
SEUIL_PERFORMANCE_FAIBLE_PCT = -10
SEUIL_BAISSE_EPARGNE_PCT = -30
SEUIL_HAUSSE_DEPENSES_PCT = 30


def regle_comptes_desequilibres(ctx: dict) -> list[dict]:
    """Un compte bas alors qu'un autre a une trésorerie confortable → suggère un virement interne."""
    comptes = ctx["comptes"]
    comptes_sains = [c for c in comptes if c.solde > SEUIL_COMPTE_SAIN]
    candidats = []
    for compte in comptes:
        if compte.solde >= SEUIL_COMPTE_FAIBLE:
            continue
        riche = next((c for c in comptes_sains if c.id != compte.id), None)
        if riche:
            message = (
                f"Le compte {compte.nom_banque} approche de son seuil minimal ({compte.solde:.2f} €). "
                f"Un virement interne depuis {riche.nom_banque} ({riche.solde:.2f} €) permettrait "
                f"d'éviter un découvert ou des frais éventuels."
            )
        else:
            message = f"Le compte {compte.nom_banque} est bas ({compte.solde:.2f} €). Pensez à effectuer un virement."
        candidats.append({
            "type_regle": "compte_desequilibre",
            "cle_contexte": f"compte:{compte.id}",
            "niveau": "warning",
            "icone": None,
            "titre": "Solde bas",
            "message": message,
            "lien": "/comptes/",
        })
    return candidats


def regle_charges_fixes_elevees(ctx: dict) -> list[dict]:
    """Charges fixes > 40% des revenus du mois → cite les abonnements les plus coûteux."""
    revenus = ctx["revenus_mois"]
    charges = ctx["charges_mensuelles"]
    if revenus <= 0 or charges <= 0:
        return []
    ratio = charges / revenus
    if ratio <= SEUIL_CHARGES_RATIO:
        return []

    plus_chers = sorted(ctx["abonnements"], key=lambda a: a.montant, reverse=True)[:2]
    noms = " et ".join(a.libelle for a in plus_chers) if plus_chers else "vos abonnements"
    return [{
        "type_regle": "charges_fixes_elevees",
        "cle_contexte": "global",
        "niveau": "warning",
        "icone": None,
        "titre": "Charges fixes élevées",
        "message": (
            f"Vos charges fixes représentent {ratio * 100:.0f}% de vos revenus ce mois-ci. "
            f"Pensez à revoir certains abonnements, notamment {noms}, afin d'optimiser votre budget."
        ),
        "lien": "/abonnements/",
    }]


def regle_liquidites_dormantes(ctx: dict) -> list[dict]:
    """Liquidités très au-dessus du besoin de trésorerie courant → suggère de les faire fructifier.

    Adaptation : le cahier des charges parle de stabilité "depuis plusieurs mois", mais l'app ne
    conserve pas d'historique de solde dans le temps — le message reste donc honnête sur ce qu'on
    peut vraiment mesurer : le niveau actuel, pas une durée vérifiée.
    """
    charges = ctx["charges_mensuelles"]
    if charges <= 0:
        return []
    total_liquidites = sum(c.solde for c in ctx["comptes"])
    seuil = charges * MOIS_TAMPON_RECOMMANDE
    if total_liquidites <= seuil:
        return []
    surplus = total_liquidites - seuil
    return [{
        "type_regle": "liquidites_dormantes",
        "cle_contexte": "global",
        "niveau": "success",
        "icone": "sparkles",
        "titre": "Liquidités disponibles",
        "message": (
            f"Vous disposez de {total_liquidites:.0f} € de liquidités, largement au-dessus de votre "
            f"besoin de trésorerie courant (~{seuil:.0f} € pour {MOIS_TAMPON_RECOMMANDE} mois de charges). "
            f"Environ {surplus:.0f} € pourraient être orientés vers votre épargne ou vos investissements."
        ),
        "lien": "/patrimoine/",
    }]


def regle_objectif_proche(ctx: dict) -> list[dict]:
    """Objectif d'épargne entre 90% et 100% de progression → message motivant."""
    candidats = []
    for obj in ctx["objectifs"]:
        pct = (obj.montant_actuel / obj.montant_cible * 100) if obj.montant_cible else 0
        if SEUIL_OBJECTIF_PROCHE_PCT <= pct < 100:
            candidats.append({
                "type_regle": "objectif_proche",
                "cle_contexte": f"objectif:{obj.id}",
                "niveau": "success",
                "icone": "trophy",
                "titre": "Objectif bientôt atteint",
                "message": f"Votre objectif \"{obj.nom}\" est atteint à {pct:.0f}% ! Encore un petit effort.",
                "lien": "/patrimoine/",
            })
    return candidats


def regle_investissement_sous_performant(ctx: dict) -> list[dict]:
    """Placement en perte significative (≤ -10%) → signale la ligne concernée."""
    candidats = []
    for p in ctx["placements"]:
        if p.capital_investi <= 0:
            continue
        perf = (p.valeur_actuelle - p.capital_investi) / p.capital_investi * 100
        if perf <= SEUIL_PERFORMANCE_FAIBLE_PCT:
            candidats.append({
                "type_regle": "investissement_sous_performant",
                "cle_contexte": f"placement:{p.id}",
                "niveau": "warning",
                "icone": None,
                "titre": "Placement en perte",
                "message": (
                    f"Votre placement \"{p.nom_support}\" affiche une performance de {perf:.1f}%. "
                    f"Cela mérite peut-être un point d'attention."
                ),
                "lien": "/patrimoine/",
            })
    return candidats


def regle_taux_epargne_baisse(ctx: dict) -> list[dict]:
    """Effort d'épargne en forte baisse par rapport au mois précédent."""
    effort = ctx["effort_epargne"]
    if effort["mois_precedent"] <= 0:
        return []
    if effort["delta_pct"] > SEUIL_BAISSE_EPARGNE_PCT:
        return []
    return [{
        "type_regle": "taux_epargne_baisse",
        "cle_contexte": "global",
        "niveau": "info",
        "icone": None,
        "titre": "Effort d'épargne en baisse",
        "message": (
            f"Vous avez épargné {effort['mois']:.0f} € ce mois-ci, contre {effort['mois_precedent']:.0f} € "
            f"le mois dernier ({effort['delta_pct']:.0f}%). Gardez un œil sur votre rythme d'épargne."
        ),
        "lien": "/patrimoine/",
    }]


def regle_depenses_hausse(ctx: dict) -> list[dict]:
    """Dépenses du mois en forte hausse par rapport au mois précédent."""
    depenses = ctx["depenses_mois"]
    if depenses["mois_precedent"] <= 0:
        return []
    variation = (depenses["mois"] - depenses["mois_precedent"]) / depenses["mois_precedent"] * 100
    if variation < SEUIL_HAUSSE_DEPENSES_PCT:
        return []
    return [{
        "type_regle": "depenses_hausse",
        "cle_contexte": "global",
        "niveau": "info",
        "icone": None,
        "titre": "Dépenses en hausse",
        "message": (
            f"Vos dépenses ce mois-ci ({depenses['mois']:.0f} €) sont en hausse de {variation:.0f}% "
            f"par rapport au mois dernier ({depenses['mois_precedent']:.0f} €). Un coup d'œil à votre "
            f"historique de mouvements peut être utile."
        ),
        "lien": "/comptes/",
    }]


REGLES = [
    regle_comptes_desequilibres,
    regle_charges_fixes_elevees,
    regle_liquidites_dormantes,
    regle_objectif_proche,
    regle_investissement_sous_performant,
    regle_taux_epargne_baisse,
    regle_depenses_hausse,
]
