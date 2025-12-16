"""
Module restocking - Système de réapprovisionnement semi-automatique.

Ce module fournit :
- Calcul automatique des quantités à commander
- Priorisation des commandes par urgence
- Génération de bons de commande
- Optimisation des commandes (regroupement par fournisseur)
- Suggestions de réapprovisionnement
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class Urgence(Enum):
    """Niveaux d'urgence pour le réapprovisionnement."""
    CRITIQUE = 1  # Rupture imminente
    ELEVEE = 2    # Sous seuil critique
    MOYENNE = 3   # Approche du seuil
    FAIBLE = 4    # Préventif


@dataclass
class RecommandationReappro:
    """Recommandation de réapprovisionnement pour un article."""

    article_id: str
    article_nom: str
    article_reference: str

    # État actuel
    quantite_actuelle: int
    seuil_critique: int
    stock_optimal: int

    # Recommandation
    quantite_recommandee: int
    urgence: Urgence
    jours_avant_rupture: Optional[int]
    cout_estime: float

    # Fournisseur
    fournisseur: str
    delai_jours: int

    # Justification
    raison: str
    date_commande_suggeree: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "article_id": self.article_id,
            "article_nom": self.article_nom,
            "article_reference": self.article_reference,
            "quantite_actuelle": self.quantite_actuelle,
            "seuil_critique": self.seuil_critique,
            "stock_optimal": self.stock_optimal,
            "quantite_recommandee": self.quantite_recommandee,
            "urgence": self.urgence.name,
            "jours_avant_rupture": self.jours_avant_rupture,
            "cout_estime": self.cout_estime,
            "fournisseur": self.fournisseur,
            "delai_jours": self.delai_jours,
            "raison": self.raison,
            "date_commande_suggeree": self.date_commande_suggeree
        }


@dataclass
class BonCommande:
    """Bon de commande groupé par fournisseur."""

    fournisseur: str
    date_creation: str
    articles: List[Dict]  # Liste des articles à commander
    total_quantite: int
    total_cout: float
    urgence_max: Urgence
    numero: str = field(default_factory=lambda: f"BC-{datetime.now().strftime('%Y%m%d-%H%M%S')}")

    def to_dict(self) -> dict:
        return {
            "numero": self.numero,
            "fournisseur": self.fournisseur,
            "date_creation": self.date_creation,
            "articles": self.articles,
            "total_quantite": self.total_quantite,
            "total_cout": self.total_cout,
            "urgence_max": self.urgence_max.name
        }


