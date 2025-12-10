"""
Module achievements - Système de badges et gamification.

Ce module gère :
- Les badges et accomplissements
- Les streaks (séries consécutives)
- Les défis hebdomadaires
- Les statistiques de progression
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


# Définition des badges
BADGES = {
    # Premiers pas
    "premier_projet": {
        "id": "premier_projet",
        "nom": "Premiers Pas",
        "description": "Créer votre premier projet",
        "icone": "🎯",
        "categorie": "debutant",
        "points": 10
    },
    "premier_objectif": {
        "id": "premier_objectif",
        "nom": "Objectif Atteint",
        "description": "Atteindre votre premier objectif financier",
        "icone": "🏆",
        "categorie": "objectifs",
        "points": 50
    },
    "premier_export": {
        "id": "premier_export",
        "nom": "Documenté",
        "description": "Exporter votre premier rapport",
        "icone": "📄",
        "categorie": "debutant",
        "points": 10
    },

    # Épargne
    "epargne_100": {
        "id": "epargne_100",
        "nom": "Petit Épargnant",
        "description": "Épargner 100€ au total",
        "icone": "💰",
        "categorie": "epargne",
        "points": 20
    },
    "epargne_1000": {
        "id": "epargne_1000",
        "nom": "Épargnant Confirmé",
        "description": "Épargner 1 000€ au total",
        "icone": "💎",
        "categorie": "epargne",
        "points": 50
    },
    "epargne_5000": {
        "id": "epargne_5000",
        "nom": "Maître Épargnant",
        "description": "Épargner 5 000€ au total",
        "icone": "👑",
        "categorie": "epargne",
        "points": 100
    },
    "epargne_10000": {
        "id": "epargne_10000",
        "nom": "Légende de l'Épargne",
        "description": "Épargner 10 000€ au total",
        "icone": "🌟",
        "categorie": "epargne",
        "points": 200
    },

    # Planning
    "planning_complet": {
        "id": "planning_complet",
        "nom": "Bien Organisé",
        "description": "Créer un planning avec tous les jours de la semaine",
        "icone": "📅",
        "categorie": "planning",
        "points": 25
    },
    "heures_10": {
        "id": "heures_10",
        "nom": "Travailleur",
        "description": "Planifier 10 heures en une semaine",
        "icone": "⏰",
        "categorie": "planning",
        "points": 30
    },
    "heures_20": {
        "id": "heures_20",
        "nom": "Acharné",
        "description": "Planifier 20 heures en une semaine",
        "icone": "🔥",
        "categorie": "planning",
        "points": 50
    },

    # Streaks
    "streak_7": {
        "id": "streak_7",
        "nom": "Une Semaine",
        "description": "7 jours consécutifs d'activité",
        "icone": "📆",
        "categorie": "streaks",
        "points": 35
    },
    "streak_30": {
        "id": "streak_30",
        "nom": "Un Mois",
        "description": "30 jours consécutifs d'activité",
        "icone": "🗓️",
        "categorie": "streaks",
        "points": 100
    },
    "streak_100": {
        "id": "streak_100",
        "nom": "Centenaire",
        "description": "100 jours consécutifs d'activité",
        "icone": "💯",
        "categorie": "streaks",
        "points": 300
    },

    # Projets
    "projets_5": {
        "id": "projets_5",
        "nom": "Multi-Projets",
        "description": "Gérer 5 projets simultanément",
        "icone": "📊",
        "categorie": "projets",
        "points": 40
    },
    "projets_10": {
        "id": "projets_10",
        "nom": "Gestionnaire Pro",
        "description": "Gérer 10 projets simultanément",
        "icone": "🎖️",
        "categorie": "projets",
        "points": 75
    },

    # Objectifs multiples
    "multi_objectifs_3": {
        "id": "multi_objectifs_3",
        "nom": "Ambitieux",
        "description": "Atteindre 3 objectifs",
        "icone": "🎯",
        "categorie": "objectifs",
        "points": 75
    },
    "multi_objectifs_10": {
        "id": "multi_objectifs_10",
        "nom": "Imparable",
        "description": "Atteindre 10 objectifs",
        "icone": "⭐",
        "categorie": "objectifs",
        "points": 200
    },

    # Spéciaux
    "taux_epargne_20": {
        "id": "taux_epargne_20",
        "nom": "Sage Financier",
        "description": "Atteindre un taux d'épargne de 20%",
        "icone": "🧠",
        "categorie": "special",
        "points": 60
    },
    "taux_epargne_50": {
        "id": "taux_epargne_50",
        "nom": "Frugaliste",
        "description": "Atteindre un taux d'épargne de 50%",
        "icone": "🏅",
        "categorie": "special",
        "points": 150
    },
    "simulation_parfaite": {
        "id": "simulation_parfaite",
        "nom": "Visionnaire",
        "description": "Créer une simulation où l'objectif est atteint",
        "icone": "🔮",
        "categorie": "special",
        "points": 25
    }
}

# Définition des défis hebdomadaires
DEFIS_TEMPLATES = [
    {
        "id": "defi_epargne_semaine",
        "nom": "Défi Épargne",
        "description": "Simuler une épargne de {montant}€ cette semaine",
        "type": "epargne",
        "objectif_base": 200,
        "points": 30
    },
    {
        "id": "defi_planning",
        "nom": "Défi Planning",
        "description": "Planifier au moins {heures}h cette semaine",
        "type": "planning",
        "objectif_base": 15,
        "points": 25
    },
    {
        "id": "defi_projet",
        "nom": "Défi Projet",
        "description": "Créer un nouveau projet cette semaine",
        "type": "projet",
        "objectif_base": 1,
        "points": 20
    },
    {
        "id": "defi_export",
        "nom": "Défi Export",
        "description": "Exporter {nombre} rapport(s) cette semaine",
        "type": "export",
        "objectif_base": 2,
        "points": 15
    }
]


class AchievementManager:
    """Gestionnaire des accomplissements et gamification."""

    def __init__(self):
        self.badges_obtenus = {}  # {badge_id: date_obtention}
        self.points_totaux = 0
        self.niveau = 1
        self.streak_actuel = 0
        self.meilleur_streak = 0
        self.derniere_activite = None
        self.statistiques = {
            "projets_crees": 0,
            "objectifs_atteints": 0,
            "exports_realises": 0,
            "epargne_totale": 0,
            "heures_planifiees": 0,
            "jours_actifs": 0
        }
        self.defis_actifs = []
        self.defis_completes = []
        self.historique_activites = []

    def enregistrer_activite(self, type_activite: str, details: dict = None):
        """Enregistre une activité et vérifie les badges."""
        maintenant = datetime.now()

        # Mettre à jour le streak
        if self.derniere_activite:
            diff = (maintenant.date() - self.derniere_activite.date()).days
            if diff == 1:
                self.streak_actuel += 1
            elif diff > 1:
                self.streak_actuel = 1
        else:
            self.streak_actuel = 1

        self.meilleur_streak = max(self.meilleur_streak, self.streak_actuel)
        self.derniere_activite = maintenant

        # Ajouter à l'historique
        self.historique_activites.append({
            "type": type_activite,
            "date": maintenant.isoformat(),
            "details": details or {}
        })

        # Limiter l'historique
        if len(self.historique_activites) > 1000:
            self.historique_activites = self.historique_activites[-1000:]

        # Mettre à jour les statistiques
        self._mettre_a_jour_statistiques(type_activite, details)

        # Vérifier les badges
        nouveaux_badges = self._verifier_badges()

        # Vérifier les défis
        self._verifier_defis(type_activite, details)

        return nouveaux_badges

    def _mettre_a_jour_statistiques(self, type_activite: str, details: dict):
        """Met à jour les statistiques selon l'activité."""
        if type_activite == "projet_cree":
            self.statistiques["projets_crees"] += 1
        elif type_activite == "objectif_atteint":
            self.statistiques["objectifs_atteints"] += 1
        elif type_activite == "export_realise":
            self.statistiques["exports_realises"] += 1
        elif type_activite == "epargne_ajoutee":
            self.statistiques["epargne_totale"] += details.get("montant", 0)
        elif type_activite == "planning_cree":
            self.statistiques["heures_planifiees"] += details.get("heures", 0)

    def _verifier_badges(self) -> List[dict]:
        """Vérifie et attribue les badges mérités."""
        nouveaux = []

        # Vérifications
        checks = {
            "premier_projet": self.statistiques["projets_crees"] >= 1,
            "premier_objectif": self.statistiques["objectifs_atteints"] >= 1,
            "premier_export": self.statistiques["exports_realises"] >= 1,
            "epargne_100": self.statistiques["epargne_totale"] >= 100,
            "epargne_1000": self.statistiques["epargne_totale"] >= 1000,
            "epargne_5000": self.statistiques["epargne_totale"] >= 5000,
            "epargne_10000": self.statistiques["epargne_totale"] >= 10000,
            "heures_10": self.statistiques["heures_planifiees"] >= 10,
            "heures_20": self.statistiques["heures_planifiees"] >= 20,
            "streak_7": self.streak_actuel >= 7,
            "streak_30": self.streak_actuel >= 30,
            "streak_100": self.streak_actuel >= 100,
            "projets_5": self.statistiques["projets_crees"] >= 5,
            "projets_10": self.statistiques["projets_crees"] >= 10,
            "multi_objectifs_3": self.statistiques["objectifs_atteints"] >= 3,
            "multi_objectifs_10": self.statistiques["objectifs_atteints"] >= 10,
        }

        for badge_id, condition in checks.items():
            if condition and badge_id not in self.badges_obtenus:
                self._attribuer_badge(badge_id)
                nouveaux.append(BADGES[badge_id])

        return nouveaux

    def _attribuer_badge(self, badge_id: str):
        """Attribue un badge."""
        if badge_id in BADGES and badge_id not in self.badges_obtenus:
            self.badges_obtenus[badge_id] = datetime.now().isoformat()
            self.points_totaux += BADGES[badge_id]["points"]
            self._calculer_niveau()

    def _calculer_niveau(self):
        """Calcule le niveau actuel basé sur les points."""
        # Formule : niveau = 1 + sqrt(points / 50)
        import math
        self.niveau = 1 + int(math.sqrt(self.points_totaux / 50))

    def _verifier_defis(self, type_activite: str, details: dict):
        """Vérifie la progression des défis actifs."""
        for defi in self.defis_actifs:
            if defi.get("type") == type_activite:
                defi["progression"] = defi.get("progression", 0) + 1
                if defi["progression"] >= defi["objectif"]:
                    self._completer_defi(defi)

    def _completer_defi(self, defi: dict):
        """Marque un défi comme complété."""
        defi["complete"] = True
        defi["date_completion"] = datetime.now().isoformat()
        self.points_totaux += defi.get("points", 0)
        self._calculer_niveau()
        self.defis_actifs.remove(defi)
        self.defis_completes.append(defi)

    def generer_defis_semaine(self):
        """Génère les défis de la semaine."""
        import random

        self.defis_actifs = []

        for template in random.sample(DEFIS_TEMPLATES, min(3, len(DEFIS_TEMPLATES))):
            defi = {
                "id": f"{template['id']}_{datetime.now().strftime('%Y%W')}",
                "nom": template["nom"],
                "description": template["description"].format(
                    montant=template.get("objectif_base", 0),
                    heures=template.get("objectif_base", 0),
                    nombre=template.get("objectif_base", 0)
                ),
                "type": template["type"],
                "objectif": template["objectif_base"],
                "progression": 0,
                "points": template["points"],
                "date_creation": datetime.now().isoformat(),
                "date_expiration": (datetime.now() + timedelta(days=7)).isoformat()
            }
            self.defis_actifs.append(defi)

    def obtenir_badges_par_categorie(self) -> Dict[str, List[dict]]:
        """Retourne les badges groupés par catégorie."""
        categories = {}

        for badge_id, badge in BADGES.items():
            cat = badge["categorie"]
            if cat not in categories:
                categories[cat] = []

            badge_info = badge.copy()
            badge_info["obtenu"] = badge_id in self.badges_obtenus
            if badge_info["obtenu"]:
                badge_info["date_obtention"] = self.badges_obtenus[badge_id]

            categories[cat].append(badge_info)

        return categories

    def obtenir_progression_niveau(self) -> dict:
        """Retourne la progression vers le prochain niveau."""
        import math

        points_niveau_actuel = 50 * (self.niveau - 1) ** 2
        points_niveau_suivant = 50 * self.niveau ** 2
        points_dans_niveau = self.points_totaux - points_niveau_actuel
        points_requis = points_niveau_suivant - points_niveau_actuel

        return {
            "niveau": self.niveau,
            "points_totaux": self.points_totaux,
            "points_dans_niveau": points_dans_niveau,
            "points_requis": points_requis,
            "progression": points_dans_niveau / points_requis if points_requis > 0 else 1
        }

    def to_dict(self) -> dict:
        """Sérialise le gestionnaire."""
        return {
            "badges_obtenus": self.badges_obtenus,
            "points_totaux": self.points_totaux,
            "niveau": self.niveau,
            "streak_actuel": self.streak_actuel,
            "meilleur_streak": self.meilleur_streak,
            "derniere_activite": self.derniere_activite.isoformat() if self.derniere_activite else None,
            "statistiques": self.statistiques,
            "defis_actifs": self.defis_actifs,
            "defis_completes": self.defis_completes[-50:],  # Garder les 50 derniers
            "historique_activites": self.historique_activites[-100:]  # Garder les 100 derniers
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AchievementManager':
        """Désérialise le gestionnaire."""
        am = cls()
        am.badges_obtenus = data.get("badges_obtenus", {})
        am.points_totaux = data.get("points_totaux", 0)
        am.niveau = data.get("niveau", 1)
        am.streak_actuel = data.get("streak_actuel", 0)
        am.meilleur_streak = data.get("meilleur_streak", 0)

        if data.get("derniere_activite"):
            am.derniere_activite = datetime.fromisoformat(data["derniere_activite"])

        am.statistiques = data.get("statistiques", am.statistiques)
        am.defis_actifs = data.get("defis_actifs", [])
        am.defis_completes = data.get("defis_completes", [])
        am.historique_activites = data.get("historique_activites", [])

        return am


def obtenir_titre_niveau(niveau: int) -> str:
    """Retourne le titre correspondant au niveau."""
    titres = {
        1: "Débutant",
        2: "Apprenti",
        3: "Initié",
        4: "Compétent",
        5: "Confirmé",
        6: "Expert",
        7: "Maître",
        8: "Grand Maître",
        9: "Légende",
        10: "Mythique"
    }
    if niveau >= 10:
        return titres[10]
    return titres.get(niveau, "Débutant")


def obtenir_couleur_niveau(niveau: int) -> str:
    """Retourne la couleur correspondant au niveau."""
    couleurs = {
        1: "#718096",  # Gris
        2: "#48bb78",  # Vert
        3: "#4299e1",  # Bleu
        4: "#9f7aea",  # Violet
        5: "#ed8936",  # Orange
        6: "#f56565",  # Rouge
        7: "#ecc94b",  # Jaune/Or
        8: "#38b2ac",  # Teal
        9: "#e53e3e",  # Rouge foncé
        10: "#805ad5"  # Violet royal
    }
    if niveau >= 10:
        return couleurs[10]
    return couleurs.get(niveau, couleurs[1])
