"""
Module timeline - Journal chronologique des mouvements de stock.

Ce module fournit :
- Affichage chronologique des mouvements
- Filtres par période, type, article
- Statistiques sur les mouvements
- Export du journal
- Recherche dans l'historique
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class EntreeTimeline:
    """Entrée dans la timeline (mouvement formaté pour affichage)."""

    date: str
    heure: str
    type: str  # "entree", "sortie", "correction", "inventaire"
    article_nom: str
    article_reference: str
    quantite: int
    motif: str
    commentaire: str
    utilisateur: str
    icone: str
    couleur: str

    @property
    def date_complete(self) -> str:
        """Retourne la date complète formatée."""
        try:
            dt = datetime.fromisoformat(f"{self.date}T{self.heure}")
            return dt.strftime("%d/%m/%Y à %H:%M")
        except:
            return f"{self.date} {self.heure}"


class TimelineManager:
    """Gestionnaire de timeline pour l'historique des mouvements."""

    # Icônes et couleurs par type de mouvement
    ICONES = {
        "entree": "📥",
        "sortie": "📤",
        "correction": "✏️",
        "inventaire": "📋"
    }

    COULEURS = {
        "entree": "#06d6a0",    # Vert
        "sortie": "#ef476f",    # Rouge
        "correction": "#ffd166", # Jaune
        "inventaire": "#4361ee"  # Bleu
    }

    MOTIFS_ICONES = {
        "vente": "💰",
        "reappro": "📦",
        "retour": "↩️",
        "perte": "❌",
        "correction": "✏️",
        "inventaire": "📋",
        "ajustement": "⚙️",
        "promotion": "🎁",
        "casse": "💥"
    }

    def __init__(self, inventaire):
        """
        Initialise le gestionnaire de timeline.

        Args:
            inventaire: Instance de la classe Inventaire
        """
        self.inventaire = inventaire

    def obtenir_timeline(self,
                        limite: int = None,
                        date_debut: str = None,
                        date_fin: str = None,
                        type_filtre: str = None,
                        article_id: str = None) -> List[EntreeTimeline]:
        """
        Récupère la timeline des mouvements.

        Args:
            limite: Nombre maximum d'entrées
            date_debut: Date de début du filtre
            date_fin: Date de fin du filtre
            type_filtre: Type de mouvement ("entree", "sortie", etc.)
            article_id: ID de l'article à filtrer

        Returns:
            Liste d'entrées de timeline triées par date décroissante
        """
        mouvements = self.inventaire.mouvements

        # Filtrer par article
        if article_id:
            mouvements = [m for m in mouvements if m.article_id == article_id]

        # Filtrer par type
        if type_filtre:
            mouvements = [m for m in mouvements if m.type == type_filtre]

        # Filtrer par période
        if date_debut or date_fin:
            mouvements = [
                m for m in mouvements
                if (not date_debut or m.date >= date_debut) and
                   (not date_fin or m.date <= date_fin)
            ]

        # Convertir en entrées de timeline
        entrees = []
        for mouvement in mouvements:
            article = self.inventaire.obtenir_article(mouvement.article_id)
            if not article:
                continue

            # Extraire date et heure
            try:
                dt = datetime.fromisoformat(mouvement.date)
                date = dt.strftime("%Y-%m-%d")
                heure = dt.strftime("%H:%M:%S")
            except:
                date = mouvement.date[:10]
                heure = mouvement.date[11:19] if len(mouvement.date) > 11 else "00:00:00"

            entree = EntreeTimeline(
                date=date,
                heure=heure,
                type=mouvement.type,
                article_nom=article.nom,
                article_reference=article.reference,
                quantite=mouvement.quantite,
                motif=mouvement.motif,
                commentaire=mouvement.commentaire,
                utilisateur=mouvement.utilisateur,
                icone=self._obtenir_icone(mouvement),
                couleur=self.COULEURS.get(mouvement.type, "#718096")
            )
            entrees.append(entree)

        # Trier par date décroissante (plus récent en premier)
        entrees.sort(key=lambda e: f"{e.date} {e.heure}", reverse=True)

        # Limiter si demandé
        if limite:
            entrees = entrees[:limite]

        return entrees

    def _obtenir_icone(self, mouvement) -> str:
        """Détermine l'icône pour un mouvement."""
        # Icône spécifique au motif si disponible
        icone_motif = self.MOTIFS_ICONES.get(mouvement.motif)
        if icone_motif:
            return icone_motif

        # Sinon icône par type
        return self.ICONES.get(mouvement.type, "📌")

    def generer_rapport_timeline(self,
                                 jours: int = 7,
                                 grouper_par_jour: bool = True) -> str:
        """
        Génère un rapport texte de la timeline.

        Args:
            jours: Nombre de jours à inclure
            grouper_par_jour: Grouper les entrées par jour

        Returns:
            Rapport formaté
        """
        date_debut = (datetime.now() - timedelta(days=jours)).isoformat()
        entrees = self.obtenir_timeline(date_debut=date_debut)

        if not entrees:
            return f"📭 Aucun mouvement dans les {jours} derniers jours.\n"

        texte = "\n" + "=" * 80 + "\n"
        texte += f"           JOURNAL DES MOUVEMENTS - {jours} DERNIERS JOURS\n"
        texte += "=" * 80 + "\n\n"

        if grouper_par_jour:
            # Grouper par date
            par_jour = {}
            for entree in entrees:
                if entree.date not in par_jour:
                    par_jour[entree.date] = []
                par_jour[entree.date].append(entree)

            # Afficher par jour
            for date in sorted(par_jour.keys(), reverse=True):
                entrees_jour = par_jour[date]

                # Formater la date
                try:
                    dt = datetime.fromisoformat(date)
                    date_fmt = dt.strftime("%A %d %B %Y")
                except:
                    date_fmt = date

                texte += f"\n📅 {date_fmt} ({len(entrees_jour)} mouvement(s))\n"
                texte += "-" * 80 + "\n"

                for entree in entrees_jour:
                    texte += self._formater_entree(entree) + "\n"
        else:
            # Liste simple
            for entree in entrees:
                texte += self._formater_entree(entree) + "\n"

        texte += "\n" + "=" * 80 + "\n"
        return texte

    def _formater_entree(self, entree: EntreeTimeline) -> str:
        """Formate une entrée pour affichage."""
        ligne = f"{entree.heure} {entree.icone} "

        if entree.type == "entree":
            ligne += f"+{entree.quantite} "
        elif entree.type == "sortie":
            ligne += f"-{entree.quantite} "
        else:
            ligne += f"={entree.quantite} "

        ligne += f"{entree.article_nom} ({entree.article_reference})"

        if entree.motif:
            ligne += f" | {entree.motif}"

        if entree.commentaire:
            ligne += f" | {entree.commentaire}"

        return ligne

    def calculer_statistiques_mouvements(self, jours: int = 30) -> Dict:
        """
        Calcule des statistiques sur les mouvements.

        Args:
            jours: Nombre de jours à analyser

        Returns:
            Dictionnaire de statistiques
        """
        date_debut = (datetime.now() - timedelta(days=jours)).isoformat()
        entrees_timeline = self.obtenir_timeline(date_debut=date_debut)

        # Compteurs par type
        par_type = {"entree": 0, "sortie": 0, "correction": 0, "inventaire": 0}
        par_motif = {}

        total_entrees_qte = 0
        total_sorties_qte = 0

        for entree in entrees_timeline:
            par_type[entree.type] = par_type.get(entree.type, 0) + 1

            if entree.motif:
                par_motif[entree.motif] = par_motif.get(entree.motif, 0) + 1

            if entree.type == "entree":
                total_entrees_qte += entree.quantite
            elif entree.type == "sortie":
                total_sorties_qte += entree.quantite

        # Mouvements par jour
        mouvements_par_jour = len(entrees_timeline) / jours if jours > 0 else 0

        return {
            "periode_jours": jours,
            "total_mouvements": len(entrees_timeline),
            "mouvements_par_jour": mouvements_par_jour,
            "par_type": par_type,
            "par_motif": par_motif,
            "total_entrees_quantite": total_entrees_qte,
            "total_sorties_quantite": total_sorties_qte,
            "solde_quantite": total_entrees_qte - total_sorties_qte
        }

    def rechercher(self, terme: str, limite: int = 50) -> List[EntreeTimeline]:
        """
        Recherche dans l'historique des mouvements.

        Args:
            terme: Terme de recherche (nom article, référence, commentaire)
            limite: Nombre maximum de résultats

        Returns:
            Liste d'entrées correspondantes
        """
        entrees = self.obtenir_timeline()
        terme_lower = terme.lower()

        resultats = [
            e for e in entrees
            if (terme_lower in e.article_nom.lower() or
                terme_lower in e.article_reference.lower() or
                (e.commentaire and terme_lower in e.commentaire.lower()) or
                terme_lower in e.motif.lower())
        ]

        return resultats[:limite]

    def obtenir_activite_recente(self, heures: int = 24) -> List[EntreeTimeline]:
        """
        Récupère l'activité récente.

        Args:
            heures: Nombre d'heures

        Returns:
            Entrées de timeline récentes
        """
        date_limite = (datetime.now() - timedelta(hours=heures)).isoformat()
        return self.obtenir_timeline(date_debut=date_limite)

    def exporter_csv(self, fichier: str, jours: int = None):
        """
        Exporte la timeline en CSV.

        Args:
            fichier: Chemin du fichier de sortie
            jours: Nombre de jours (None = tout)
        """
        import csv

        date_debut = None
        if jours:
            date_debut = (datetime.now() - timedelta(days=jours)).isoformat()

        entrees = self.obtenir_timeline(date_debut=date_debut)

        with open(fichier, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # En-tête
            writer.writerow([
                "Date", "Heure", "Type", "Article", "Référence",
                "Quantité", "Motif", "Commentaire", "Utilisateur"
            ])

            # Données
            for entree in reversed(entrees):  # Ordre chronologique
                writer.writerow([
                    entree.date,
                    entree.heure,
                    entree.type,
                    entree.article_nom,
                    entree.article_reference,
                    entree.quantite,
                    entree.motif,
                    entree.commentaire,
                    entree.utilisateur
                ])

    def generer_resume_journalier(self, date: str = None) -> str:
        """
        Génère un résumé des mouvements pour une journée.

        Args:
            date: Date au format YYYY-MM-DD (None = aujourd'hui)

        Returns:
            Résumé formaté
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        date_debut = f"{date}T00:00:00"
        date_fin = f"{date}T23:59:59"

        entrees = self.obtenir_timeline(date_debut=date_debut, date_fin=date_fin)

        if not entrees:
            return f"📭 Aucun mouvement le {date}.\n"

        # Compteurs
        nb_entrees = len([e for e in entrees if e.type == "entree"])
        nb_sorties = len([e for e in entrees if e.type == "sortie"])
        nb_corrections = len([e for e in entrees if e.type == "correction"])

        qte_entrees = sum(e.quantite for e in entrees if e.type == "entree")
        qte_sorties = sum(e.quantite for e in entrees if e.type == "sortie")

        texte = f"\n📊 RÉSUMÉ DU {date}\n"
        texte += "=" * 60 + "\n\n"
        texte += f"Total mouvements: {len(entrees)}\n"
        texte += f"  📥 Entrées:     {nb_entrees} ({qte_entrees} unités)\n"
        texte += f"  📤 Sorties:     {nb_sorties} ({qte_sorties} unités)\n"
        texte += f"  ✏️  Corrections: {nb_corrections}\n"
        texte += f"\nSolde:          {qte_entrees - qte_sorties:+} unités\n"
        texte += "\n" + "=" * 60 + "\n"

        return texte
