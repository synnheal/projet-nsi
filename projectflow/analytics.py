"""
Module analytics - Analyses financières et statistiques avancées.

Ce module fournit :
- Calculs de valeur de stock
- Analyses de rotation des stocks
- Calculs de marges et rentabilité
- Statistiques par catégorie
- Tableaux de bord financiers
- Analyses de performance
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics


@dataclass
class RapportFinancier:
    """Rapport financier complet d'un inventaire."""

    # Valeurs globales
    valeur_stock_total: float
    valeur_achat_total: float
    valeur_vente_potentielle: float
    marge_potentielle: float
    taux_marge_moyen: float

    # Statistiques articles
    nombre_articles: int
    articles_actifs: int
    articles_en_rupture: int
    articles_critiques: int

    # Rotations
    rotation_moyenne: float
    articles_rotation_rapide: int  # > 12 rotations/an
    articles_rotation_lente: int  # < 4 rotations/an

    # Top performers
    top_articles_valeur: List[Dict]
    top_articles_marge: List[Dict]
    articles_morts: List[Dict]  # Aucune vente

    # Par catégorie
    stats_categories: Dict[str, Dict]


@dataclass
class AnalyseVente:
    """Analyse des ventes sur une période."""

    periode_debut: str
    periode_fin: str
    jours: int

    # Ventes
    total_ventes_quantite: int
    total_ventes_valeur: float
    moyenne_jour_quantite: float
    moyenne_jour_valeur: float

    # Articles
    articles_vendus: int
    article_plus_vendu: Optional[Dict]
    article_plus_rentable: Optional[Dict]

    # Tendances
    tendance_globale: str  # "hausse", "baisse", "stable"
    croissance_pourcentage: float


