"""
Module main - Point d'entrée, navigation et logique centrale.

Ce module :
- Charge les projets existants via le module storage
- Gère le menu principal en console
- Orchestre les appels aux modules finance, planning et export_html
- Permet de créer, modifier ou supprimer des projets
"""

import os
import sys

from . import storage
from . import finance
from . import planning
from . import export_html


def effacer_ecran():
    """Efface l'écran de la console."""
    os.system('cls' if os.name == 'nt' else 'clear')


def afficher_titre():
    """Affiche le titre de l'application."""
    print("\n" + "=" * 50)
    print("       PROJECTFLOW - Gestion de Projets")
    print("=" * 50)


def afficher_menu_principal():
    """Affiche le menu principal."""
    print("\n  MENU PRINCIPAL")
    print("  " + "-" * 30)
    print("  1. Nouveau projet")
    print("  2. Ouvrir un projet")
    print("  3. Supprimer un projet")
    print("  4. Quitter")
    print()


def saisir_choix(message: str, choix_valides: list) -> str:
    """
    Demande à l'utilisateur de saisir un choix.

    Args:
        message: Message à afficher
        choix_valides: Liste des choix valides

    Returns:
        Choix de l'utilisateur
    """
    while True:
        reponse = input(message).strip()
        if reponse in choix_valides:
            return reponse
        print(f"  Choix invalide. Options: {', '.join(choix_valides)}")


def saisir_nombre(message: str, minimum: float = 0, maximum: float = None) -> float:
    """
    Demande à l'utilisateur de saisir un nombre.

    Args:
        message: Message à afficher
        minimum: Valeur minimale acceptée
        maximum: Valeur maximale acceptée (optionnel)

    Returns:
        Nombre saisi
    """
    while True:
        try:
            valeur = float(input(message).strip().replace(",", "."))
            if valeur < minimum:
                print(f"  La valeur doit être >= {minimum}")
                continue
            if maximum is not None and valeur > maximum:
                print(f"  La valeur doit être <= {maximum}")
                continue
            return valeur
        except ValueError:
            print("  Veuillez entrer un nombre valide.")


def saisir_entier(message: str, minimum: int = 0, maximum: int = None) -> int:
    """
    Demande à l'utilisateur de saisir un entier.

    Args:
        message: Message à afficher
        minimum: Valeur minimale acceptée
        maximum: Valeur maximale acceptée (optionnel)

    Returns:
        Entier saisi
    """
    while True:
        try:
            valeur = int(input(message).strip())
            if valeur < minimum:
                print(f"  La valeur doit être >= {minimum}")
                continue
            if maximum is not None and valeur > maximum:
                print(f"  La valeur doit être <= {maximum}")
                continue
            return valeur
        except ValueError:
            print("  Veuillez entrer un nombre entier valide.")


def creer_nouveau_projet():
    """Crée un nouveau projet avec les informations saisies."""
    effacer_ecran()
    print("\n" + "=" * 50)
    print("  NOUVEAU PROJET")
    print("=" * 50)

    nom = input("\n  Nom du projet: ").strip()
    if not nom:
        print("  Nom invalide. Annulation.")
        return None

    projet = storage.creer_projet(nom)

    # Saisie des données financières
    print("\n  --- Données financières ---")
    projet["finances"]["revenus"] = saisir_nombre("  Revenus mensuels (€): ")
    projet["finances"]["depenses_fixes"] = saisir_nombre("  Dépenses fixes (€): ")
    projet["finances"]["depenses_variables"] = saisir_nombre("  Dépenses variables (€): ")
    projet["finances"]["objectif"] = saisir_nombre("  Objectif à atteindre (€): ", minimum=1)
    projet["finances"]["duree_mois"] = saisir_entier("  Durée de simulation (mois): ", minimum=1, maximum=120)

    # Saisie du planning
    print("\n  --- Planning hebdomadaire ---")
    if saisir_choix("  Configurer le planning maintenant? (o/n): ", ["o", "n"]) == "o":
        projet["planning"] = saisir_planning()
    else:
        projet["planning"] = planning.creer_planning_vide()

    # Exécuter la simulation
    projet["simulation"] = finance.analyser_finances(projet)
    projet["progression"] = finance.calculer_progression(
        projet["simulation"],
        projet["finances"]["objectif"]
    )

    # Sauvegarder
    if storage.ajouter_projet(projet):
        print("\n  ✓ Projet créé et sauvegardé avec succès!")
        return projet
    else:
        print("\n  ✗ Erreur lors de la sauvegarde.")
        return None


