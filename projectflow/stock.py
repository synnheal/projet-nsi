"""
Module stock - Gestion intelligente des articles et inventaire.

Ce module fournit :
- Gestion complète des articles (création, modification, suppression)
- Suivi des mouvements de stock (entrées/sorties)
- Calcul automatique des seuils d'alerte
- Catégorisation intelligente des articles
- Historique des mouvements
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import uuid


# Catégories d'articles prédéfinies
CATEGORIES_ARTICLES = {
    "electronique": {"nom": "Électronique", "icone": "💻", "couleur": "#4361ee"},
    "vetements": {"nom": "Vêtements", "icone": "👕", "couleur": "#06d6a0"},
    "alimentaire": {"nom": "Alimentaire", "icone": "🍽️", "couleur": "#ffd166"},
    "cosmetique": {"nom": "Cosmétique", "icone": "💄", "couleur": "#ef476f"},
    "papeterie": {"nom": "Papeterie", "icone": "📝", "couleur": "#7209b7"},
    "sport": {"nom": "Sport", "icone": "⚽", "couleur": "#00b4d8"},
    "maison": {"nom": "Maison", "icone": "🏠", "couleur": "#fb8500"},
    "jouets": {"nom": "Jouets", "icone": "🧸", "couleur": "#ff006e"},
    "livres": {"nom": "Livres", "icone": "📚", "couleur": "#38b000"},
    "autres": {"nom": "Autres", "icone": "📦", "couleur": "#718096"}
}


@dataclass
class Mouvement:
    """Représente un mouvement de stock (entrée ou sortie)."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str = ""
    type: str = "sortie"  # "entree", "sortie", "correction", "inventaire"
    quantite: int = 0
    date: str = field(default_factory=lambda: datetime.now().isoformat())
    prix_unitaire: float = 0.0
    motif: str = ""  # "vente", "reappro", "retour", "perte", "correction"
    utilisateur: str = ""
    commentaire: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "article_id": self.article_id,
            "type": self.type,
            "quantite": self.quantite,
            "date": self.date,
            "prix_unitaire": self.prix_unitaire,
            "motif": self.motif,
            "utilisateur": self.utilisateur,
            "commentaire": self.commentaire
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Mouvement':
        return cls(**data)