class AnalyticsEngine:
    """Moteur d'analyse financière et statistique."""

    def __init__(self, inventaire):
        """
        Initialise le moteur d'analyse.

        Args:
            inventaire: Instance de la classe Inventaire
        """
        self.inventaire = inventaire

    def generer_rapport_financier(self) -> RapportFinancier:
        """
        Génère un rapport financier complet de l'inventaire.

        Returns:
            Objet RapportFinancier avec toutes les statistiques
        """
        articles = self.inventaire.articles

        # Valeurs globales
        valeur_stock_total = sum(a.valeur_stock for a in articles)
        valeur_achat_total = sum(a.quantite * a.prix_achat for a in articles)
        valeur_vente_potentielle = sum(a.valeur_vente_potentielle for a in articles)
        marge_potentielle = valeur_vente_potentielle - valeur_achat_total

        # Taux de marge moyen
        marges = [a.taux_marge for a in articles if a.prix_achat > 0]
        taux_marge_moyen = statistics.mean(marges) if marges else 0

        # Statistiques articles
        nombre_articles = len(articles)
        articles_actifs = len([a for a in articles if a.actif])
        articles_en_rupture = len([a for a in articles if a.quantite == 0])
        articles_critiques = len([a for a in articles if a.statut_stock == "critique"])

        # Rotations
        rotations = [a.rotation_stock for a in articles if a.rotation_stock > 0]
        rotation_moyenne = statistics.mean(rotations) if rotations else 0
        articles_rotation_rapide = len([a for a in articles if a.rotation_stock > 12])
        articles_rotation_lente = len([a for a in articles if 0 < a.rotation_stock < 4])

        # Top articles par valeur
        top_valeur = sorted(articles, key=lambda a: a.valeur_stock, reverse=True)[:5]
        top_articles_valeur = [
            {
                "id": a.id,
                "nom": a.nom,
                "valeur": a.valeur_stock,
                "quantite": a.quantite
            }
            for a in top_valeur
        ]

        # Top articles par marge
        top_marge = sorted(articles, key=lambda a: a.marge_unitaire * a.quantite, reverse=True)[:5]
        top_articles_marge = [
            {
                "id": a.id,
                "nom": a.nom,
                "marge_totale": a.marge_unitaire * a.quantite,
                "taux_marge": a.taux_marge
            }
            for a in top_marge
        ]

        # Articles morts (aucune vente)
        articles_morts_list = []
        for article in articles:
            mouvements = self.inventaire.obtenir_mouvements_article(article.id)
            ventes = [m for m in mouvements if m.type == "sortie" and m.motif == "vente"]
            if not ventes and article.quantite > 0:
                articles_morts_list.append({
                    "id": article.id,
                    "nom": article.nom,
                    "quantite": article.quantite,
                    "valeur_bloquee": article.valeur_stock
                })

        # Stats par catégorie
        stats_categories = self._calculer_stats_categories()

        return RapportFinancier(
            valeur_stock_total=valeur_stock_total,
            valeur_achat_total=valeur_achat_total,
            valeur_vente_potentielle=valeur_vente_potentielle,
            marge_potentielle=marge_potentielle,
            taux_marge_moyen=taux_marge_moyen,
            nombre_articles=nombre_articles,
            articles_actifs=articles_actifs,
            articles_en_rupture=articles_en_rupture,
            articles_critiques=articles_critiques,
            rotation_moyenne=rotation_moyenne,
            articles_rotation_rapide=articles_rotation_rapide,
            articles_rotation_lente=articles_rotation_lente,
            top_articles_valeur=top_articles_valeur,
            top_articles_marge=top_articles_marge,
            articles_morts=articles_morts_list[:10],
            stats_categories=stats_categories
        )

    def _calculer_stats_categories(self) -> Dict[str, Dict]:
        """Calcule les statistiques par catégorie."""
        from .stock import CATEGORIES_ARTICLES

        stats = {}

        for cat_id, cat_info in CATEGORIES_ARTICLES.items():
            articles_cat = self.inventaire.filtrer_par_categorie(cat_id)

            if not articles_cat:
                continue

            valeur_stock = sum(a.valeur_stock for a in articles_cat)
            valeur_vente = sum(a.valeur_vente_potentielle for a in articles_cat)
            marge = valeur_vente - valeur_stock

            stats[cat_id] = {
                "nom": cat_info["nom"],
                "icone": cat_info["icone"],
                "couleur": cat_info["couleur"],
                "nombre_articles": len(articles_cat),
                "valeur_stock": valeur_stock,
                "valeur_vente_potentielle": valeur_vente,
                "marge_potentielle": marge,
                "pourcentage_total": 0  # Sera calculé après
            }

        # Calculer les pourcentages
        valeur_totale = sum(s["valeur_stock"] for s in stats.values())
        if valeur_totale > 0:
            for cat_stats in stats.values():
                cat_stats["pourcentage_total"] = (cat_stats["valeur_stock"] / valeur_totale) * 100

        return stats

    def analyser_ventes(self, jours: int = 30) -> AnalyseVente:
        """
        Analyse les ventes sur une période donnée.

        Args:
            jours: Nombre de jours à analyser

        Returns:
            Objet AnalyseVente avec les statistiques
        """
        date_debut = (datetime.now() - timedelta(days=jours)).isoformat()
        date_fin = datetime.now().isoformat()

        mouvements = self.inventaire.obtenir_mouvements_periode(date_debut, date_fin)
        ventes = [m for m in mouvements if m.type == "sortie" and m.motif == "vente"]

        # Totaux
        total_ventes_quantite = sum(v.quantite for v in ventes)
        total_ventes_valeur = sum(v.quantite * v.prix_unitaire for v in ventes)
        moyenne_jour_quantite = total_ventes_quantite / jours if jours > 0 else 0
        moyenne_jour_valeur = total_ventes_valeur / jours if jours > 0 else 0

        # Articles vendus
        articles_vendus_ids = set(v.article_id for v in ventes)
        articles_vendus = len(articles_vendus_ids)

        # Article le plus vendu
        ventes_par_article = {}
        valeur_par_article = {}

        for vente in ventes:
            article_id = vente.article_id
            ventes_par_article[article_id] = ventes_par_article.get(article_id, 0) + vente.quantite
            valeur_par_article[article_id] = valeur_par_article.get(article_id, 0) + (vente.quantite * vente.prix_unitaire)

        article_plus_vendu = None
        if ventes_par_article:
            id_plus_vendu = max(ventes_par_article, key=ventes_par_article.get)
            article = self.inventaire.obtenir_article(id_plus_vendu)
            if article:
                article_plus_vendu = {
                    "id": article.id,
                    "nom": article.nom,
                    "quantite_vendue": ventes_par_article[id_plus_vendu]
                }

        # Article le plus rentable
        article_plus_rentable = None
        if valeur_par_article:
            id_plus_rentable = max(valeur_par_article, key=valeur_par_article.get)
            article = self.inventaire.obtenir_article(id_plus_rentable)
            if article:
                article_plus_rentable = {
                    "id": article.id,
                    "nom": article.nom,
                    "valeur_vendue": valeur_par_article[id_plus_rentable]
                }

        # Tendance (comparer première moitié vs seconde moitié)
        tendance, croissance = self._calculer_tendance_ventes(jours)

        return AnalyseVente(
            periode_debut=date_debut,
            periode_fin=date_fin,
            jours=jours,
            total_ventes_quantite=total_ventes_quantite,
            total_ventes_valeur=total_ventes_valeur,
            moyenne_jour_quantite=moyenne_jour_quantite,
            moyenne_jour_valeur=moyenne_jour_valeur,
            articles_vendus=articles_vendus,
            article_plus_vendu=article_plus_vendu,
            article_plus_rentable=article_plus_rentable,
            tendance_globale=tendance,
            croissance_pourcentage=croissance
        )

    def _calculer_tendance_ventes(self, jours: int) -> Tuple[str, float]:
        """Calcule la tendance globale des ventes."""
        milieu = jours // 2

        date_milieu = (datetime.now() - timedelta(days=milieu)).isoformat()
        date_debut = (datetime.now() - timedelta(days=jours)).isoformat()
        date_fin = datetime.now().isoformat()

        # Ventes première moitié
        mouvements_debut = self.inventaire.obtenir_mouvements_periode(date_debut, date_milieu)
        ventes_debut = sum(
            m.quantite for m in mouvements_debut
            if m.type == "sortie" and m.motif == "vente"
        )

        # Ventes seconde moitié
        mouvements_fin = self.inventaire.obtenir_mouvements_periode(date_milieu, date_fin)
        ventes_fin = sum(
            m.quantite for m in mouvements_fin
            if m.type == "sortie" and m.motif == "vente"
        )

        if ventes_debut == 0:
            return "stable", 0.0

        variation = ((ventes_fin - ventes_debut) / ventes_debut) * 100

        if variation > 10:
            return "hausse", variation
        elif variation < -10:
            return "baisse", variation
        else:
            return "stable", variation

    def calculer_rotation_stock(self, article_id: str, periode_jours: int = 365) -> float:
        """
        Calcule la rotation du stock pour un article.

        Rotation = Quantité vendue sur période / Stock moyen

        Args:
            article_id: ID de l'article
            periode_jours: Période en jours (défaut: 1 an)

        Returns:
            Nombre de rotations
        """
        date_debut = (datetime.now() - timedelta(days=periode_jours)).isoformat()
        date_fin = datetime.now().isoformat()

        mouvements = self.inventaire.obtenir_mouvements_periode(date_debut, date_fin)
        ventes = sum(
            m.quantite for m in mouvements
            if m.article_id == article_id and m.type == "sortie" and m.motif == "vente"
        )

        article = self.inventaire.obtenir_article(article_id)
        if not article or article.quantite == 0:
            return 0.0

        # Stock moyen simplifié (stock actuel)
        # Dans une version avancée, on calculerait la moyenne sur la période
        rotation = ventes / article.quantite

        return rotation

    def calculer_cout_stockage(self, taux_annuel: float = 0.25) -> float:
        """
        Estime le coût de stockage (immobilisation du capital).

        Args:
            taux_annuel: Taux de coût annuel (défaut 25%)

        Returns:
            Coût de stockage annuel estimé
        """
        valeur_stock = sum(a.valeur_stock for a in self.inventaire.articles)
        return valeur_stock * taux_annuel

    def identifier_articles_a_promouvoir(self, limite: int = 10) -> List[Dict]:
        """
        Identifie les articles à promouvoir (rotation lente, stock élevé).

        Returns:
            Liste des articles à promouvoir
        """
        articles_candidats = []

        for article in self.inventaire.articles:
            if not article.actif:
                continue

            # Critères : rotation lente ET stock supérieur à l'optimal
            if article.rotation_stock < 4 and article.quantite > article.stock_optimal:
                valeur_bloquee = article.valeur_stock
                articles_candidats.append({
                    "id": article.id,
                    "nom": article.nom,
                    "quantite": article.quantite,
                    "stock_optimal": article.stock_optimal,
                    "rotation": article.rotation_stock,
                    "valeur_bloquee": valeur_bloquee,
                    "score": valeur_bloquee * (1 / (article.rotation_stock + 0.1))
                })

        # Trier par score (valeur bloquée / rotation)
        articles_candidats.sort(key=lambda x: x["score"], reverse=True)

        return articles_candidats[:limite]

    def calculer_abc_analysis(self) -> Dict[str, List[Dict]]:
        """
        Effectue une analyse ABC (Pareto) sur les articles.

        A = 20% des articles représentent 80% de la valeur
        B = 30% des articles représentent 15% de la valeur
        C = 50% des articles représentent 5% de la valeur

        Returns:
            Dictionnaire avec clés A, B, C contenant les articles
        """
        # Trier par valeur décroissante
        articles_tries = sorted(
            self.inventaire.articles,
            key=lambda a: a.valeur_stock,
            reverse=True
        )

        valeur_totale = sum(a.valeur_stock for a in articles_tries)
        nb_total = len(articles_tries)

        cumul = 0
        categories = {"A": [], "B": [], "C": []}

        for i, article in enumerate(articles_tries):
            cumul += article.valeur_stock
            pct_cumul = (cumul / valeur_totale * 100) if valeur_totale > 0 else 0

            article_info = {
                "id": article.id,
                "nom": article.nom,
                "valeur_stock": article.valeur_stock,
                "pourcentage_cumul": pct_cumul
            }

            if pct_cumul <= 80:
                categories["A"].append(article_info)
            elif pct_cumul <= 95:
                categories["B"].append(article_info)
            else:
                categories["C"].append(article_info)

        return categories

    def generer_tableau_bord(self) -> str:
        """
        Génère un tableau de bord texte formaté.

        Returns:
            Tableau de bord formaté
        """
        rapport = self.generer_rapport_financier()

        texte = "\n" + "=" * 70 + "\n"
        texte += "                   TABLEAU DE BORD FINANCIER\n"
        texte += "=" * 70 + "\n\n"

        # Section 1: Vue d'ensemble
        texte += "📊 VUE D'ENSEMBLE\n"
        texte += "-" * 70 + "\n"
        texte += f"Articles totaux:          {rapport.nombre_articles}\n"
        texte += f"Articles actifs:          {rapport.articles_actifs}\n"
        texte += f"Articles en rupture:      {rapport.articles_en_rupture} 🔴\n"
        texte += f"Articles critiques:       {rapport.articles_critiques} 🟠\n\n"

        # Section 2: Valeurs
        texte += "💰 VALEURS\n"
        texte += "-" * 70 + "\n"
        texte += f"Valeur stock (achat):     {rapport.valeur_stock_total:,.2f} €\n"
        texte += f"Valeur vente potentielle: {rapport.valeur_vente_potentielle:,.2f} €\n"
        texte += f"Marge potentielle:        {rapport.marge_potentielle:,.2f} € ({rapport.taux_marge_moyen:.1f}%)\n\n"

        # Section 3: Rotations
        texte += "🔄 ROTATION DES STOCKS\n"
        texte += "-" * 70 + "\n"
        texte += f"Rotation moyenne:         {rapport.rotation_moyenne:.2f} fois/an\n"
        texte += f"Rotation rapide (>12):    {rapport.articles_rotation_rapide} articles\n"
        texte += f"Rotation lente (<4):      {rapport.articles_rotation_lente} articles\n\n"

        # Section 4: Top articles
        texte += "🏆 TOP 5 - VALEUR STOCK\n"
        texte += "-" * 70 + "\n"
        for i, art in enumerate(rapport.top_articles_valeur[:5], 1):
            texte += f"{i}. {art['nom'][:40]:40} {art['valeur']:>12,.2f} €\n"

        texte += "\n💎 TOP 5 - MARGE POTENTIELLE\n"
        texte += "-" * 70 + "\n"
        for i, art in enumerate(rapport.top_articles_marge[:5], 1):
            texte += f"{i}. {art['nom'][:40]:40} {art['marge_totale']:>12,.2f} €\n"

        if rapport.articles_morts:
            texte += "\n⚠️  ARTICLES MORTS (aucune vente)\n"
            texte += "-" * 70 + "\n"
            for art in rapport.articles_morts[:5]:
                texte += f"• {art['nom'][:50]:50} {art['valeur_bloquee']:>10,.2f} €\n"

        texte += "\n" + "=" * 70 + "\n"

        return texte
