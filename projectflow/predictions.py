"""
Module predictions - Prévisions intelligentes et détection d'anomalies.

Ce module fournit :
- Calcul automatique des seuils d'alerte
- Prévisions de ventes (moyenne glissante, tendance)
- Détection d'anomalies dans le stock
- Estimation des ruptures de stock
- Recommandations de réapprovisionnement
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics


@dataclass
class Prevision:
    """Résultat d'une prévision de ventes."""

    article_id: str
    article_nom: str
    ventes_jour_moyenne: float
    ventes_semaine_prevue: float
    ventes_mois_prevue: float
    tendance: str  # "hausse", "baisse", "stable"
    tendance_pourcentage: float
    confiance: float  # 0-100%


@dataclass
class Anomalie:
    """Représente une anomalie détectée."""

    article_id: str
    article_nom: str
    type: str  # "stock_negatif", "variation_brutale", "inactivite", "surstock"
    severite: str  # "critique", "elevee", "moyenne", "faible"
    message: str
    valeur_actuelle: float
    valeur_attendue: Optional[float] = None
    date_detection: str = ""

    def __post_init__(self):
        if not self.date_detection:
            self.date_detection = datetime.now().isoformat()


class PredictionEngine:
    """Moteur de prévisions et d'analyse intelligent."""

    def __init__(self, inventaire):
        """
        Initialise le moteur de prévisions.

        Args:
            inventaire: Instance de la classe Inventaire
        """
        self.inventaire = inventaire

    def calculer_seuil_automatique(self, article_id: str,
                                   marge_securite: float = 1.5) -> Optional[int]:
        """
        Calcule le seuil minimum automatique pour un article.

        Formule : seuil = (ventes_jour_moyenne × délai_réappro) × marge_sécurité

        Args:
            article_id: ID de l'article
            marge_securite: Multiplicateur de sécurité (défaut 1.5)

        Returns:
            Seuil calculé ou None si pas assez de données
        """
        article = self.inventaire.obtenir_article(article_id)
        if not article:
            return None

        # Calculer les ventes moyennes par jour
        ventes_jour = self.calculer_ventes_moyennes_jour(article_id, jours=30)
        if ventes_jour <= 0:
            # Pas de ventes = seuil par défaut
            return max(1, int(article.stock_optimal * 0.1))

        # Formule : ventes/jour × délai + marge de sécurité
        delai = article.delai_reappro_jours
        seuil = int((ventes_jour * delai) * marge_securite)

        # Minimum 1, maximum stock optimal
        return max(1, min(seuil, article.stock_optimal))

    def calculer_ventes_moyennes_jour(self, article_id: str, jours: int = 30) -> float:
        """
        Calcule la moyenne des ventes par jour sur une période.

        Args:
            article_id: ID de l'article
            jours: Nombre de jours à analyser

        Returns:
            Ventes moyennes par jour
        """
        date_debut = (datetime.now() - timedelta(days=jours)).isoformat()
        date_fin = datetime.now().isoformat()

        mouvements = self.inventaire.obtenir_mouvements_periode(date_debut, date_fin)

        # Filtrer les ventes de cet article
        ventes = [
            m.quantite for m in mouvements
            if m.article_id == article_id and m.type == "sortie" and m.motif == "vente"
        ]

        if not ventes:
            return 0.0

        total_ventes = sum(ventes)
        return total_ventes / jours

    def prevoir_ventes(self, article_id: str, jours_analyse: int = 30) -> Optional[Prevision]:
        """
        Prévoit les ventes futures d'un article.

        Args:
            article_id: ID de l'article
            jours_analyse: Période d'analyse en jours

        Returns:
            Objet Prevision ou None
        """
        article = self.inventaire.obtenir_article(article_id)
        if not article:
            return None

        # Calculer les ventes moyennes
        ventes_jour = self.calculer_ventes_moyennes_jour(article_id, jours_analyse)

        # Calculer la tendance (comparer première moitié vs seconde moitié)
        tendance, tendance_pct = self._calculer_tendance(article_id, jours_analyse)

        # Confiance basée sur le nombre de ventes
        mouvements = self.inventaire.obtenir_mouvements_article(article_id)
        ventes = [m for m in mouvements if m.type == "sortie" and m.motif == "vente"]
        confiance = min(100, len(ventes) * 5)  # 5% par vente, max 100%

        return Prevision(
            article_id=article_id,
            article_nom=article.nom,
            ventes_jour_moyenne=ventes_jour,
            ventes_semaine_prevue=ventes_jour * 7,
            ventes_mois_prevue=ventes_jour * 30,
            tendance=tendance,
            tendance_pourcentage=tendance_pct,
            confiance=confiance
        )

    def _calculer_tendance(self, article_id: str, jours: int = 30) -> Tuple[str, float]:
        """
        Calcule la tendance des ventes (hausse/baisse/stable).

        Returns:
            Tuple (tendance, pourcentage)
        """
        milieu = jours // 2
        date_milieu = (datetime.now() - timedelta(days=milieu)).isoformat()
        date_debut = (datetime.now() - timedelta(days=jours)).isoformat()
        date_fin = datetime.now().isoformat()

        # Ventes première moitié
        mouvements_debut = self.inventaire.obtenir_mouvements_periode(date_debut, date_milieu)
        ventes_debut = sum(
            m.quantite for m in mouvements_debut
            if m.article_id == article_id and m.type == "sortie" and m.motif == "vente"
        )

        # Ventes seconde moitié
        mouvements_fin = self.inventaire.obtenir_mouvements_periode(date_milieu, date_fin)
        ventes_fin = sum(
            m.quantite for m in mouvements_fin
            if m.article_id == article_id and m.type == "sortie" and m.motif == "vente"
        )

        if ventes_debut == 0:
            return "stable", 0.0

        # Calcul du pourcentage de variation
        variation = ((ventes_fin - ventes_debut) / ventes_debut) * 100

        if variation > 10:
            return "hausse", variation
        elif variation < -10:
            return "baisse", variation
        else:
            return "stable", variation

    def detecter_anomalies(self) -> List[Anomalie]:
        """
        Détecte les anomalies sur tous les articles.

        Returns:
            Liste des anomalies détectées
        """
        anomalies = []

        for article in self.inventaire.articles:
            # 1. Stock négatif
            if article.quantite < 0:
                anomalies.append(Anomalie(
                    article_id=article.id,
                    article_nom=article.nom,
                    type="stock_negatif",
                    severite="critique",
                    message=f"Stock négatif détecté : {article.quantite} unités",
                    valeur_actuelle=article.quantite,
                    valeur_attendue=0
                ))

            # 2. Rupture de stock
            if article.quantite == 0 and article.actif:
                anomalies.append(Anomalie(
                    article_id=article.id,
                    article_nom=article.nom,
                    type="rupture_stock",
                    severite="critique",
                    message="Article en rupture de stock",
                    valeur_actuelle=0,
                    valeur_attendue=article.seuil_critique
                ))

            # 3. Stock critique (sous le seuil)
            if 0 < article.quantite <= article.seuil_critique:
                jours = article.jours_avant_rupture
                msg = f"Stock critique : {article.quantite} unités"
                if jours:
                    msg += f" (rupture prévue dans {jours} jours)"

                anomalies.append(Anomalie(
                    article_id=article.id,
                    article_nom=article.nom,
                    type="stock_critique",
                    severite="elevee",
                    message=msg,
                    valeur_actuelle=article.quantite,
                    valeur_attendue=article.seuil_critique
                ))

            # 4. Surstock
            if article.quantite > article.stock_optimal * 1.5:
                anomalies.append(Anomalie(
                    article_id=article.id,
                    article_nom=article.nom,
                    type="surstock",
                    severite="moyenne",
                    message=f"Surstock détecté : {article.quantite} unités (optimal: {article.stock_optimal})",
                    valeur_actuelle=article.quantite,
                    valeur_attendue=article.stock_optimal
                ))

            # 5. Inactivité (aucune vente récente)
            mouvements = self.inventaire.obtenir_mouvements_article(article.id, limite=10)
            ventes = [m for m in mouvements if m.type == "sortie" and m.motif == "vente"]

            if not ventes and article.quantite > 0:
                anomalies.append(Anomalie(
                    article_id=article.id,
                    article_nom=article.nom,
                    type="inactivite",
                    severite="faible",
                    message="Aucune vente enregistrée (article mort ?)",
                    valeur_actuelle=0
                ))

            # 6. Variation brutale (détection simplifiée)
            if len(mouvements) >= 2:
                dernier = mouvements[0]
                avant_dernier = mouvements[1]

                if dernier.type == "sortie" and avant_dernier.type == "sortie":
                    if dernier.quantite > avant_dernier.quantite * 3:
                        anomalies.append(Anomalie(
                            article_id=article.id,
                            article_nom=article.nom,
                            type="variation_brutale",
                            severite="moyenne",
                            message=f"Pic de ventes inhabituel : {dernier.quantite} unités",
                            valeur_actuelle=dernier.quantite,
                            valeur_attendue=avant_dernier.quantite
                        ))

        return anomalies

    def mettre_a_jour_statistiques_article(self, article_id: str):
        """
        Met à jour les statistiques calculées d'un article.

        Met à jour :
        - ventes_jour (moyenne sur 30 jours)
        - rotation_stock (nombre de fois que le stock tourne par an)
        - seuil_min_auto (seuil calculé automatiquement)
        """
        article = self.inventaire.obtenir_article(article_id)
        if not article:
            return

        # Ventes moyennes par jour
        article.ventes_jour = self.calculer_ventes_moyennes_jour(article_id, jours=30)

        # Rotation du stock
        ventes_annuelles = article.ventes_jour * 365
        if article.quantite > 0:
            article.rotation_stock = ventes_annuelles / article.quantite
        else:
            article.rotation_stock = 0.0

        # Seuil automatique
        article.seuil_min_auto = self.calculer_seuil_automatique(article_id)

        article.date_modification = datetime.now().isoformat()

    def mettre_a_jour_tous_les_articles(self):
        """Met à jour les statistiques de tous les articles."""
        for article in self.inventaire.articles:
            self.mettre_a_jour_statistiques_article(article.id)

    def generer_rapport_anomalies(self) -> str:
        """
        Génère un rapport texte des anomalies.

        Returns:
            Rapport formaté
        """
        anomalies = self.detecter_anomalies()

        if not anomalies:
            return "✅ Aucune anomalie détectée.\n"

        rapport = f"⚠️  {len(anomalies)} anomalie(s) détectée(s)\n"
        rapport += "=" * 60 + "\n\n"

        # Grouper par sévérité
        par_severite = {"critique": [], "elevee": [], "moyenne": [], "faible": []}
        for anomalie in anomalies:
            par_severite[anomalie.severite].append(anomalie)

        icones = {
            "critique": "🔴",
            "elevee": "🟠",
            "moyenne": "🟡",
            "faible": "🔵"
        }

        for severite in ["critique", "elevee", "moyenne", "faible"]:
            anomalies_sev = par_severite[severite]
            if anomalies_sev:
                rapport += f"\n{icones[severite]} {severite.upper()} ({len(anomalies_sev)})\n"
                rapport += "-" * 60 + "\n"
                for anom in anomalies_sev:
                    rapport += f"• {anom.article_nom}\n"
                    rapport += f"  {anom.message}\n"
                    rapport += f"  Type: {anom.type}\n\n"

        return rapport

    def estimer_rupture_stock(self, article_id: str) -> Optional[dict]:
        """
        Estime quand un article sera en rupture de stock.

        Returns:
            Dictionnaire avec les détails de l'estimation
        """
        article = self.inventaire.obtenir_article(article_id)
        if not article:
            return None

        ventes_jour = self.calculer_ventes_moyennes_jour(article_id, jours=30)

        if ventes_jour <= 0:
            return {
                "article_id": article_id,
                "article_nom": article.nom,
                "rupture_prevue": False,
                "jours_restants": None,
                "date_rupture": None,
                "message": "Aucune vente enregistrée, impossible d'estimer"
            }

        jours_restants = int(article.quantite / ventes_jour)
        date_rupture = datetime.now() + timedelta(days=jours_restants)

        return {
            "article_id": article_id,
            "article_nom": article.nom,
            "quantite_actuelle": article.quantite,
            "ventes_jour": round(ventes_jour, 2),
            "rupture_prevue": True,
            "jours_restants": jours_restants,
            "date_rupture": date_rupture.strftime("%Y-%m-%d"),
            "message": f"Rupture prévue dans {jours_restants} jours ({date_rupture.strftime('%d/%m/%Y')})"
        }