@dataclass
class Article:
    """Représente un article en stock."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nom: str = ""
    reference: str = ""  # SKU/Code barre
    categorie: str = "autres"

    # Stock
    quantite: int = 0
    seuil_min: Optional[int] = None  # Seuil manuel
    seuil_min_auto: Optional[int] = None  # Seuil calculé automatiquement
    stock_optimal: int = 100

    # Prix
    prix_achat: float = 0.0
    prix_vente: float = 0.0

    # Fournisseur
    fournisseur: str = ""
    delai_reappro_jours: int = 7  # Délai de réapprovisionnement en jours

    # Métadonnées
    date_creation: str = field(default_factory=lambda: datetime.now().isoformat())
    date_modification: str = field(default_factory=lambda: datetime.now().isoformat())
    actif: bool = True
    emplacement: str = ""  # Allée, rayon, etc.

    # Statistiques (calculées)
    ventes_jour: float = 0.0  # Moyenne des ventes par jour
    rotation_stock: float = 0.0  # Nombre de fois que le stock tourne par an

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nom": self.nom,
            "reference": self.reference,
            "categorie": self.categorie,
            "quantite": self.quantite,
            "seuil_min": self.seuil_min,
            "seuil_min_auto": self.seuil_min_auto,
            "stock_optimal": self.stock_optimal,
            "prix_achat": self.prix_achat,
            "prix_vente": self.prix_vente,
            "fournisseur": self.fournisseur,
            "delai_reappro_jours": self.delai_reappro_jours,
            "date_creation": self.date_creation,
            "date_modification": self.date_modification,
            "actif": self.actif,
            "emplacement": self.emplacement,
            "ventes_jour": self.ventes_jour,
            "rotation_stock": self.rotation_stock
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        return cls(**data)

    @property
    def marge_unitaire(self) -> float:
        """Marge bénéficiaire unitaire."""
        return self.prix_vente - self.prix_achat

    @property
    def taux_marge(self) -> float:
        """Taux de marge en pourcentage."""
        if self.prix_achat <= 0:
            return 0
        return (self.marge_unitaire / self.prix_achat) * 100

    @property
    def valeur_stock(self) -> float:
        """Valeur totale du stock de cet article (au prix d'achat)."""
        return self.quantite * self.prix_achat

    @property
    def valeur_vente_potentielle(self) -> float:
        """Valeur potentielle si tout le stock est vendu."""
        return self.quantite * self.prix_vente

    @property
    def seuil_critique(self) -> int:
        """Retourne le seuil d'alerte (auto si disponible, sinon manuel)."""
        if self.seuil_min_auto is not None:
            return self.seuil_min_auto
        if self.seuil_min is not None:
            return self.seuil_min
        # Seuil par défaut : 10% du stock optimal
        return max(1, int(self.stock_optimal * 0.1))

    @property
    def statut_stock(self) -> str:
        """Retourne le statut du stock : critique, faible, moyen, bon."""
        seuil = self.seuil_critique
        if self.quantite <= 0:
            return "rupture"
        elif self.quantite <= seuil:
            return "critique"
        elif self.quantite <= seuil * 2:
            return "faible"
        elif self.quantite >= self.stock_optimal * 1.2:
            return "surstock"
        else:
            return "bon"

    @property
    def jours_avant_rupture(self) -> Optional[int]:
        """Estime le nombre de jours avant rupture de stock."""
        if self.ventes_jour <= 0:
            return None
        return int(self.quantite / self.ventes_jour)


class Inventaire:
    """Gestion d'un inventaire complet."""

    def __init__(self, nom: str = "Mon Inventaire"):
        self.id = str(uuid.uuid4())
        self.nom = nom
        self.articles: List[Article] = []
        self.mouvements: List[Mouvement] = []
        self.date_creation = datetime.now().isoformat()
        self.date_modification = datetime.now().isoformat()

    def ajouter_article(self, article: Article) -> Article:
        """Ajoute un nouvel article."""
        self.articles.append(article)
        self._maj_date()
        return article

    def supprimer_article(self, article_id: str) -> bool:
        """Supprime un article."""
        self.articles = [a for a in self.articles if a.id != article_id]
        # Supprimer aussi les mouvements associés
        self.mouvements = [m for m in self.mouvements if m.article_id != article_id]
        self._maj_date()
        return True

    def obtenir_article(self, article_id: str) -> Optional[Article]:
        """Récupère un article par son ID."""
        for article in self.articles:
            if article.id == article_id:
                return article
        return None

    def rechercher_articles(self, terme: str) -> List[Article]:
        """Recherche des articles par nom ou référence."""
        terme = terme.lower()
        return [
            a for a in self.articles
            if terme in a.nom.lower() or terme in a.reference.lower()
        ]

    def filtrer_par_categorie(self, categorie: str) -> List[Article]:
        """Filtre les articles par catégorie."""
        return [a for a in self.articles if a.categorie == categorie]

    def filtrer_par_statut(self, statut: str) -> List[Article]:
        """Filtre les articles par statut de stock."""
        return [a for a in self.articles if a.statut_stock == statut]

    def enregistrer_mouvement(self, mouvement: Mouvement) -> Mouvement:
        """Enregistre un mouvement et met à jour le stock."""
        article = self.obtenir_article(mouvement.article_id)
        if not article:
            raise ValueError(f"Article {mouvement.article_id} introuvable")

        # Mettre à jour la quantité
        if mouvement.type == "entree":
            article.quantite += mouvement.quantite
        elif mouvement.type == "sortie":
            article.quantite -= mouvement.quantite
            if article.quantite < 0:
                raise ValueError(f"Stock insuffisant pour {article.nom}")
        elif mouvement.type == "correction":
            # Correction = nouvelle quantité absolue
            article.quantite = mouvement.quantite
        elif mouvement.type == "inventaire":
            # Inventaire physique = ajustement
            article.quantite = mouvement.quantite

        article.date_modification = datetime.now().isoformat()
        self.mouvements.append(mouvement)
        self._maj_date()

        return mouvement

    def ajouter_stock(self, article_id: str, quantite: int, prix_unitaire: float = 0,
                     motif: str = "reappro", commentaire: str = "") -> Mouvement:
        """Ajoute du stock (entrée)."""
        mouvement = Mouvement(
            article_id=article_id,
            type="entree",
            quantite=quantite,
            prix_unitaire=prix_unitaire,
            motif=motif,
            commentaire=commentaire
        )
        return self.enregistrer_mouvement(mouvement)

    def retirer_stock(self, article_id: str, quantite: int, prix_unitaire: float = 0,
                     motif: str = "vente", commentaire: str = "") -> Mouvement:
        """Retire du stock (sortie)."""
        mouvement = Mouvement(
            article_id=article_id,
            type="sortie",
            quantite=quantite,
            prix_unitaire=prix_unitaire,
            motif=motif,
            commentaire=commentaire
        )
        return self.enregistrer_mouvement(mouvement)

    def obtenir_mouvements_article(self, article_id: str,
                                   limite: int = None) -> List[Mouvement]:
        """Récupère les mouvements d'un article."""
        mouvements = [m for m in self.mouvements if m.article_id == article_id]
        mouvements.sort(key=lambda m: m.date, reverse=True)
        if limite:
            return mouvements[:limite]
        return mouvements

    def obtenir_mouvements_periode(self, date_debut: str,
                                   date_fin: str) -> List[Mouvement]:
        """Récupère les mouvements sur une période."""
        return [
            m for m in self.mouvements
            if date_debut <= m.date <= date_fin
        ]

    def calculer_statistiques_globales(self) -> dict:
        """Calcule les statistiques globales de l'inventaire."""
        total_articles = len(self.articles)
        articles_actifs = len([a for a in self.articles if a.actif])

        valeur_stock_total = sum(a.valeur_stock for a in self.articles)
        valeur_vente_potentielle = sum(a.valeur_vente_potentielle for a in self.articles)

        # Répartition par statut
        par_statut = {}
        for statut in ["rupture", "critique", "faible", "bon", "surstock"]:
            par_statut[statut] = len(self.filtrer_par_statut(statut))

        # Répartition par catégorie
        par_categorie = {}
        for categorie in CATEGORIES_ARTICLES.keys():
            articles_cat = self.filtrer_par_categorie(categorie)
            if articles_cat:
                par_categorie[categorie] = {
                    "nombre": len(articles_cat),
                    "valeur": sum(a.valeur_stock for a in articles_cat)
                }

        return {
            "total_articles": total_articles,
            "articles_actifs": articles_actifs,
            "valeur_stock_total": valeur_stock_total,
            "valeur_vente_potentielle": valeur_vente_potentielle,
            "marge_potentielle": valeur_vente_potentielle - valeur_stock_total,
            "par_statut": par_statut,
            "par_categorie": par_categorie,
            "total_mouvements": len(self.mouvements)
        }

    def _maj_date(self):
        """Met à jour la date de modification."""
        self.date_modification = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convertit l'inventaire en dictionnaire."""
        return {
            "id": self.id,
            "nom": self.nom,
            "date_creation": self.date_creation,
            "date_modification": self.date_modification,
            "articles": [a.to_dict() for a in self.articles],
            "mouvements": [m.to_dict() for m in self.mouvements]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Inventaire':
        """Crée un inventaire depuis un dictionnaire."""
        inventaire = cls(nom=data.get("nom", "Mon Inventaire"))
        inventaire.id = data.get("id", inventaire.id)
        inventaire.date_creation = data.get("date_creation", inventaire.date_creation)
        inventaire.date_modification = data.get("date_modification", inventaire.date_modification)

        # Charger les articles
        for article_data in data.get("articles", []):
            inventaire.articles.append(Article.from_dict(article_data))

        # Charger les mouvements
        for mouvement_data in data.get("mouvements", []):
            inventaire.mouvements.append(Mouvement.from_dict(mouvement_data))

        return inventaire


def creer_article_exemple() -> Article:
    """Crée un article d'exemple pour les tests."""
    return Article(
        nom="Ordinateur Portable HP",
        reference="HP-LT-001",
        categorie="electronique",
        quantite=15,
        seuil_min=5,
        stock_optimal=25,
        prix_achat=450.0,
        prix_vente=699.0,
        fournisseur="TechDistrib",
        delai_reappro_jours=5,
        emplacement="A-12-3"
    )
