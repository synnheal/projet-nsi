"""
Module finance - Traitement et simulation des données financières.

Ce module permet :
- Le calcul de l'épargne mensuelle
- La génération d'un tableau mensuel avec cumul d'épargne
- La détection du moment où l'objectif est atteint
- L'identification des cas impossibles (épargne < 0)
"""

from typing import Optional


def calculer_epargne_mensuelle(revenus: float, depenses_fixes: float, depenses_variables: float) -> float:
    """
    Calcule l'épargne mensuelle disponible.

    Args:
        revenus: Revenus mensuels
        depenses_fixes: Dépenses fixes mensuelles
        depenses_variables: Dépenses variables mensuelles

    Returns:
        Montant de l'épargne mensuelle (peut être négatif)
    """
    return revenus - depenses_fixes - depenses_variables


def simuler_objectif(revenus: float, depenses_fixes: float, depenses_variables: float,
                     objectif: float, duree_mois: int = 24) -> dict:
    """
    Simule l'atteinte d'un objectif financier sur plusieurs mois.

    Args:
        revenus: Revenus mensuels
        depenses_fixes: Dépenses fixes mensuelles
        depenses_variables: Dépenses variables mensuelles
        objectif: Montant de l'objectif à atteindre
        duree_mois: Durée de la simulation en mois

    Returns:
        Dictionnaire contenant les résultats de la simulation
    """
    epargne_mensuelle = calculer_epargne_mensuelle(revenus, depenses_fixes, depenses_variables)

    # Vérification des cas impossibles
    if epargne_mensuelle <= 0:
        return {
            "possible": False,
            "epargne_mensuelle": epargne_mensuelle,
            "message": "Impossible d'épargner : les dépenses dépassent les revenus.",
            "tableau_mensuel": [],
            "total_epargne": 0,
            "mois_objectif_atteint": None
        }

    # Génération du tableau mensuel
    tableau_mensuel = []
    cumul = 0
    mois_objectif_atteint = None

    for mois in range(1, duree_mois + 1):
        cumul += epargne_mensuelle
        objectif_atteint = cumul >= objectif

        if objectif_atteint and mois_objectif_atteint is None:
            mois_objectif_atteint = mois

        tableau_mensuel.append({
            "mois": mois,
            "revenu": revenus,
            "depenses": depenses_fixes + depenses_variables,
            "economie": epargne_mensuelle,
            "cumul": round(cumul, 2),
            "objectif_atteint": objectif_atteint
        })

    # Calcul du nombre de mois nécessaires (théorique)
    mois_necessaires = None
    if epargne_mensuelle > 0:
        import math
        mois_necessaires = math.ceil(objectif / epargne_mensuelle)

    return {
        "possible": True,
        "epargne_mensuelle": round(epargne_mensuelle, 2),
        "message": generer_message_resultat(mois_objectif_atteint, mois_necessaires, objectif, duree_mois),
        "tableau_mensuel": tableau_mensuel,
        "total_epargne": round(cumul, 2),
        "mois_objectif_atteint": mois_objectif_atteint,
        "mois_necessaires": mois_necessaires
    }


def generer_message_resultat(mois_atteint: Optional[int], mois_necessaires: Optional[int],
                              objectif: float, duree_simulation: int) -> str:
    """
    Génère un message descriptif du résultat de la simulation.

    Args:
        mois_atteint: Mois où l'objectif est atteint (ou None)
        mois_necessaires: Nombre de mois théoriquement nécessaires
        objectif: Montant de l'objectif
        duree_simulation: Durée de la simulation en mois

    Returns:
        Message descriptif
    """
    if mois_atteint:
        return f"Objectif de {objectif}€ atteint au mois {mois_atteint}."
    elif mois_necessaires and mois_necessaires > duree_simulation:
        return f"Objectif de {objectif}€ atteignable en {mois_necessaires} mois (au-delà de la simulation de {duree_simulation} mois)."
    else:
        return f"Simulation terminée. Objectif de {objectif}€ non atteint dans la période."


def analyser_finances(projet: dict) -> dict:
    """
    Analyse les finances d'un projet et retourne la simulation.

    Args:
        projet: Dictionnaire du projet

    Returns:
        Résultats de la simulation
    """
    finances = projet.get("finances", {})

    return simuler_objectif(
        revenus=finances.get("revenus", 0),
        depenses_fixes=finances.get("depenses_fixes", 0),
        depenses_variables=finances.get("depenses_variables", 0),
        objectif=finances.get("objectif", 0),
        duree_mois=finances.get("duree_mois", 12)
    )


def formater_tableau_simulation(simulation: dict) -> str:
    """
    Formate le tableau de simulation pour affichage console.

    Args:
        simulation: Dictionnaire de la simulation

    Returns:
        Chaîne formatée pour affichage
    """
    if not simulation.get("possible"):
        return f"\n⚠️  {simulation.get('message', 'Simulation impossible')}\n"

    lignes = []
    lignes.append("\n" + "=" * 70)
    lignes.append(f"  Épargne mensuelle : {simulation['epargne_mensuelle']}€")
    lignes.append("=" * 70)
    lignes.append(f"{'Mois':<6} {'Revenu':<12} {'Dépenses':<12} {'Économie':<12} {'Cumul':<12} {'Statut':<10}")
    lignes.append("-" * 70)

    for ligne in simulation.get("tableau_mensuel", []):
        statut = "✓" if ligne["objectif_atteint"] else ""
        lignes.append(
            f"{ligne['mois']:<6} {ligne['revenu']:<12.2f} {ligne['depenses']:<12.2f} "
            f"{ligne['economie']:<12.2f} {ligne['cumul']:<12.2f} {statut:<10}"
        )

    lignes.append("-" * 70)
    lignes.append(f"  {simulation.get('message', '')}")
    lignes.append("=" * 70 + "\n")

    return "\n".join(lignes)


def calculer_progression(simulation: dict, objectif: float) -> float:
    """
    Calcule le pourcentage de progression vers l'objectif.

    Args:
        simulation: Dictionnaire de la simulation
        objectif: Montant de l'objectif

    Returns:
        Pourcentage de progression (0.0 à 1.0)
    """
    if not simulation or objectif <= 0:
        return 0.0

    total = simulation.get("total_epargne", 0)
    progression = min(total / objectif, 1.0)
    return round(progression, 2)