def saisir_planning() -> dict:
    """
    Permet à l'utilisateur de configurer son planning.

    Returns:
        Dictionnaire du planning
    """
    jours_dispo = []
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

    print("\n  Quels jours êtes-vous disponible?")
    for i, jour in enumerate(jours, 1):
        print(f"  {i}. {jour.capitalize()}")

    print("\n  Entrez les numéros des jours (ex: 1,3,5 pour Lun,Mer,Ven)")
    choix = input("  Votre choix: ").strip()

    try:
        indices = [int(x.strip()) - 1 for x in choix.split(",")]
        jours_dispo = [jours[i] for i in indices if 0 <= i < len(jours)]
    except (ValueError, IndexError):
        print("  Saisie invalide, planning vide créé.")
        return planning.creer_planning_vide()

    if not jours_dispo:
        return planning.creer_planning_vide()

    heures_totales = saisir_nombre(
        f"\n  Heures totales par semaine à consacrer à l'objectif: ",
        minimum=1,
        maximum=77  # Max théorique (11h * 7 jours)
    )

    return planning.generer_planning(jours_dispo, heures_totales)


def afficher_liste_projets():
    """Affiche la liste des projets disponibles."""
    projets = storage.lister_projets()

    if not projets:
        print("\n  Aucun projet enregistré.")
        return []

    print("\n  PROJETS DISPONIBLES")
    print("  " + "-" * 40)
    for i, projet in enumerate(projets, 1):
        progression = projet.get("progression", 0) * 100
        print(f"  {i}. {projet['nom']} ({progression:.0f}%) - {projet['date_creation']}")

    return projets


def selectionner_projet():
    """
    Permet à l'utilisateur de sélectionner un projet.

    Returns:
        Le projet sélectionné ou None
    """
    projets = afficher_liste_projets()
    if not projets:
        return None

    try:
        choix = saisir_entier("\n  Numéro du projet (0 pour annuler): ", minimum=0, maximum=len(projets))
        if choix == 0:
            return None
        return projets[choix - 1]
    except (ValueError, IndexError):
        print("  Choix invalide.")
        return None


def afficher_menu_projet(projet: dict):
    """Affiche le menu d'un projet."""
    print(f"\n  PROJET: {projet['nom']}")
    print("  " + "-" * 30)
    print("  1. Voir la simulation financière")
    print("  2. Voir le planning")
    print("  3. Modifier les finances")
    print("  4. Modifier le planning")
    print("  5. Exporter en HTML")
    print("  6. Dupliquer le projet")
    print("  7. Renommer le projet")
    print("  8. Retour au menu principal")
    print()


def gerer_projet(projet: dict):
    """
    Gère les interactions avec un projet.

    Args:
        projet: Le projet à gérer
    """
    while True:
        effacer_ecran()
        afficher_titre()
        afficher_menu_projet(projet)

        choix = saisir_choix("  Votre choix: ", ["1", "2", "3", "4", "5", "6", "7", "8"])

        if choix == "1":
            # Voir simulation
            effacer_ecran()
            print(finance.formater_tableau_simulation(projet.get("simulation", {})))
            input("\n  Appuyez sur Entrée pour continuer...")

        elif choix == "2":
            # Voir planning
            effacer_ecran()
            print(planning.formater_planning(projet.get("planning", {})))
            input("\n  Appuyez sur Entrée pour continuer...")

        elif choix == "3":
            # Modifier finances
            modifier_finances(projet)

        elif choix == "4":
            # Modifier planning
            modifier_planning(projet)

        elif choix == "5":
            # Exporter HTML
            effacer_ecran()
            try:
                chemin = export_html.exporter_rapport(projet)
                print(f"\n  ✓ Rapport exporté: {chemin}")
            except Exception as e:
                print(f"\n  ✗ Erreur lors de l'export: {e}")
            input("\n  Appuyez sur Entrée pour continuer...")

        elif choix == "6":
            # Dupliquer
            nouveau_nom = input("\n  Nom du nouveau projet: ").strip()
            if nouveau_nom:
                nouveau = storage.dupliquer_projet(projet["id"], nouveau_nom)
                if nouveau:
                    print(f"\n  ✓ Projet dupliqué: {nouveau_nom}")
                else:
                    print("\n  ✗ Erreur lors de la duplication.")
            input("\n  Appuyez sur Entrée pour continuer...")

        elif choix == "7":
            # Renommer
            nouveau_nom = input("\n  Nouveau nom: ").strip()
            if nouveau_nom:
                if storage.renommer_projet(projet["id"], nouveau_nom):
                    projet["nom"] = nouveau_nom
                    print(f"\n  ✓ Projet renommé: {nouveau_nom}")
                else:
                    print("\n  ✗ Erreur lors du renommage.")
            input("\n  Appuyez sur Entrée pour continuer...")

        elif choix == "8":
            break


