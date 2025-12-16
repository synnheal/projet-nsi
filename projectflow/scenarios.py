"""
Module scenarios - Simulations de scénarios What-If pour la gestion de stock.

Ce module fournit :
- Simulation d'augmentation/diminution des ventes
- Simulation d'impact de ruptures de stock
- Simulation de changements de prix
- Simulation de délais de réapprovisionnement
- Comparaison de différents scénarios
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class Scenario:
    """Représente un scénario de simulation."""

    nom: str
    description: str
    modifications: Dict  # Paramètres modifiés

    # Types de modifications possibles:
    # - variation_ventes: float (ex: 0.2 = +20%, -0.1 = -10%)
    # - rupture_article_ids: List[str] (articles en rupture simulée)
    # - variation_prix: float (variation des prix de vente)
    # - variation_delai: int (jours ajoutés aux délais)
    # - variation_cout: float (variation des coûts d'achat)

    couleur: str = "#4361ee"


@dataclass
class ResultatSimulation:
    """Résultat d'une simulation de scénario."""

    scenario: Scenario
    duree_jours: int

    # Métriques financières
    chiffre_affaires_total: float
    cout_total: float
    marge_totale: float
    taux_marge_moyen: float

    # Stock
    ruptures_count: int  # Nombre de ruptures
    jours_rupture_total: int  # Total jours en rupture
    ventes_perdues: float  # CA perdu à cause de ruptures

    # Réapprovisionnements
    nb_reappros: int
    cout_stockage_estime: float

    # Performance
    score_global: float  # Score 0-100


