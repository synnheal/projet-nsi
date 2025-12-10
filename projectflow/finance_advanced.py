"""
Module finance_advanced - Fonctionnalités financières avancées.

Ce module ajoute :
- Revenus variables par mois
- Catégories de dépenses détaillées
- Multi-objectifs
- Scénarios "What-if"
- Analyses et recommandations
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
import math


# Catégories de dépenses prédéfinies
CATEGORIES_DEPENSES = {
    "logement": {"nom": "Logement", "icone": "🏠", "couleur": "#4361ee"},
    "alimentation": {"nom": "Alimentation", "icone": "🍽️", "couleur": "#06d6a0"},
    "transport": {"nom": "Transport", "icone": "🚗", "couleur": "#ffd166"},
    "sante": {"nom": "Santé", "icone": "🏥", "couleur": "#ef476f"},
    "loisirs": {"nom": "Loisirs", "icone": "🎮", "couleur": "#7209b7"},
    "education": {"nom": "Éducation", "icone": "📚", "couleur": "#00b4d8"},
    "vetements": {"nom": "Vêtements", "icone": "👕", "couleur": "#fb8500"},
    "services": {"nom": "Services", "icone": "📱", "couleur": "#ff006e"},
    "epargne": {"nom": "Épargne", "icone": "💰", "couleur": "#38b000"},
    "autres": {"nom": "Autres", "icone": "📦", "couleur": "#718096"}
}


class RevenusVariables:
    """Gestion des revenus variables par mois."""

    def __init__(self):
        self.revenus_base = 0
        self.revenus_mensuels = {}  # {mois: montant}
        self.revenus_exceptionnels = []  # [(mois, montant, description)]

    def definir_base(self, montant: float):
        """Définit le revenu de base mensuel."""
        self.revenus_base = montant

    def ajouter_revenu_mensuel(self, mois: int, montant: float):
        """Définit un revenu spécifique pour un mois."""
        self.revenus_mensuels[mois] = montant

    def ajouter_revenu_exceptionnel(self, mois: int, montant: float, description: str = ""):
        """Ajoute un revenu exceptionnel (prime, bonus, etc.)."""
        self.revenus_exceptionnels.append((mois, montant, description))

    def obtenir_revenu(self, mois: int) -> float:
        """Retourne le revenu total pour un mois donné."""
        base = self.revenus_mensuels.get(mois, self.revenus_base)
        exceptionnels = sum(m for mo, m, _ in self.revenus_exceptionnels if mo == mois)
        return base + exceptionnels

    def to_dict(self) -> dict:
        return {
            "revenus_base": self.revenus_base,
            "revenus_mensuels": self.revenus_mensuels,
            "revenus_exceptionnels": self.revenus_exceptionnels
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RevenusVariables':
        rv = cls()
        rv.revenus_base = data.get("revenus_base", 0)
        rv.revenus_mensuels = {int(k): v for k, v in data.get("revenus_mensuels", {}).items()}
        rv.revenus_exceptionnels = data.get("revenus_exceptionnels", [])
        return rv


class DepensesCategories:
    """Gestion des dépenses par catégories."""

    def __init__(self):
        self.depenses = {}  # {categorie: montant}
        self.depenses_exceptionnelles = []  # [(mois, categorie, montant, description)]

    def definir_depense(self, categorie: str, montant: float):
        """Définit une dépense mensuelle pour une catégorie."""
        if categorie in CATEGORIES_DEPENSES:
            self.depenses[categorie] = montant

    def ajouter_depense_exceptionnelle(self, mois: int, categorie: str,
                                        montant: float, description: str = ""):
        """Ajoute une dépense exceptionnelle."""
        self.depenses_exceptionnelles.append((mois, categorie, montant, description))

    def obtenir_total_mensuel(self, mois: int = None) -> float:
        """Retourne le total des dépenses mensuelles."""
        base = sum(self.depenses.values())
        if mois:
            exceptionnelles = sum(m for mo, _, m, _ in self.depenses_exceptionnelles if mo == mois)
            return base + exceptionnelles
        return base

    def obtenir_par_categorie(self) -> Dict[str, float]:
        """Retourne les dépenses par catégorie."""
        return self.depenses.copy()

    def obtenir_repartition(self) -> List[Tuple[str, float]]:
        """Retourne la répartition pour graphique camembert."""
        result = []
        for cat, montant in self.depenses.items():
            if montant > 0:
                info = CATEGORIES_DEPENSES.get(cat, {})
                nom = info.get("nom", cat.capitalize())
                result.append((nom, montant))
        return sorted(result, key=lambda x: x[1], reverse=True)

    def to_dict(self) -> dict:
        return {
            "depenses": self.depenses,
            "depenses_exceptionnelles": self.depenses_exceptionnelles
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DepensesCategories':
        dc = cls()
        dc.depenses = data.get("depenses", {})
        dc.depenses_exceptionnelles = data.get("depenses_exceptionnelles", [])
        return dc


class Objectif:
    """Représente un objectif financier."""

    def __init__(self, nom: str, montant: float, priorite: int = 1,
                 date_limite: str = None):
        self.id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.nom = nom
        self.montant = montant
        self.priorite = priorite  # 1 = haute, 2 = moyenne, 3 = basse
        self.date_limite = date_limite
        self.montant_atteint = 0
        self.atteint = False

    @property
    def progression(self) -> float:
        if self.montant <= 0:
            return 0
        return min(self.montant_atteint / self.montant, 1.0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nom": self.nom,
            "montant": self.montant,
            "priorite": self.priorite,
            "date_limite": self.date_limite,
            "montant_atteint": self.montant_atteint,
            "atteint": self.atteint
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Objectif':
        obj = cls(
            nom=data.get("nom", ""),
            montant=data.get("montant", 0),
            priorite=data.get("priorite", 1),
            date_limite=data.get("date_limite")
        )
        obj.id = data.get("id", obj.id)
        obj.montant_atteint = data.get("montant_atteint", 0)
        obj.atteint = data.get("atteint", False)
        return obj


class MultiObjectifs:
    """Gestion de plusieurs objectifs avec répartition automatique."""

    def __init__(self):
        self.objectifs = []

    def ajouter_objectif(self, objectif: Objectif):
        """Ajoute un nouvel objectif."""
        self.objectifs.append(objectif)
        self._trier_par_priorite()

    def supprimer_objectif(self, objectif_id: str):
        """Supprime un objectif."""
        self.objectifs = [o for o in self.objectifs if o.id != objectif_id]

    def _trier_par_priorite(self):
        """Trie les objectifs par priorité."""
        self.objectifs.sort(key=lambda x: x.priorite)

    def repartir_epargne(self, montant_total: float) -> Dict[str, float]:
        """
        Répartit l'épargne entre les objectifs selon leur priorité.

        Stratégie : Priorité d'abord (remplir les objectifs haute priorité en premier)
        """
        repartition = {}
        restant = montant_total

        for obj in self.objectifs:
            if obj.atteint:
                repartition[obj.id] = 0
                continue

            besoin = obj.montant - obj.montant_atteint
            allocation = min(restant, besoin)
            repartition[obj.id] = allocation
            restant -= allocation

            if restant <= 0:
                break

        return repartition

    def repartir_epargne_proportionnel(self, montant_total: float) -> Dict[str, float]:
        """
        Répartit l'épargne proportionnellement aux objectifs non atteints.
        """
        objectifs_actifs = [o for o in self.objectifs if not o.atteint]
        if not objectifs_actifs:
            return {}

        total_restant = sum(o.montant - o.montant_atteint for o in objectifs_actifs)
        if total_restant <= 0:
            return {o.id: 0 for o in objectifs_actifs}

        repartition = {}
        for obj in objectifs_actifs:
            besoin = obj.montant - obj.montant_atteint
            proportion = besoin / total_restant
            repartition[obj.id] = montant_total * proportion

        return repartition

    def to_dict(self) -> dict:
        return {
            "objectifs": [o.to_dict() for o in self.objectifs]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'MultiObjectifs':
        mo = cls()
        for obj_data in data.get("objectifs", []):
            mo.objectifs.append(Objectif.from_dict(obj_data))
        return mo


class Scenario:
    """Représente un scénario what-if."""

    def __init__(self, nom: str, modifications: dict = None):
        self.nom = nom
        self.modifications = modifications or {}
        # modifications peut contenir:
        # - revenus_ajustement: float (ex: +100 ou -50)
        # - depenses_ajustement: float
        # - objectif_ajustement: float
        # - duree_mois: int

    def appliquer(self, finances_base: dict) -> dict:
        """Applique les modifications au scénario de base."""
        result = finances_base.copy()

        if "revenus_ajustement" in self.modifications:
            result["revenus"] = result.get("revenus", 0) + self.modifications["revenus_ajustement"]

        if "depenses_ajustement" in self.modifications:
            total_dep = result.get("depenses_fixes", 0) + result.get("depenses_variables", 0)
            ajustement = self.modifications["depenses_ajustement"]
            # Répartir l'ajustement proportionnellement
            if total_dep > 0:
                ratio_fixes = result.get("depenses_fixes", 0) / total_dep
                result["depenses_fixes"] = result.get("depenses_fixes", 0) + ajustement * ratio_fixes
                result["depenses_variables"] = result.get("depenses_variables", 0) + ajustement * (1 - ratio_fixes)

        if "objectif_ajustement" in self.modifications:
            result["objectif"] = result.get("objectif", 0) + self.modifications["objectif_ajustement"]

        if "duree_mois" in self.modifications:
            result["duree_mois"] = self.modifications["duree_mois"]

        return result


def simuler_avance(revenus: 'RevenusVariables', depenses: 'DepensesCategories',
                   objectifs: 'MultiObjectifs', duree_mois: int = 24) -> dict:
    """
    Simulation avancée avec revenus variables et multi-objectifs.

    Returns:
        Dictionnaire avec résultats détaillés
    """
    tableau_mensuel = []
    cumul_total = 0

    for mois in range(1, duree_mois + 1):
        revenu_mois = revenus.obtenir_revenu(mois)
        depenses_mois = depenses.obtenir_total_mensuel(mois)
        epargne_mois = revenu_mois - depenses_mois

        cumul_total += max(epargne_mois, 0)

        # Répartir l'épargne entre objectifs
        if epargne_mois > 0:
            repartition = objectifs.repartir_epargne(epargne_mois)
            for obj in objectifs.objectifs:
                if obj.id in repartition:
                    obj.montant_atteint += repartition[obj.id]
                    if obj.montant_atteint >= obj.montant:
                        obj.atteint = True

        # Statut des objectifs
        objectifs_status = []
        for obj in objectifs.objectifs:
            objectifs_status.append({
                "id": obj.id,
                "nom": obj.nom,
                "progression": obj.progression,
                "atteint": obj.atteint
            })

        tableau_mensuel.append({
            "mois": mois,
            "revenu": revenu_mois,
            "depenses": depenses_mois,
            "epargne": epargne_mois,
            "cumul": cumul_total,
            "objectifs": objectifs_status
        })

    # Résumé
    tous_atteints = all(o.atteint for o in objectifs.objectifs)
    epargne_moyenne = sum(t["epargne"] for t in tableau_mensuel) / len(tableau_mensuel)

    return {
        "tableau_mensuel": tableau_mensuel,
        "cumul_total": cumul_total,
        "epargne_moyenne": epargne_moyenne,
        "tous_objectifs_atteints": tous_atteints,
        "objectifs_finaux": [o.to_dict() for o in objectifs.objectifs]
    }


def comparer_scenarios(finances_base: dict, scenarios: List[Scenario],
                       duree_mois: int = 24) -> List[dict]:
    """
    Compare plusieurs scénarios what-if.

    Args:
        finances_base: Données financières de base
        scenarios: Liste de scénarios à comparer
        duree_mois: Durée de simulation

    Returns:
        Liste de résultats pour chaque scénario
    """
    from . import finance

    resultats = []

    # Scénario de base
    sim_base = finance.simuler_objectif(
        revenus=finances_base.get("revenus", 0),
        depenses_fixes=finances_base.get("depenses_fixes", 0),
        depenses_variables=finances_base.get("depenses_variables", 0),
        objectif=finances_base.get("objectif", 0),
        duree_mois=duree_mois
    )

    resultats.append({
        "nom": "Actuel",
        "color": "#4361ee",
        "data": [t["cumul"] for t in sim_base.get("tableau_mensuel", [])],
        "mois_objectif": sim_base.get("mois_objectif_atteint"),
        "total": sim_base.get("total_epargne", 0)
    })

    # Autres scénarios
    colors = ["#06d6a0", "#ffd166", "#ef476f", "#7209b7"]
    for i, scenario in enumerate(scenarios):
        finances_modifiees = scenario.appliquer(finances_base)

        sim = finance.simuler_objectif(
            revenus=finances_modifiees.get("revenus", 0),
            depenses_fixes=finances_modifiees.get("depenses_fixes", 0),
            depenses_variables=finances_modifiees.get("depenses_variables", 0),
            objectif=finances_modifiees.get("objectif", 0),
            duree_mois=duree_mois
        )

        resultats.append({
            "nom": scenario.nom,
            "color": colors[i % len(colors)],
            "data": [t["cumul"] for t in sim.get("tableau_mensuel", [])],
            "mois_objectif": sim.get("mois_objectif_atteint"),
            "total": sim.get("total_epargne", 0)
        })

    return resultats


def generer_recommandations(finances: dict, simulation: dict) -> List[dict]:
    """
    Génère des recommandations personnalisées.

    Returns:
        Liste de recommandations avec type, message et impact
    """
    recommandations = []

    revenus = finances.get("revenus", 0)
    depenses_fixes = finances.get("depenses_fixes", 0)
    depenses_variables = finances.get("depenses_variables", 0)
    objectif = finances.get("objectif", 0)

    total_depenses = depenses_fixes + depenses_variables
    epargne = revenus - total_depenses
    taux_epargne = (epargne / revenus * 100) if revenus > 0 else 0

    # Analyse du taux d'épargne
    if taux_epargne < 10:
        recommandations.append({
            "type": "warning",
            "titre": "Taux d'épargne faible",
            "message": f"Votre taux d'épargne est de {taux_epargne:.1f}%. L'idéal est d'atteindre 20%.",
            "action": "Identifiez les dépenses variables réductibles.",
            "impact": f"+{revenus * 0.1:.0f}€/mois si vous atteignez 20%"
        })
    elif taux_epargne >= 30:
        recommandations.append({
            "type": "success",
            "titre": "Excellent taux d'épargne",
            "message": f"Bravo ! Votre taux d'épargne de {taux_epargne:.1f}% est excellent.",
            "action": "Maintenez ce rythme !",
            "impact": None
        })

    # Analyse des dépenses variables
    if depenses_variables > depenses_fixes * 0.5:
        reduction_possible = depenses_variables * 0.2
        recommandations.append({
            "type": "info",
            "titre": "Dépenses variables élevées",
            "message": "Vos dépenses variables représentent une part importante de votre budget.",
            "action": "Réduire de 20% permettrait d'accélérer vos objectifs.",
            "impact": f"+{reduction_possible:.0f}€/mois d'épargne"
        })

    # Temps pour atteindre l'objectif
    if simulation.get("mois_objectif_atteint"):
        mois = simulation["mois_objectif_atteint"]
        if mois > 24:
            recommandations.append({
                "type": "warning",
                "titre": "Objectif à long terme",
                "message": f"Votre objectif sera atteint dans {mois} mois ({mois // 12} ans).",
                "action": "Envisagez d'augmenter votre épargne mensuelle.",
                "impact": f"Avec +100€/mois, objectif atteint en {max(1, int(objectif / (epargne + 100)))} mois"
            })
    elif not simulation.get("possible"):
        recommandations.append({
            "type": "danger",
            "titre": "Objectif impossible",
            "message": "Vos dépenses dépassent vos revenus.",
            "action": "Réduisez vos dépenses ou augmentez vos revenus.",
            "impact": f"Besoin de +{abs(epargne):.0f}€/mois pour équilibrer"
        })

    # Recommandation d'objectifs intermédiaires
    if objectif > epargne * 12:
        objectif_intermediaire = epargne * 6
        recommandations.append({
            "type": "info",
            "titre": "Objectif intermédiaire suggéré",
            "message": "Votre objectif est ambitieux. Créez des étapes.",
            "action": f"Premier objectif : {objectif_intermediaire:,.0f}€ en 6 mois.",
            "impact": "Motivation accrue avec des victoires rapides"
        })

    return recommandations


def calculer_statistiques(simulation: dict) -> dict:
    """
    Calcule des statistiques détaillées sur la simulation.
    """
    tableau = simulation.get("tableau_mensuel", [])
    if not tableau:
        return {}

    epargnes = [t.get("epargne", 0) for t in tableau]
    revenus = [t.get("revenu", 0) for t in tableau]

    return {
        "epargne_min": min(epargnes),
        "epargne_max": max(epargnes),
        "epargne_moyenne": sum(epargnes) / len(epargnes),
        "revenu_total": sum(revenus),
        "depenses_totales": sum(t.get("depenses", 0) for t in tableau),
        "mois_negatifs": sum(1 for e in epargnes if e < 0),
        "mois_positifs": sum(1 for e in epargnes if e > 0),
        "tendance": "hausse" if epargnes[-1] > epargnes[0] else "baisse"
    }