class RestockingEngine:
    """Moteur de réapprovisionnement intelligent."""

    def __init__(self, inventaire, prediction_engine):
        """
        Initialise le moteur de réapprovisionnement.

        Args:
            inventaire: Instance de la classe Inventaire
            prediction_engine: Instance de PredictionEngine
        """
        self.inventaire = inventaire
        self.prediction_engine = prediction_engine

    def generer_recommandations(self,
                                inclure_preventif: bool = True) -> List[RecommandationReappro]:
        """
        Génère les recommandations de réapprovisionnement.

        Args:
            inclure_preventif: Inclure les recommandations préventives

        Returns:
            Liste des recommandations triées par urgence
        """
        recommandations = []

        for article in self.inventaire.articles:
            if not article.actif:
                continue

            # Vérifier si réapprovisionnement nécessaire
            reco = self._evaluer_article(article, inclure_preventif)
            if reco:
                recommandations.append(reco)

        # Trier par urgence puis par jours avant rupture
        recommandations.sort(key=lambda r: (
            r.urgence.value,
            r.jours_avant_rupture if r.jours_avant_rupture is not None else 999
        ))

        return recommandations

    def _evaluer_article(self, article, inclure_preventif: bool) -> Optional[RecommandationReappro]:
        """
        Évalue si un article nécessite un réapprovisionnement.

        Returns:
            RecommandationReappro ou None
        """
        quantite_actuelle = article.quantite
        seuil_critique = article.seuil_critique
        stock_optimal = article.stock_optimal

        # Déterminer l'urgence et la quantité
        urgence = None
        quantite_a_commander = 0
        raison = ""

        # Rupture de stock
        if quantite_actuelle == 0:
            urgence = Urgence.CRITIQUE
            quantite_a_commander = stock_optimal
            raison = "Rupture de stock"

        # Stock critique (sous seuil)
        elif quantite_actuelle <= seuil_critique:
            urgence = Urgence.ELEVEE
            quantite_a_commander = stock_optimal - quantite_actuelle
            raison = f"Stock critique ({quantite_actuelle} ≤ {seuil_critique})"

        # Stock faible (entre seuil et seuil*2)
        elif quantite_actuelle <= seuil_critique * 2:
            urgence = Urgence.MOYENNE
            quantite_a_commander = stock_optimal - quantite_actuelle
            raison = f"Stock faible, proche du seuil"

        # Prévention (si ventes régulières et stock sous optimal)
        elif inclure_preventif and article.ventes_jour > 0:
            if quantite_actuelle < stock_optimal * 0.7:
                urgence = Urgence.FAIBLE
                quantite_a_commander = stock_optimal - quantite_actuelle
                raison = "Réapprovisionnement préventif"

        # Pas de réapprovisionnement nécessaire
        if urgence is None:
            return None

        # Estimer les jours avant rupture
        estimation = self.prediction_engine.estimer_rupture_stock(article.id)
        jours_avant_rupture = estimation["jours_restants"] if estimation else None

        # Coût estimé
        cout_estime = quantite_a_commander * article.prix_achat

        return RecommandationReappro(
            article_id=article.id,
            article_nom=article.nom,
            article_reference=article.reference,
            quantite_actuelle=quantite_actuelle,
            seuil_critique=seuil_critique,
            stock_optimal=stock_optimal,
            quantite_recommandee=quantite_a_commander,
            urgence=urgence,
            jours_avant_rupture=jours_avant_rupture,
            cout_estime=cout_estime,
            fournisseur=article.fournisseur,
            delai_jours=article.delai_reappro_jours,
            raison=raison
        )

    def calculer_quantite_optimale(self, article_id: str,
                                   methode: str = "stock_optimal") -> int:
        """
        Calcule la quantité optimale à commander.

        Méthodes disponibles:
        - "stock_optimal": Ramener au stock optimal
        - "eoq": Economic Order Quantity (formule Wilson)
        - "min_max": Entre min et max

        Args:
            article_id: ID de l'article
            methode: Méthode de calcul

        Returns:
            Quantité optimale à commander
        """
        article = self.inventaire.obtenir_article(article_id)
        if not article:
            return 0

        if methode == "stock_optimal":
            # Simple : ramener au stock optimal
            return max(0, article.stock_optimal - article.quantite)

        elif methode == "eoq":
            # Economic Order Quantity (formule de Wilson)
            # EOQ = sqrt((2 × demande annuelle × coût commande) / coût stockage)
            # Simplifié ici
            demande_annuelle = article.ventes_jour * 365
            if demande_annuelle <= 0:
                return article.stock_optimal

            # Estimation du coût de commande (fixe par commande)
            cout_commande = 50  # €
            # Estimation du coût de stockage (% du prix d'achat)
            cout_stockage = article.prix_achat * 0.25  # 25% par an

            if cout_stockage <= 0:
                return article.stock_optimal

            eoq = ((2 * demande_annuelle * cout_commande) / cout_stockage) ** 0.5
            return int(eoq)

        elif methode == "min_max":
            # Politique min-max
            return max(0, article.stock_optimal - article.quantite)

        return article.stock_optimal

    def generer_bons_commande(self,
                             recommandations: List[RecommandationReappro] = None,
                             grouper_par_fournisseur: bool = True) -> List[BonCommande]:
        """
        Génère des bons de commande à partir des recommandations.

        Args:
            recommandations: Liste de recommandations (ou auto-généré)
            grouper_par_fournisseur: Grouper les articles par fournisseur

        Returns:
            Liste de bons de commande
        """
        if recommandations is None:
            recommandations = self.generer_recommandations(inclure_preventif=False)

        if not grouper_par_fournisseur:
            # Un bon par article
            bons = []
            for reco in recommandations:
                bon = BonCommande(
                    fournisseur=reco.fournisseur,
                    date_creation=datetime.now().isoformat(),
                    articles=[{
                        "article_id": reco.article_id,
                        "nom": reco.article_nom,
                        "reference": reco.article_reference,
                        "quantite": reco.quantite_recommandee,
                        "prix_unitaire": reco.cout_estime / reco.quantite_recommandee if reco.quantite_recommandee > 0 else 0,
                        "total": reco.cout_estime
                    }],
                    total_quantite=reco.quantite_recommandee,
                    total_cout=reco.cout_estime,
                    urgence_max=reco.urgence
                )
                bons.append(bon)
            return bons

        # Grouper par fournisseur
        par_fournisseur = {}

        for reco in recommandations:
            fournisseur = reco.fournisseur or "Fournisseur inconnu"

            if fournisseur not in par_fournisseur:
                par_fournisseur[fournisseur] = {
                    "articles": [],
                    "total_quantite": 0,
                    "total_cout": 0,
                    "urgence_max": Urgence.FAIBLE
                }

            article_info = {
                "article_id": reco.article_id,
                "nom": reco.article_nom,
                "reference": reco.article_reference,
                "quantite": reco.quantite_recommandee,
                "prix_unitaire": reco.cout_estime / reco.quantite_recommandee if reco.quantite_recommandee > 0 else 0,
                "total": reco.cout_estime,
                "urgence": reco.urgence.name
            }

            par_fournisseur[fournisseur]["articles"].append(article_info)
            par_fournisseur[fournisseur]["total_quantite"] += reco.quantite_recommandee
            par_fournisseur[fournisseur]["total_cout"] += reco.cout_estime

            # Garder l'urgence maximale
            if reco.urgence.value < par_fournisseur[fournisseur]["urgence_max"].value:
                par_fournisseur[fournisseur]["urgence_max"] = reco.urgence

        # Créer les bons de commande
        bons = []
        for fournisseur, data in par_fournisseur.items():
            bon = BonCommande(
                fournisseur=fournisseur,
                date_creation=datetime.now().isoformat(),
                articles=data["articles"],
                total_quantite=data["total_quantite"],
                total_cout=data["total_cout"],
                urgence_max=data["urgence_max"]
            )
            bons.append(bon)

        # Trier par urgence
        bons.sort(key=lambda b: b.urgence_max.value)

        return bons

    def formater_bon_commande(self, bon: BonCommande) -> str:
        """
        Formate un bon de commande en texte.

        Returns:
            Bon de commande formaté
        """
        texte = "\n" + "=" * 80 + "\n"
        texte += f"                    BON DE COMMANDE N° {bon.numero}\n"
        texte += "=" * 80 + "\n\n"

        texte += f"Fournisseur: {bon.fournisseur}\n"
        texte += f"Date:        {datetime.fromisoformat(bon.date_creation).strftime('%d/%m/%Y %H:%M')}\n"
        texte += f"Urgence:     {bon.urgence_max.name} {'🔴' if bon.urgence_max == Urgence.CRITIQUE else '🟠' if bon.urgence_max == Urgence.ELEVEE else '🟡'}\n\n"

        texte += "-" * 80 + "\n"
        texte += f"{'Réf.':15} {'Article':35} {'Qté':>8} {'P.U.':>10} {'Total':>10}\n"
        texte += "-" * 80 + "\n"

        for article in bon.articles:
            texte += f"{article['reference'][:15]:15} "
            texte += f"{article['nom'][:35]:35} "
            texte += f"{article['quantite']:8} "
            texte += f"{article['prix_unitaire']:10.2f} € "
            texte += f"{article['total']:10.2f} €\n"

        texte += "-" * 80 + "\n"
        texte += f"{'TOTAL':60} {bon.total_quantite:8} {'':10} {bon.total_cout:10.2f} €\n"
        texte += "=" * 80 + "\n"

        return texte

    def generer_rapport_reappro(self, recommandations: List[RecommandationReappro] = None) -> str:
        """
        Génère un rapport texte des recommandations de réapprovisionnement.

        Returns:
            Rapport formaté
        """
        if recommandations is None:
            recommandations = self.generer_recommandations(inclure_preventif=False)

        if not recommandations:
            return "✅ Aucun réapprovisionnement nécessaire.\n"

        texte = "\n" + "=" * 80 + "\n"
        texte += "              RAPPORT DE RÉAPPROVISIONNEMENT\n"
        texte += "=" * 80 + "\n\n"

        # Grouper par urgence
        par_urgence = {u: [] for u in Urgence}
        for reco in recommandations:
            par_urgence[reco.urgence].append(reco)

        icones = {
            Urgence.CRITIQUE: "🔴",
            Urgence.ELEVEE: "🟠",
            Urgence.MOYENNE: "🟡",
            Urgence.FAIBLE: "🔵"
        }

        for urgence in [Urgence.CRITIQUE, Urgence.ELEVEE, Urgence.MOYENNE, Urgence.FAIBLE]:
            recos = par_urgence[urgence]
            if not recos:
                continue

            texte += f"\n{icones[urgence]} {urgence.name} ({len(recos)} article(s))\n"
            texte += "-" * 80 + "\n"

            for reco in recos:
                texte += f"\n📦 {reco.article_nom} ({reco.article_reference})\n"
                texte += f"   Stock actuel:  {reco.quantite_actuelle} (seuil: {reco.seuil_critique})\n"
                texte += f"   À commander:   {reco.quantite_recommandee} unités\n"
                texte += f"   Coût estimé:   {reco.cout_estime:.2f} €\n"
                texte += f"   Fournisseur:   {reco.fournisseur} (délai: {reco.delai_jours}j)\n"

                if reco.jours_avant_rupture is not None:
                    texte += f"   ⚠️  Rupture dans: {reco.jours_avant_rupture} jours\n"

                texte += f"   Raison:        {reco.raison}\n"

        # Résumé
        texte += "\n" + "=" * 80 + "\n"
        texte += "RÉSUMÉ\n"
        texte += "-" * 80 + "\n"
        texte += f"Total articles à commander: {len(recommandations)}\n"
        texte += f"Coût total estimé:          {sum(r.cout_estime for r in recommandations):.2f} €\n"
        texte += "=" * 80 + "\n"

        return texte