class ScenarioEngine:
    """Moteur de simulation de scénarios."""

    def __init__(self, inventaire, prediction_engine):
        """
        Initialise le moteur de scénarios.

        Args:
            inventaire: Instance de la classe Inventaire
            prediction_engine: Instance de PredictionEngine
        """
        self.inventaire = inventaire
        self.prediction_engine = prediction_engine

    def simuler_scenario(self, scenario: Scenario, duree_jours: int = 90) -> ResultatSimulation:
        """
        Simule un scénario sur une période donnée.

        Args:
            scenario: Scénario à simuler
            duree_jours: Durée de la simulation en jours

        Returns:
            Résultat de la simulation
        """
        # Copier l'inventaire pour ne pas modifier l'original
        inventaire_sim = deepcopy(self.inventaire)

        # Appliquer les modifications du scénario
        self._appliquer_modifications(inventaire_sim, scenario)

        # Simuler jour par jour
        metriques = self._executer_simulation(inventaire_sim, scenario, duree_jours)

        # Calculer le score global
        score = self._calculer_score(metriques)

        return ResultatSimulation(
            scenario=scenario,
            duree_jours=duree_jours,
            chiffre_affaires_total=metriques["ca_total"],
            cout_total=metriques["cout_total"],
            marge_totale=metriques["marge_totale"],
            taux_marge_moyen=metriques["taux_marge_moyen"],
            ruptures_count=metriques["ruptures_count"],
            jours_rupture_total=metriques["jours_rupture_total"],
            ventes_perdues=metriques["ventes_perdues"],
            nb_reappros=metriques["nb_reappros"],
            cout_stockage_estime=metriques["cout_stockage"],
            score_global=score
        )

    def _appliquer_modifications(self, inventaire_sim, scenario: Scenario):
        """Applique les modifications du scénario à l'inventaire simulé."""
        mods = scenario.modifications

        # Variation des prix de vente
        if "variation_prix" in mods:
            variation = mods["variation_prix"]
            for article in inventaire_sim.articles:
                article.prix_vente *= (1 + variation)

        # Variation des coûts d'achat
        if "variation_cout" in mods:
            variation = mods["variation_cout"]
            for article in inventaire_sim.articles:
                article.prix_achat *= (1 + variation)

        # Variation des délais de réappro
        if "variation_delai" in mods:
            jours = mods["variation_delai"]
            for article in inventaire_sim.articles:
                article.delai_reappro_jours += jours
                article.delai_reappro_jours = max(1, article.delai_reappro_jours)

        # Ruptures forcées
        if "rupture_article_ids" in mods:
            for article_id in mods["rupture_article_ids"]:
                article = inventaire_sim.obtenir_article(article_id)
                if article:
                    article.quantite = 0

    def _executer_simulation(self, inventaire_sim, scenario: Scenario, duree_jours: int) -> Dict:
        """Exécute la simulation jour par jour."""
        ca_total = 0
        cout_total = 0
        ruptures_count = 0
        jours_rupture_total = 0
        ventes_perdues = 0
        nb_reappros = 0

        variation_ventes = scenario.modifications.get("variation_ventes", 0)

        for jour in range(duree_jours):
            # Pour chaque article
            for article in inventaire_sim.articles:
                if not article.actif:
                    continue

                # Calculer les ventes du jour
                ventes_base = article.ventes_jour
                ventes_jour = ventes_base * (1 + variation_ventes)
                ventes_jour = max(0, int(ventes_jour))

                # Tenter la vente
                if article.quantite >= ventes_jour:
                    # Vente réussie
                    article.quantite -= ventes_jour
                    ca_total += ventes_jour * article.prix_vente
                    cout_total += ventes_jour * article.prix_achat
                elif article.quantite > 0:
                    # Vente partielle
                    ca_total += article.quantite * article.prix_vente
                    cout_total += article.quantite * article.prix_achat
                    ventes_perdues += (ventes_jour - article.quantite) * article.prix_vente
                    article.quantite = 0
                    ruptures_count += 1
                    jours_rupture_total += 1
                else:
                    # Rupture complète
                    ventes_perdues += ventes_jour * article.prix_vente
                    jours_rupture_total += 1

                # Réapprovisionnement automatique si sous seuil
                if article.quantite <= article.seuil_critique:
                    quantite_reappro = article.stock_optimal - article.quantite
                    article.quantite += quantite_reappro
                    cout_total += quantite_reappro * article.prix_achat
                    nb_reappros += 1

        # Coût de stockage (immobilisation capital)
        valeur_stock_moyenne = sum(a.valeur_stock for a in inventaire_sim.articles)
        cout_stockage = valeur_stock_moyenne * 0.25 * (duree_jours / 365)  # 25% par an

        marge_totale = ca_total - cout_total
        taux_marge_moyen = (marge_totale / ca_total * 100) if ca_total > 0 else 0

        return {
            "ca_total": ca_total,
            "cout_total": cout_total,
            "marge_totale": marge_totale,
            "taux_marge_moyen": taux_marge_moyen,
            "ruptures_count": ruptures_count,
            "jours_rupture_total": jours_rupture_total,
            "ventes_perdues": ventes_perdues,
            "nb_reappros": nb_reappros,
            "cout_stockage": cout_stockage
        }

    def _calculer_score(self, metriques: Dict) -> float:
        """
        Calcule un score global pour le scénario (0-100).

        Critères :
        - Marge (40%)
        - Absence de ruptures (40%)
        - Efficacité du stock (20%)
        """
        # Score marge (0-40 points)
        taux_marge = metriques["taux_marge_moyen"]
        score_marge = min(40, (taux_marge / 50) * 40)  # 50% = max

        # Score ruptures (0-40 points)
        jours_rupture = metriques["jours_rupture_total"]
        score_ruptures = max(0, 40 - (jours_rupture / 10))  # -4 points par jour

        # Score efficacité stock (0-20 points)
        nb_reappros = metriques["nb_reappros"]
        score_efficacite = max(0, 20 - (nb_reappros / 5))  # -4 points par réappro

        return score_marge + score_ruptures + score_efficacite

    def comparer_scenarios(self, scenarios: List[Scenario], duree_jours: int = 90) -> List[ResultatSimulation]:
        """
        Compare plusieurs scénarios.

        Args:
            scenarios: Liste de scénarios à comparer
            duree_jours: Durée de simulation

        Returns:
            Liste de résultats triés par score
        """
        resultats = []

        # Ajouter le scénario actuel (baseline)
        scenario_actuel = Scenario(
            nom="Situation actuelle",
            description="Sans modification",
            modifications={},
            couleur="#4361ee"
        )
        resultats.append(self.simuler_scenario(scenario_actuel, duree_jours))

        # Simuler les autres scénarios
        for scenario in scenarios:
            resultat = self.simuler_scenario(scenario, duree_jours)
            resultats.append(resultat)

        # Trier par score décroissant
        resultats.sort(key=lambda r: r.score_global, reverse=True)

        return resultats

    def generer_scenarios_predéfinis(self) -> List[Scenario]:
        """
        Génère des scénarios prédéfinis utiles.

        Returns:
            Liste de scénarios standard
        """
        return [
            Scenario(
                nom="Ventes +20%",
                description="Augmentation des ventes de 20% (campagne marketing)",
                modifications={"variation_ventes": 0.2},
                couleur="#06d6a0"
            ),
            Scenario(
                nom="Ventes -20%",
                description="Baisse des ventes de 20% (période creuse)",
                modifications={"variation_ventes": -0.2},
                couleur="#ef476f"
            ),
            Scenario(
                nom="Prix +10%",
                description="Augmentation des prix de vente de 10%",
                modifications={"variation_prix": 0.1},
                couleur="#ffd166"
            ),
            Scenario(
                nom="Coûts +15%",
                description="Augmentation des coûts d'achat de 15% (inflation)",
                modifications={"variation_cout": 0.15},
                couleur="#ff006e"
            ),
            Scenario(
                nom="Délais +5j",
                description="Allongement des délais de réapprovisionnement (+5 jours)",
                modifications={"variation_delai": 5},
                couleur="#7209b7"
            ),
            Scenario(
                nom="Optimiste",
                description="Ventes +15% et marge +5%",
                modifications={"variation_ventes": 0.15, "variation_prix": 0.05},
                couleur="#38b000"
            ),
            Scenario(
                nom="Pessimiste",
                description="Ventes -15% et coûts +10%",
                modifications={"variation_ventes": -0.15, "variation_cout": 0.1},
                couleur="#dc2626"
            ),
        ]

    def formater_comparaison(self, resultats: List[ResultatSimulation]) -> str:
        """
        Formate une comparaison de scénarios en texte.

        Returns:
            Rapport formaté
        """
        texte = "\n" + "=" * 90 + "\n"
        texte += "                      COMPARAISON DE SCÉNARIOS\n"
        texte += "=" * 90 + "\n\n"

        for i, resultat in enumerate(resultats, 1):
            scenario = resultat.scenario

            texte += f"\n{i}. {scenario.nom}"
            if i == 1:
                texte += " 🏆"
            texte += "\n"
            texte += "-" * 90 + "\n"
            texte += f"Description:        {scenario.description}\n"
            texte += f"Score global:       {resultat.score_global:.1f}/100\n\n"

            # Métriques financières
            texte += "💰 FINANCES\n"
            texte += f"  CA total:         {resultat.chiffre_affaires_total:>15,.2f} €\n"
            texte += f"  Coûts:            {resultat.cout_total:>15,.2f} €\n"
            texte += f"  Marge:            {resultat.marge_totale:>15,.2f} € ({resultat.taux_marge_moyen:.1f}%)\n\n"

            # Stock
            texte += "📦 STOCK\n"
            texte += f"  Ruptures:         {resultat.ruptures_count} fois\n"
            texte += f"  Jours en rupture: {resultat.jours_rupture_total} jours\n"
            texte += f"  Ventes perdues:   {resultat.ventes_perdues:>15,.2f} €\n"
            texte += f"  Réappros:         {resultat.nb_reappros}\n"
            texte += f"  Coût stockage:    {resultat.cout_stockage_estime:>15,.2f} €\n\n"

        # Recommandation
        texte += "=" * 90 + "\n"
        texte += f"🎯 RECOMMANDATION: {resultats[0].scenario.nom}\n"
        texte += "=" * 90 + "\n"

        return texte

    def analyser_impact_rupture(self, article_id: str, duree_jours: int = 30) -> Dict:
        """
        Analyse l'impact d'une rupture prolongée sur un article.

        Args:
            article_id: ID de l'article
            duree_jours: Durée de la rupture simulée

        Returns:
            Dictionnaire avec l'analyse
        """
        article = self.inventaire.obtenir_article(article_id)
        if not article:
            return {"erreur": "Article introuvable"}

        # Ventes perdues
        ventes_jour = article.ventes_jour
        ventes_perdues_quantite = ventes_jour * duree_jours
        ca_perdu = ventes_perdues_quantite * article.prix_vente
        marge_perdue = ventes_perdues_quantite * article.marge_unitaire

        # Impact en pourcentage du CA annuel
        ca_annuel_article = ventes_jour * 365 * article.prix_vente
        impact_pct = (ca_perdu / ca_annuel_article * 100) if ca_annuel_article > 0 else 0

        return {
            "article_id": article_id,
            "article_nom": article.nom,
            "duree_rupture_jours": duree_jours,
            "ventes_perdues_quantite": int(ventes_perdues_quantite),
            "ca_perdu": ca_perdu,
            "marge_perdue": marge_perdue,
            "impact_pourcentage_ca_annuel": impact_pct,
            "severite": self._determiner_severite_impact(impact_pct)
        }

    def _determiner_severite_impact(self, impact_pct: float) -> str:
        """Détermine la sévérité de l'impact."""
        if impact_pct >= 20:
            return "Critique"
        elif impact_pct >= 10:
            return "Élevée"
        elif impact_pct >= 5:
            return "Moyenne"
        else:
            return "Faible"