def modifier_finances(projet: dict):
    """
    Permet de modifier les données financières d'un projet.

    Args:
        projet: Le projet à modifier
    """
    effacer_ecran()
    print("\n  MODIFIER LES FINANCES")
    print("  " + "-" * 30)
    print("  (Appuyez sur Entrée pour garder la valeur actuelle)")

    finances = projet["finances"]

    # Revenus
    actuel = finances.get("revenus", 0)
    saisie = input(f"\n  Revenus mensuels [{actuel}€]: ").strip()
    if saisie:
        try:
            finances["revenus"] = float(saisie.replace(",", "."))
        except ValueError:
            pass

    # Dépenses fixes
    actuel = finances.get("depenses_fixes", 0)
    saisie = input(f"  Dépenses fixes [{actuel}€]: ").strip()
    if saisie:
        try:
            finances["depenses_fixes"] = float(saisie.replace(",", "."))
        except ValueError:
            pass

    # Dépenses variables
    actuel = finances.get("depenses_variables", 0)
    saisie = input(f"  Dépenses variables [{actuel}€]: ").strip()
    if saisie:
        try:
            finances["depenses_variables"] = float(saisie.replace(",", "."))
        except ValueError:
            pass

    # Objectif
    actuel = finances.get("objectif", 0)
    saisie = input(f"  Objectif [{actuel}€]: ").strip()
    if saisie:
        try:
            finances["objectif"] = float(saisie.replace(",", "."))
        except ValueError:
            pass

    # Durée
    actuel = finances.get("duree_mois", 12)
    saisie = input(f"  Durée de simulation [{actuel} mois]: ").strip()
    if saisie:
        try:
            finances["duree_mois"] = int(saisie)
        except ValueError:
            pass

    # Recalculer la simulation
    projet["simulation"] = finance.analyser_finances(projet)
    projet["progression"] = finance.calculer_progression(
        projet["simulation"],
        projet["finances"]["objectif"]
    )

    # Sauvegarder
    if storage.mettre_a_jour_projet(projet):
        print("\n  ✓ Modifications enregistrées.")
    else:
        print("\n  ✗ Erreur lors de la sauvegarde.")

    input("\n  Appuyez sur Entrée pour continuer...")


def modifier_planning(projet: dict):
    """
    Permet de modifier le planning d'un projet.

    Args:
        projet: Le projet à modifier
    """
    effacer_ecran()
    print("\n  MODIFIER LE PLANNING")
    print("  " + "-" * 30)

    projet["planning"] = saisir_planning()

    # Sauvegarder
    if storage.mettre_a_jour_projet(projet):
        print("\n  ✓ Planning mis à jour.")
    else:
        print("\n  ✗ Erreur lors de la sauvegarde.")

    input("\n  Appuyez sur Entrée pour continuer...")


def supprimer_projet_menu():
    """Menu de suppression d'un projet."""
    effacer_ecran()
    print("\n  SUPPRIMER UN PROJET")
    print("  " + "-" * 30)

    projet = selectionner_projet()
    if not projet:
        return

    confirmation = saisir_choix(
        f"\n  Supprimer '{projet['nom']}'? Cette action est irréversible. (o/n): ",
        ["o", "n"]
    )

    if confirmation == "o":
        if storage.supprimer_projet(projet["id"]):
            print(f"\n  ✓ Projet '{projet['nom']}' supprimé.")
        else:
            print("\n  ✗ Erreur lors de la suppression.")
    else:
        print("\n  Suppression annulée.")

    input("\n  Appuyez sur Entrée pour continuer...")


def menu_principal():
    """Boucle principale de l'application."""
    while True:
        effacer_ecran()
        afficher_titre()
        afficher_menu_principal()

        choix = saisir_choix("  Votre choix: ", ["1", "2", "3", "4"])

        if choix == "1":
            projet = creer_nouveau_projet()
            if projet:
                input("\n  Appuyez sur Entrée pour continuer...")
                gerer_projet(projet)

        elif choix == "2":
            effacer_ecran()
            print("\n  OUVRIR UN PROJET")
            print("  " + "-" * 30)
            projet = selectionner_projet()
            if projet:
                gerer_projet(projet)

        elif choix == "3":
            supprimer_projet_menu()

        elif choix == "4":
            effacer_ecran()
            print("\n  Merci d'avoir utilisé ProjectFlow!")
            print("  À bientôt!\n")
            sys.exit(0)


def main():
    """Point d'entrée de l'application."""
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n  Programme interrompu.")
        sys.exit(0)


if __name__ == "__main__":
    main()
