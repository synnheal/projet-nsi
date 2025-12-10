"""
Module storage - Gestion de la persistance et restauration des projets.

Ce module gère :
- L'enregistrement automatique des projets dans un fichier JSON
- Le chargement des projets au démarrage
- Les opérations : ajout, suppression, duplication, renommage
"""

import json
import os
import uuid
from datetime import datetime
from typing import Optional

# Chemin par défaut du fichier de sauvegarde
FICHIER_SAUVEGARDE = "projectflow_data.json"


def generer_id() -> str:
    """Génère un identifiant unique pour un projet."""
    return str(uuid.uuid4())[:8]


def creer_projet(nom: str) -> dict:
    """
    Crée un nouveau projet avec les valeurs par défaut.

    Args:
        nom: Nom du projet

    Returns:
        Dictionnaire représentant le projet
    """
    return {
        "id": generer_id(),
        "nom": nom,
        "date_creation": datetime.now().strftime("%Y-%m-%d"),
        "finances": {
            "revenus": 0,
            "depenses_fixes": 0,
            "depenses_variables": 0,
            "objectif": 0,
            "duree_mois": 12
        },
        "simulation": None,
        "planning": None,
        "progression": 0.0
    }


def charger_donnees(fichier: str = FICHIER_SAUVEGARDE) -> dict:
    """
    Charge les données depuis le fichier JSON.

    Args:
        fichier: Chemin du fichier de sauvegarde

    Returns:
        Dictionnaire contenant tous les projets et métadonnées
    """
    if not os.path.exists(fichier):
        return {
            "projets": [],
            "version": "1.0",
            "derniere_modification": None
        }

    try:
        with open(fichier, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {
            "projets": [],
            "version": "1.0",
            "derniere_modification": None
        }


def sauvegarder_donnees(donnees: dict, fichier: str = FICHIER_SAUVEGARDE) -> bool:
    """
    Sauvegarde les données dans le fichier JSON.

    Args:
        donnees: Dictionnaire des données à sauvegarder
        fichier: Chemin du fichier de sauvegarde

    Returns:
        True si succès, False sinon
    """
    try:
        donnees["derniere_modification"] = datetime.now().isoformat()
        with open(fichier, "w", encoding="utf-8") as f:
            json.dump(donnees, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def lister_projets(fichier: str = FICHIER_SAUVEGARDE) -> list:
    """
    Retourne la liste de tous les projets.

    Args:
        fichier: Chemin du fichier de sauvegarde

    Returns:
        Liste des projets
    """
    donnees = charger_donnees(fichier)
    return donnees.get("projets", [])


def obtenir_projet(projet_id: str, fichier: str = FICHIER_SAUVEGARDE) -> Optional[dict]:
    """
    Récupère un projet par son identifiant.

    Args:
        projet_id: Identifiant du projet
        fichier: Chemin du fichier de sauvegarde

    Returns:
        Le projet ou None si non trouvé
    """
    projets = lister_projets(fichier)
    for projet in projets:
        if projet["id"] == projet_id:
            return projet
    return None


def ajouter_projet(projet: dict, fichier: str = FICHIER_SAUVEGARDE) -> bool:
    """
    Ajoute un nouveau projet.

    Args:
        projet: Dictionnaire du projet à ajouter
        fichier: Chemin du fichier de sauvegarde

    Returns:
        True si succès, False sinon
    """
    donnees = charger_donnees(fichier)
    donnees["projets"].append(projet)
    return sauvegarder_donnees(donnees, fichier)


def mettre_a_jour_projet(projet: dict, fichier: str = FICHIER_SAUVEGARDE) -> bool:
    """
    Met à jour un projet existant.

    Args:
        projet: Dictionnaire du projet mis à jour
        fichier: Chemin du fichier de sauvegarde

    Returns:
        True si succès, False sinon
    """
    donnees = charger_donnees(fichier)
    for i, p in enumerate(donnees["projets"]):
        if p["id"] == projet["id"]:
            donnees["projets"][i] = projet
            return sauvegarder_donnees(donnees, fichier)
    return False


def supprimer_projet(projet_id: str, fichier: str = FICHIER_SAUVEGARDE) -> bool:
    """
    Supprime un projet par son identifiant.

    Args:
        projet_id: Identifiant du projet à supprimer
        fichier: Chemin du fichier de sauvegarde

    Returns:
        True si succès, False sinon
    """
    donnees = charger_donnees(fichier)
    projets_initiaux = len(donnees["projets"])
    donnees["projets"] = [p for p in donnees["projets"] if p["id"] != projet_id]

    if len(donnees["projets"]) < projets_initiaux:
        return sauvegarder_donnees(donnees, fichier)
    return False


def dupliquer_projet(projet_id: str, nouveau_nom: str, fichier: str = FICHIER_SAUVEGARDE) -> Optional[dict]:
    """
    Duplique un projet existant avec un nouveau nom.

    Args:
        projet_id: Identifiant du projet à dupliquer
        nouveau_nom: Nom du nouveau projet
        fichier: Chemin du fichier de sauvegarde

    Returns:
        Le nouveau projet ou None si échec
    """
    projet_original = obtenir_projet(projet_id, fichier)
    if not projet_original:
        return None

    nouveau_projet = projet_original.copy()
    nouveau_projet["id"] = generer_id()
    nouveau_projet["nom"] = nouveau_nom
    nouveau_projet["date_creation"] = datetime.now().strftime("%Y-%m-%d")

    # Copie profonde des données imbriquées
    if projet_original.get("finances"):
        nouveau_projet["finances"] = projet_original["finances"].copy()
    if projet_original.get("simulation"):
        nouveau_projet["simulation"] = projet_original["simulation"].copy()
    if projet_original.get("planning"):
        nouveau_projet["planning"] = projet_original["planning"].copy()

    if ajouter_projet(nouveau_projet, fichier):
        return nouveau_projet
    return None


def renommer_projet(projet_id: str, nouveau_nom: str, fichier: str = FICHIER_SAUVEGARDE) -> bool:
    """
    Renomme un projet existant.

    Args:
        projet_id: Identifiant du projet
        nouveau_nom: Nouveau nom du projet
        fichier: Chemin du fichier de sauvegarde

    Returns:
        True si succès, False sinon
    """
    projet = obtenir_projet(projet_id, fichier)
    if not projet:
        return False

    projet["nom"] = nouveau_nom
    return mettre_a_jour_projet(projet, fichier)
