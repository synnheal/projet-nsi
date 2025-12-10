"""
Module planning - Génération et organisation du planning hebdomadaire.

Ce module permet :
- La répartition des heures sur les jours disponibles
- La construction de créneaux structurés (matin/après-midi/soir)
- La génération d'un calendrier hebdomadaire
"""

from typing import Optional

# Constantes pour les jours de la semaine
JOURS_SEMAINE = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

# Créneaux horaires disponibles
CRENEAUX = {
    "matin": {"debut": "08:00", "fin": "12:00", "max_heures": 4},
    "apres_midi": {"debut": "14:00", "fin": "18:00", "max_heures": 4},
    "soir": {"debut": "19:00", "fin": "22:00", "max_heures": 3}
}


def creer_planning_vide() -> dict:
    """
    Crée un planning hebdomadaire vide.

    Returns:
        Dictionnaire représentant un planning vide
    """
    return {jour: [] for jour in JOURS_SEMAINE}


def repartir_heures(heures_totales: float, jours_disponibles: list,
                    heures_par_jour: Optional[dict] = None) -> dict:
    """
    Répartit les heures sur les jours disponibles.

    Args:
        heures_totales: Nombre total d'heures à répartir par semaine
        jours_disponibles: Liste des jours disponibles
        heures_par_jour: Dictionnaire optionnel des heures max par jour

    Returns:
        Dictionnaire avec les heures réparties par jour
    """
    if not jours_disponibles:
        return {}

    repartition = {}

    if heures_par_jour:
        # Répartition pondérée selon les disponibilités
        total_dispo = sum(heures_par_jour.get(jour, 0) for jour in jours_disponibles)
        if total_dispo == 0:
            return {jour: 0 for jour in jours_disponibles}

        heures_restantes = heures_totales
        for jour in jours_disponibles:
            dispo = heures_par_jour.get(jour, 0)
            proportion = dispo / total_dispo
            heures_jour = min(round(heures_totales * proportion, 1), dispo)
            repartition[jour] = heures_jour
            heures_restantes -= heures_jour
    else:
        # Répartition équitable
        heures_par_jour_equitable = round(heures_totales / len(jours_disponibles), 1)
        repartition = {jour: heures_par_jour_equitable for jour in jours_disponibles}

    return repartition


def generer_creneaux(heures: float) -> list:
    """
    Génère les créneaux horaires pour un nombre d'heures donné.

    Args:
        heures: Nombre d'heures à placer

    Returns:
        Liste des créneaux avec leurs durées
    """
    creneaux_jour = []
    heures_restantes = heures

    # Priorité : matin, puis après-midi, puis soir
    ordre_creneaux = ["matin", "apres_midi", "soir"]

    for creneau in ordre_creneaux:
        if heures_restantes <= 0:
            break

        max_heures = CRENEAUX[creneau]["max_heures"]
        heures_creneau = min(heures_restantes, max_heures)

        if heures_creneau > 0:
            creneaux_jour.append({
                "periode": creneau,
                "duree": heures_creneau,
                "debut": CRENEAUX[creneau]["debut"],
                "fin": calculer_fin(CRENEAUX[creneau]["debut"], heures_creneau)
            })
            heures_restantes -= heures_creneau

    return creneaux_jour


def calculer_fin(debut: str, duree: float) -> str:
    """
    Calcule l'heure de fin à partir de l'heure de début et de la durée.

    Args:
        debut: Heure de début (format "HH:MM")
        duree: Durée en heures

    Returns:
        Heure de fin (format "HH:MM")
    """
    heures, minutes = map(int, debut.split(":"))
    total_minutes = heures * 60 + minutes + int(duree * 60)
    heures_fin = total_minutes // 60
    minutes_fin = total_minutes % 60
    return f"{heures_fin:02d}:{minutes_fin:02d}"


def generer_planning(jours_disponibles: list, heures_totales: float,
                     heures_par_jour: Optional[dict] = None) -> dict:
    """
    Génère un planning hebdomadaire complet.

    Args:
        jours_disponibles: Liste des jours disponibles
        heures_totales: Nombre total d'heures par semaine
        heures_par_jour: Dictionnaire optionnel des heures max par jour

    Returns:
        Dictionnaire représentant le planning complet
    """
    # Valider les jours
    jours_valides = [j.lower() for j in jours_disponibles if j.lower() in JOURS_SEMAINE]

    if not jours_valides:
        return creer_planning_vide()

    # Répartir les heures
    repartition = repartir_heures(heures_totales, jours_valides, heures_par_jour)

    # Générer le planning avec créneaux
    planning = creer_planning_vide()
    for jour, heures in repartition.items():
        if heures > 0:
            planning[jour] = generer_creneaux(heures)

    return planning


def calculer_total_heures(planning: dict) -> float:
    """
    Calcule le total d'heures dans un planning.

    Args:
        planning: Dictionnaire du planning

    Returns:
        Total d'heures
    """
    total = 0
    for jour, creneaux in planning.items():
        for creneau in creneaux:
            total += creneau.get("duree", 0)
    return total


def formater_planning(planning: dict) -> str:
    """
    Formate le planning pour affichage console.

    Args:
        planning: Dictionnaire du planning

    Returns:
        Chaîne formatée pour affichage
    """
    lignes = []
    lignes.append("\n" + "=" * 50)
    lignes.append("  PLANNING HEBDOMADAIRE")
    lignes.append("=" * 50)

    jours_avec_creneaux = False

    for jour in JOURS_SEMAINE:
        creneaux = planning.get(jour, [])
        if creneaux:
            jours_avec_creneaux = True
            jour_affiche = jour.capitalize()
            lignes.append(f"\n  {jour_affiche}:")
            for creneau in creneaux:
                periode = creneau["periode"].replace("_", "-").capitalize()
                lignes.append(f"    • {periode}: {creneau['duree']}h ({creneau['debut']} - {creneau['fin']})")

    if not jours_avec_creneaux:
        lignes.append("\n  Aucun créneau défini.")

    total = calculer_total_heures(planning)
    lignes.append(f"\n  Total: {total}h / semaine")
    lignes.append("=" * 50 + "\n")

    return "\n".join(lignes)


def formater_periode(periode: str) -> str:
    """
    Formate le nom d'une période pour l'affichage.

    Args:
        periode: Nom de la période (matin, apres_midi, soir)

    Returns:
        Nom formaté
    """
    periodes = {
        "matin": "Matin",
        "apres_midi": "Après-midi",
        "soir": "Soir"
    }
    return periodes.get(periode, periode.capitalize())


def valider_planning(planning: dict) -> tuple:
    """
    Valide un planning et retourne les éventuelles erreurs.

    Args:
        planning: Dictionnaire du planning

    Returns:
        Tuple (est_valide, liste_erreurs)
    """
    erreurs = []

    for jour, creneaux in planning.items():
        if jour not in JOURS_SEMAINE:
            erreurs.append(f"Jour invalide: {jour}")
            continue

        total_jour = sum(c.get("duree", 0) for c in creneaux)
        if total_jour > 11:  # Max théorique (4+4+3)
            erreurs.append(f"{jour}: plus de 11h planifiées ({total_jour}h)")

    return (len(erreurs) == 0, erreurs)
