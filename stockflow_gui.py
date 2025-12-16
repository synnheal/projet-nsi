"""
StockFlow Pro - Interface Graphique Moderne

Interface complète intégrant toutes les fonctionnalités :
- Dashboard avec KPIs en temps réel
- Gestion des articles (CRUD complet)
- Mouvements de stock (entrées/sorties)
- Prévisions et détection d'anomalies
- Analyses financières avancées
- Réapprovisionnement intelligent
- Timeline chronologique
- Simulations de scénarios
- Export HTML professionnel
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import sys
import json
from datetime import datetime, timedelta

# Imports StockFlow
from projectflow.stock import Inventaire, Article, Mouvement, CATEGORIES_ARTICLES
from projectflow.predictions import PredictionEngine
from projectflow.analytics import AnalyticsEngine
from projectflow.restocking import RestockingEngine, Urgence
from projectflow.timeline import TimelineManager
from projectflow.scenarios import ScenarioEngine, Scenario

from projectflow.themes import obtenir_theme_manager, THEMES
from projectflow.charts import LineChart, PieChart, BarChart


class ModernCard(tk.Frame):
    """Carte moderne avec ombre."""

    def __init__(self, parent, bg_color, **kwargs):
        super().__init__(parent, bg=parent["bg"])

        shadow = tk.Frame(self, bg="#d0d0d0")
        shadow.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 3))

        self.card = tk.Frame(shadow, bg=bg_color, **kwargs)
        self.card.pack(fill="both", expand=True)

    def get_card(self):
        return self.card


class StockFlowApp:
    """Application principale StockFlow Pro."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("StockFlow Pro 📦")
        self.root.geometry("1600x900")
        self.root.minsize(1400, 800)

        # Gestionnaires
        self.theme_manager = obtenir_theme_manager()
        self.theme = self.theme_manager.theme

        # Charger ou créer l'inventaire
        self.inventaire = self._charger_inventaire()
        self.predictions = PredictionEngine(self.inventaire)
        self.analytics = AnalyticsEngine(self.inventaire)
        self.restocking = RestockingEngine(self.inventaire, self.predictions)
        self.timeline = TimelineManager(self.inventaire)
        self.scenarios = ScenarioEngine(self.inventaire, self.predictions)

        # État
        self.current_page = "dashboard"
        self.selected_article = None

        # Construire l'interface
        self.root.configure(bg=self.theme.bg_primary)
        self._build_ui()
        self._show_dashboard()

        # Centrer
        self._center_window()

    def _charger_inventaire(self):
        """Charge l'inventaire depuis le fichier."""
        try:
            if os.path.exists("stockflow_inventaire.json"):
                with open("stockflow_inventaire.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return Inventaire.from_dict(data)
        except:
            pass

        # Créer un inventaire d'exemple
        inv = Inventaire(nom="Boutique High-Tech")

        # Ajouter des articles d'exemple
        articles_demo = [
            Article(
                nom="MacBook Pro 16\"",
                reference="APPLE-MBP-16",
                categorie="electronique",
                quantite=8,
                seuil_min=3,
                stock_optimal=15,
                prix_achat=2200,
                prix_vente=2899,
                fournisseur="Apple France",
                delai_reappro_jours=7,
                ventes_jour=0.8
            ),
            Article(
                nom="iPhone 15 Pro",
                reference="APPLE-IP15PRO",
                categorie="electronique",
                quantite=25,
                seuil_min=10,
                stock_optimal=40,
                prix_achat=950,
                prix_vente=1329,
                fournisseur="Apple France",
                delai_reappro_jours=5,
                ventes_jour=2.5
            ),
            Article(
                nom="AirPods Pro 2",
                reference="APPLE-APP2",
                categorie="electronique",
                quantite=2,
                seuil_min=15,
                stock_optimal=50,
                prix_achat=210,
                prix_vente=279,
                fournisseur="Apple France",
                delai_reappro_jours=3,
                ventes_jour=3.2
            ),
        ]

        for article in articles_demo:
            inv.ajouter_article(article)

        return inv

    def _sauvegarder_inventaire(self):
        """Sauvegarde l'inventaire."""
        try:
            with open("stockflow_inventaire.json", "w", encoding="utf-8") as f:
                json.dump(self.inventaire.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde : {e}")

    def _center_window(self):
        """Centre la fenêtre."""
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"+{x}+{y}")

    def _build_ui(self):
        """Construit l'interface."""
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=self.theme.bg_secondary, width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self._build_sidebar()

        # Zone principale
        self.main = tk.Frame(self.root, bg=self.theme.bg_primary)
        self.main.pack(side="right", fill="both", expand=True)

    def _build_sidebar(self):
        """Construit la sidebar."""
        # Logo
        header = tk.Frame(self.sidebar, bg=self.theme.bg_secondary)
        header.pack(fill="x", padx=20, pady=25)

        logo = tk.Label(header, text="📦 StockFlow", font=("Segoe UI", 22, "bold"),
                       fg=self.theme.accent, bg=self.theme.bg_secondary)
        logo.pack()

        version = tk.Label(header, text="PRO", font=("Segoe UI", 8, "bold"),
                          fg=self.theme.text_primary, bg=self.theme.accent,
                          padx=8, pady=2)
        version.pack(pady=5)

        # Navigation
        nav_frame = tk.Frame(self.sidebar, bg=self.theme.bg_secondary)
        nav_frame.pack(fill="x", pady=20, padx=12)

        nav_items = [
            ("dashboard", "📊", "Dashboard"),
            ("articles", "📦", "Articles"),
            ("mouvements", "📝", "Mouvements"),
            ("previsions", "🔮", "Prévisions"),
            ("analytics", "💰", "Analyses"),
            ("reappro", "🚚", "Réappro"),
            ("timeline", "📅", "Timeline"),
            ("scenarios", "🎯", "Scénarios"),
            ("settings", "⚙️", "Réglages"),
        ]

        self.nav_buttons = {}
        for key, icon, text in nav_items:
            btn_container = tk.Frame(nav_frame, bg=self.theme.bg_secondary, cursor="hand2")
            btn_container.pack(fill="x", pady=3)

            indicator = tk.Frame(btn_container, bg=self.theme.accent if key == self.current_page else self.theme.bg_secondary,
                               width=4)
            indicator.pack(side="left", fill="y")

            inner = tk.Label(btn_container, text=f"  {icon}  {text}",
                           font=("Segoe UI", 11, "bold" if key == self.current_page else "normal"),
                           fg=self.theme.accent if key == self.current_page else self.theme.text_secondary,
                           bg=self.theme.bg_card if key == self.current_page else self.theme.bg_secondary,
                           anchor="w", padx=18, pady=14)
            inner.pack(side="left", fill="x", expand=True)

            inner.bind("<Button-1>", lambda e, k=key: self._navigate(k))

            self.nav_buttons[key] = (inner, indicator)

    def _navigate(self, page):
        """Navigation entre les pages."""
        self.current_page = page

        # Mettre à jour styles
        for key, (button, indicator) in self.nav_buttons.items():
            if key == page:
                button.config(bg=self.theme.bg_card, fg=self.theme.accent,
                            font=("Segoe UI", 11, "bold"))
                indicator.config(bg=self.theme.accent)
            else:
                button.config(bg=self.theme.bg_secondary, fg=self.theme.text_secondary,
                            font=("Segoe UI", 11, "normal"))
                indicator.config(bg=self.theme.bg_secondary)

        # Afficher la page
        pages = {
            "dashboard": self._show_dashboard,
            "articles": self._show_articles,
            "mouvements": self._show_mouvements,
            "previsions": self._show_previsions,
            "analytics": self._show_analytics,
            "reappro": self._show_reappro,
            "timeline": self._show_timeline,
            "scenarios": self._show_scenarios,
            "settings": self._show_settings
        }

        if page in pages:
            pages[page]()

    def _clear_main(self):
        """Efface la zone principale."""
        for widget in self.main.winfo_children():
            widget.destroy()

    def _show_dashboard(self):
        """Affiche le dashboard."""
        self._clear_main()

        # Mettre à jour les stats
        self.predictions.mettre_a_jour_tous_les_articles()

        # Header
        header = tk.Frame(self.main, bg=self.theme.bg_primary)
        header.pack(fill="x", padx=50, pady=35)

        tk.Label(header, text="📊 Dashboard", font=("Segoe UI", 28, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(side="left")

        # Bouton rafraîchir
        refresh = tk.Label(header, text="🔄 Actualiser", font=("Segoe UI", 11, "bold"),
                          fg=self.theme.text_primary, bg=self.theme.accent,
                          padx=15, pady=8, cursor="hand2")
        refresh.pack(side="right")
        refresh.bind("<Button-1>", lambda e: self._show_dashboard())

        # KPIs
        stats_frame = tk.Frame(self.main, bg=self.theme.bg_primary)
        stats_frame.pack(fill="x", padx=50, pady=15)

        rapport = self.analytics.generer_rapport_financier()
        anomalies = self.predictions.detecter_anomalies()

        stats = [
            ("Articles", len(self.inventaire.articles), self.theme.accent, "📦"),
            ("Valeur Stock", f"{rapport.valeur_stock_total:,.0f}€", self.theme.success, "💰"),
            ("Ruptures", len([a for a in anomalies if a.type == "rupture_stock"]), self.theme.danger, "🔴"),
            ("Marge", f"{rapport.taux_marge_moyen:.1f}%", self.theme.warning, "📊"),
        ]

        for label, value, color, icon in stats:
            card = ModernCard(stats_frame, self.theme.bg_card)
            card_inner = card.get_card()
            card_inner.config(padx=22, pady=18)
            card.pack(side="left", padx=8, expand=True, fill="both")

            tk.Label(card_inner, text=icon, font=("Segoe UI", 28),
                    bg=self.theme.bg_card).pack(anchor="w")

            tk.Label(card_inner, text=str(value), font=("Segoe UI", 32, "bold"),
                    fg=color, bg=self.theme.bg_card).pack(anchor="w", pady=(12, 4))

            tk.Label(card_inner, text=label, font=("Segoe UI", 10),
                    fg=self.theme.text_secondary, bg=self.theme.bg_card).pack(anchor="w")

        # Anomalies critiques
        if anomalies:
            alert_frame = tk.Frame(self.main, bg=self.theme.bg_primary)
            alert_frame.pack(fill="x", padx=50, pady=15)

            tk.Label(alert_frame, text=f"⚠️  {len(anomalies)} Anomalie(s) Détectée(s)",
                    font=("Segoe UI", 16, "bold"), fg=self.theme.danger,
                    bg=self.theme.bg_primary).pack(anchor="w", pady=(0, 10))

            for anom in anomalies[:5]:
                anom_card = tk.Frame(alert_frame, bg=self.theme.bg_card, padx=15, pady=10)
                anom_card.pack(fill="x", pady=3)

                icones = {"critique": "🔴", "elevee": "🟠", "moyenne": "🟡", "faible": "🔵"}

                tk.Label(anom_card, text=f"{icones.get(anom.severite, '⚪')} {anom.article_nom}",
                        font=("Segoe UI", 11, "bold"), fg=self.theme.text_primary,
                        bg=self.theme.bg_card).pack(anchor="w")

                tk.Label(anom_card, text=anom.message, font=("Segoe UI", 10),
                        fg=self.theme.text_secondary, bg=self.theme.bg_card).pack(anchor="w")

        # Articles critiques
        critiques_frame = tk.Frame(self.main, bg=self.theme.bg_primary)
        critiques_frame.pack(fill="both", expand=True, padx=50, pady=15)

        tk.Label(critiques_frame, text="📋 Articles Récents", font=("Segoe UI", 16, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", pady=(0, 10))

        for article in self.inventaire.articles[:5]:
            self._create_article_row(critiques_frame, article)

    def _create_article_row(self, parent, article):
        """Crée une ligne d'article."""
        row = tk.Frame(parent, bg=self.theme.bg_card, padx=15, pady=10)
        row.pack(fill="x", pady=3)

        # Icône statut
        icones_statut = {
            "rupture": "🔴",
            "critique": "🟠",
            "faible": "🟡",
            "bon": "🟢",
            "surstock": "🔵"
        }

        tk.Label(row, text=icones_statut.get(article.statut_stock, "⚪"),
                font=("Segoe UI", 14), bg=self.theme.bg_card).pack(side="left", padx=(0, 10))

        # Nom
        tk.Label(row, text=article.nom, font=("Segoe UI", 11, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_card,
                width=30, anchor="w").pack(side="left")

        # Stock
        tk.Label(row, text=f"Stock: {article.quantite}", font=("Segoe UI", 10),
                fg=self.theme.text_secondary, bg=self.theme.bg_card,
                width=15).pack(side="left")

        # Valeur
        tk.Label(row, text=f"{article.valeur_stock:,.0f}€", font=("Segoe UI", 10, "bold"),
                fg=self.theme.success, bg=self.theme.bg_card).pack(side="right")

    def _show_articles(self):
        """Affiche la gestion des articles."""
        self._clear_main()

        # Header
        header = tk.Frame(self.main, bg=self.theme.bg_primary)
        header.pack(fill="x", padx=40, pady=30)

        tk.Label(header, text="📦 Gestion des Articles", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(side="left")

        # Bouton nouvel article
        new_btn = tk.Label(header, text="➕ Nouvel Article", font=("Segoe UI", 11, "bold"),
                          fg=self.theme.text_primary, bg=self.theme.success,
                          padx=20, pady=8, cursor="hand2")
        new_btn.pack(side="right")
        new_btn.bind("<Button-1>", lambda e: self._show_new_article_dialog())

        # Liste des articles
        list_frame = tk.Frame(self.main, bg=self.theme.bg_primary)
        list_frame.pack(fill="both", expand=True, padx=40)

        # Scroll
        canvas = tk.Canvas(list_frame, bg=self.theme.bg_primary, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.theme.bg_primary)

        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for article in self.inventaire.articles:
            self._create_article_card_detailed(content, article)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_article_card_detailed(self, parent, article):
        """Crée une carte article détaillée."""
        card = ModernCard(parent, self.theme.bg_card)
        card_inner = card.get_card()
        card_inner.config(padx=20, pady=15)
        card.pack(fill="x", pady=5)

        # Header
        header = tk.Frame(card_inner, bg=self.theme.bg_card)
        header.pack(fill="x")

        icones_statut = {"rupture": "🔴", "critique": "🟠", "faible": "🟡", "bon": "🟢", "surstock": "🔵"}

        tk.Label(header, text=f"{icones_statut.get(article.statut_stock, '⚪')} {article.nom}",
                font=("Segoe UI", 14, "bold"), fg=self.theme.text_primary,
                bg=self.theme.bg_card).pack(side="left")

        tk.Label(header, text=article.reference, font=("Segoe UI", 10),
                fg=self.theme.text_muted, bg=self.theme.bg_card).pack(side="left", padx=10)

        # Info
        info_frame = tk.Frame(card_inner, bg=self.theme.bg_card)
        info_frame.pack(fill="x", pady=10)

        infos = [
            ("Stock", f"{article.quantite} / {article.stock_optimal}"),
            ("Seuil", str(article.seuil_critique)),
            ("Prix Vente", f"{article.prix_vente}€"),
            ("Marge", f"{article.taux_marge:.1f}%"),
            ("Valeur", f"{article.valeur_stock:,.0f}€"),
        ]

        for i, (label, value) in enumerate(infos):
            col = tk.Frame(info_frame, bg=self.theme.bg_card)
            col.pack(side="left", padx=15)

            tk.Label(col, text=label, font=("Segoe UI", 9),
                    fg=self.theme.text_muted, bg=self.theme.bg_card).pack()
            tk.Label(col, text=value, font=("Segoe UI", 11, "bold"),
                    fg=self.theme.text_primary, bg=self.theme.bg_card).pack()

        # Actions
        actions = tk.Frame(card_inner, bg=self.theme.bg_card)
        actions.pack(fill="x", pady=(10, 0))

        btn_vente = tk.Label(actions, text="📤 Vente", font=("Segoe UI", 9, "bold"),
                            fg=self.theme.text_primary, bg=self.theme.warning,
                            padx=12, pady=6, cursor="hand2")
        btn_vente.pack(side="left", padx=3)
        btn_vente.bind("<Button-1>", lambda e, a=article: self._dialog_vente(a))

        btn_entree = tk.Label(actions, text="📥 Entrée", font=("Segoe UI", 9, "bold"),
                             fg=self.theme.text_primary, bg=self.theme.success,
                             padx=12, pady=6, cursor="hand2")
        btn_entree.pack(side="left", padx=3)
        btn_entree.bind("<Button-1>", lambda e, a=article: self._dialog_entree(a))

    def _show_new_article_dialog(self):
        """Dialogue nouvel article."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouvel Article")
        dialog.geometry("500x600")
        dialog.configure(bg=self.theme.bg_primary)

        tk.Label(dialog, text="➕ Nouvel Article", font=("Segoe UI", 18, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(pady=20)

        form = tk.Frame(dialog, bg=self.theme.bg_card, padx=30, pady=25)
        form.pack(fill="both", expand=True, padx=20, pady=10)

        entries = {}
        fields = [
            ("Nom", "nom"),
            ("Référence", "reference"),
            ("Quantité", "quantite"),
            ("Seuil minimum", "seuil_min"),
            ("Stock optimal", "stock_optimal"),
            ("Prix d'achat", "prix_achat"),
            ("Prix de vente", "prix_vente"),
            ("Fournisseur", "fournisseur"),
        ]

        for label, key in fields:
            tk.Label(form, text=label, font=("Segoe UI", 11),
                    fg=self.theme.text_secondary, bg=self.theme.bg_card).pack(anchor="w", pady=(10, 5))

            entry = tk.Entry(form, font=("Segoe UI", 12), bg=self.theme.bg_input,
                           fg=self.theme.text_primary, relief="flat")
            entry.pack(fill="x", ipady=8)
            entries[key] = entry

        # Catégorie
        tk.Label(form, text="Catégorie", font=("Segoe UI", 11),
                fg=self.theme.text_secondary, bg=self.theme.bg_card).pack(anchor="w", pady=(10, 5))

        cat_var = tk.StringVar(value="electronique")
        cat_combo = ttk.Combobox(form, textvariable=cat_var,
                                values=list(CATEGORIES_ARTICLES.keys()),
                                state="readonly")
        cat_combo.pack(fill="x", ipady=8)

        # Boutons
        btn_frame = tk.Frame(dialog, bg=self.theme.bg_primary)
        btn_frame.pack(fill="x", padx=20, pady=20)

        def save():
            try:
                article = Article(
                    nom=entries["nom"].get(),
                    reference=entries["reference"].get(),
                    categorie=cat_var.get(),
                    quantite=int(entries["quantite"].get() or 0),
                    seuil_min=int(entries["seuil_min"].get() or 5),
                    stock_optimal=int(entries["stock_optimal"].get() or 20),
                    prix_achat=float(entries["prix_achat"].get() or 0),
                    prix_vente=float(entries["prix_vente"].get() or 0),
                    fournisseur=entries["fournisseur"].get(),
                )
                self.inventaire.ajouter_article(article)
                self._sauvegarder_inventaire()
                messagebox.showinfo("Succès", "Article créé !")
                dialog.destroy()
                self._show_articles()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        tk.Label(btn_frame, text="✅ Créer", font=("Segoe UI", 11, "bold"),
                fg=self.theme.text_primary, bg=self.theme.success,
                padx=25, pady=10, cursor="hand2").pack(side="right")
        btn_frame.winfo_children()[-1].bind("<Button-1>", lambda e: save())

        tk.Label(btn_frame, text="❌ Annuler", font=("Segoe UI", 11, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_card,
                padx=25, pady=10, cursor="hand2").pack(side="left")
        btn_frame.winfo_children()[-1].bind("<Button-1>", lambda e: dialog.destroy())

    def _dialog_vente(self, article):
        """Dialogue de vente."""
        qte = simpledialog.askinteger("Vente", f"Quantité à vendre ({article.nom}) ?",
                                     minvalue=1, maxvalue=article.quantite)
        if qte:
            try:
                self.inventaire.retirer_stock(article.id, qte, article.prix_vente, "vente")
                self._sauvegarder_inventaire()
                messagebox.showinfo("Succès", f"{qte} × {article.nom} vendus !")
                self._show_articles()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def _dialog_entree(self, article):
        """Dialogue d'entrée de stock."""
        qte = simpledialog.askinteger("Entrée Stock", f"Quantité à ajouter ({article.nom}) ?",
                                     minvalue=1)
        if qte:
            try:
                self.inventaire.ajouter_stock(article.id, qte, article.prix_achat, "reappro")
                self._sauvegarder_inventaire()
                messagebox.showinfo("Succès", f"+{qte} × {article.nom} ajoutés !")
                self._show_articles()
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def _show_mouvements(self):
        """Affiche les mouvements."""
        self._clear_main()

        tk.Label(self.main, text="📝 Mouvements de Stock", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=30)

        # Stats
        stats = self.timeline.calculer_statistiques_mouvements(jours=30)

        stats_frame = tk.Frame(self.main, bg=self.theme.bg_primary)
        stats_frame.pack(fill="x", padx=40, pady=15)

        kpis = [
            ("Mouvements", stats['total_mouvements'], "📊"),
            ("Entrées", stats['total_entrees_quantite'], "📥"),
            ("Sorties", stats['total_sorties_quantite'], "📤"),
            ("Solde", stats['solde_quantite'], "⚖️"),
        ]

        for label, value, icon in kpis:
            card = ModernCard(stats_frame, self.theme.bg_card)
            card_inner = card.get_card()
            card_inner.config(padx=20, pady=15)
            card.pack(side="left", padx=8, expand=True)

            tk.Label(card_inner, text=icon, font=("Segoe UI", 20),
                    bg=self.theme.bg_card).pack()
            tk.Label(card_inner, text=str(value), font=("Segoe UI", 24, "bold"),
                    fg=self.theme.accent, bg=self.theme.bg_card).pack()
            tk.Label(card_inner, text=label, font=("Segoe UI", 10),
                    fg=self.theme.text_muted, bg=self.theme.bg_card).pack()

        # Liste des mouvements
        tk.Label(self.main, text="Derniers mouvements (30j)", font=("Segoe UI", 14, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=(20, 10))

        entrees = self.timeline.obtenir_timeline(limite=20)

        for entree in entrees:
            row = tk.Frame(self.main, bg=self.theme.bg_card, padx=15, pady=10)
            row.pack(fill="x", padx=40, pady=3)

            tk.Label(row, text=entree.icone, font=("Segoe UI", 14),
                    bg=self.theme.bg_card).pack(side="left", padx=(0, 10))

            tk.Label(row, text=entree.article_nom, font=("Segoe UI", 11, "bold"),
                    fg=self.theme.text_primary, bg=self.theme.bg_card,
                    width=30, anchor="w").pack(side="left")

            signe = "+" if entree.type == "entree" else "-"
            tk.Label(row, text=f"{signe}{entree.quantite}", font=("Segoe UI", 10),
                    fg=self.theme.success if entree.type == "entree" else self.theme.danger,
                    bg=self.theme.bg_card, width=10).pack(side="left")

            tk.Label(row, text=entree.motif, font=("Segoe UI", 10),
                    fg=self.theme.text_muted, bg=self.theme.bg_card,
                    width=15).pack(side="left")

            tk.Label(row, text=entree.date_complete, font=("Segoe UI", 9),
                    fg=self.theme.text_muted, bg=self.theme.bg_card).pack(side="right")

    def _show_previsions(self):
        """Affiche les prévisions."""
        self._clear_main()

        tk.Label(self.main, text="🔮 Prévisions & Anomalies", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=30)

        # Mettre à jour
        self.predictions.mettre_a_jour_tous_les_articles()

        # Anomalies
        anomalies = self.predictions.detecter_anomalies()

        tk.Label(self.main, text=f"⚠️  {len(anomalies)} Anomalie(s)", font=("Segoe UI", 16, "bold"),
                fg=self.theme.danger, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=(0, 10))

        for anom in anomalies[:10]:
            card = tk.Frame(self.main, bg=self.theme.bg_card, padx=15, pady=10)
            card.pack(fill="x", padx=40, pady=3)

            icones = {"critique": "🔴", "elevee": "🟠", "moyenne": "🟡", "faible": "🔵"}

            tk.Label(card, text=f"{icones.get(anom.severite, '⚪')} {anom.article_nom}",
                    font=("Segoe UI", 12, "bold"), fg=self.theme.text_primary,
                    bg=self.theme.bg_card, width=30, anchor="w").pack(side="left")

            tk.Label(card, text=anom.message, font=("Segoe UI", 10),
                    fg=self.theme.text_secondary, bg=self.theme.bg_card).pack(side="left", padx=20)

            tk.Label(card, text=anom.type, font=("Segoe UI", 9),
                    fg=self.theme.text_muted, bg=self.theme.bg_card).pack(side="right")

        # Prévisions
        tk.Label(self.main, text="📈 Prévisions de Ventes", font=("Segoe UI", 16, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=(30, 10))

        for article in self.inventaire.articles[:5]:
            prev = self.predictions.prevoir_ventes(article.id)
            if prev:
                card = tk.Frame(self.main, bg=self.theme.bg_card, padx=15, pady=10)
                card.pack(fill="x", padx=40, pady=3)

                fleches = {"hausse": "📈", "baisse": "📉", "stable": "➡️"}

                tk.Label(card, text=f"{fleches.get(prev.tendance, '➡️')} {article.nom}",
                        font=("Segoe UI", 11, "bold"), fg=self.theme.text_primary,
                        bg=self.theme.bg_card, width=30, anchor="w").pack(side="left")

                tk.Label(card, text=f"Mois: {prev.ventes_mois_prevue:.0f} unités",
                        font=("Segoe UI", 10), fg=self.theme.text_secondary,
                        bg=self.theme.bg_card, width=20).pack(side="left")

                tk.Label(card, text=f"{prev.tendance.capitalize()} ({prev.tendance_pourcentage:+.1f}%)",
                        font=("Segoe UI", 10, "bold"),
                        fg=self.theme.success if prev.tendance == "hausse" else self.theme.danger if prev.tendance == "baisse" else self.theme.text_muted,
                        bg=self.theme.bg_card).pack(side="left", padx=10)

    def _show_analytics(self):
        """Affiche les analyses."""
        self._clear_main()

        tk.Label(self.main, text="💰 Analyses Financières", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=30)

        rapport = self.analytics.generer_rapport_financier()

        # KPIs financiers
        stats_frame = tk.Frame(self.main, bg=self.theme.bg_primary)
        stats_frame.pack(fill="x", padx=40, pady=15)

        kpis = [
            ("Valeur Stock", f"{rapport.valeur_stock_total:,.0f}€", self.theme.accent),
            ("Valeur Vente", f"{rapport.valeur_vente_potentielle:,.0f}€", self.theme.success),
            ("Marge", f"{rapport.marge_potentielle:,.0f}€", self.theme.warning),
            ("Taux Marge", f"{rapport.taux_marge_moyen:.1f}%", self.theme.danger),
        ]

        for label, value, color in kpis:
            card = ModernCard(stats_frame, self.theme.bg_card)
            card_inner = card.get_card()
            card_inner.config(padx=20, pady=15)
            card.pack(side="left", padx=8, expand=True)

            tk.Label(card_inner, text=str(value), font=("Segoe UI", 28, "bold"),
                    fg=color, bg=self.theme.bg_card).pack()
            tk.Label(card_inner, text=label, font=("Segoe UI", 10),
                    fg=self.theme.text_muted, bg=self.theme.bg_card).pack()

        # Top 5
        tk.Label(self.main, text="🏆 Top 5 - Valeur Stock", font=("Segoe UI", 16, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=(20, 10))

        for i, art in enumerate(rapport.top_articles_valeur[:5], 1):
            row = tk.Frame(self.main, bg=self.theme.bg_card, padx=15, pady=10)
            row.pack(fill="x", padx=40, pady=3)

            medailles = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            tk.Label(row, text=medailles[i-1], font=("Segoe UI", 14),
                    bg=self.theme.bg_card).pack(side="left", padx=(0, 10))

            tk.Label(row, text=art['nom'], font=("Segoe UI", 11, "bold"),
                    fg=self.theme.text_primary, bg=self.theme.bg_card,
                    width=35, anchor="w").pack(side="left")

            tk.Label(row, text=f"{art['valeur']:,.0f}€", font=("Segoe UI", 12, "bold"),
                    fg=self.theme.success, bg=self.theme.bg_card).pack(side="right")

    def _show_reappro(self):
        """Affiche le réapprovisionnement."""
        self._clear_main()

        tk.Label(self.main, text="🚚 Réapprovisionnement", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=30)

        # Générer recommandations
        recos = self.restocking.generer_recommandations(inclure_preventif=False)

        tk.Label(self.main, text=f"📋 {len(recos)} Recommandation(s)", font=("Segoe UI", 16, "bold"),
                fg=self.theme.accent, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=(0, 10))

        icones_urgence = {"CRITIQUE": "🔴", "ELEVEE": "🟠", "MOYENNE": "🟡", "FAIBLE": "🔵"}

        for reco in recos[:10]:
            card = tk.Frame(self.main, bg=self.theme.bg_card, padx=15, pady=12)
            card.pack(fill="x", padx=40, pady=4)

            # Header
            header = tk.Frame(card, bg=self.theme.bg_card)
            header.pack(fill="x")

            tk.Label(header, text=f"{icones_urgence.get(reco.urgence.name, '⚪')} {reco.article_nom}",
                    font=("Segoe UI", 12, "bold"), fg=self.theme.text_primary,
                    bg=self.theme.bg_card).pack(side="left")

            tk.Label(header, text=reco.urgence.name, font=("Segoe UI", 9, "bold"),
                    fg=self.theme.text_primary, bg=self.theme.danger if reco.urgence.name == "CRITIQUE" else self.theme.warning,
                    padx=8, pady=2).pack(side="right")

            # Info
            info = tk.Frame(card, bg=self.theme.bg_card)
            info.pack(fill="x", pady=(8, 0))

            infos = [
                ("Stock actuel", f"{reco.quantite_actuelle}"),
                ("Seuil", f"{reco.seuil_critique}"),
                ("À commander", f"{reco.quantite_recommandee}"),
                ("Coût", f"{reco.cout_estime:,.0f}€"),
                ("Fournisseur", reco.fournisseur),
            ]

            for i, (label, value) in enumerate(infos):
                col = tk.Frame(info, bg=self.theme.bg_card)
                col.pack(side="left", padx=10)

                tk.Label(col, text=label, font=("Segoe UI", 8),
                        fg=self.theme.text_muted, bg=self.theme.bg_card).pack()
                tk.Label(col, text=value, font=("Segoe UI", 10, "bold"),
                        fg=self.theme.text_primary, bg=self.theme.bg_card).pack()

            if reco.jours_avant_rupture:
                tk.Label(card, text=f"⚠️  Rupture dans {reco.jours_avant_rupture} jours",
                        font=("Segoe UI", 9, "bold"), fg=self.theme.danger,
                        bg=self.theme.bg_card).pack(anchor="w", pady=(5, 0))

    def _show_timeline(self):
        """Affiche la timeline."""
        self._show_mouvements()  # Réutilise la page mouvements

    def _show_scenarios(self):
        """Affiche les scénarios."""
        self._clear_main()

        tk.Label(self.main, text="🎯 Simulations de Scénarios", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=30)

        # Scénarios prédéfinis
        scenarios = self.scenarios.generer_scenarios_predéfinis()[:4]

        tk.Label(self.main, text="Comparer les scénarios", font=("Segoe UI", 14),
                fg=self.theme.text_secondary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=(0, 15))

        # Bouton comparer
        compare_btn = tk.Label(self.main, text="▶️  Lancer la Simulation", font=("Segoe UI", 12, "bold"),
                              fg=self.theme.text_primary, bg=self.theme.accent,
                              padx=25, pady=12, cursor="hand2")
        compare_btn.pack(anchor="w", padx=40, pady=10)
        compare_btn.bind("<Button-1>", lambda e: self._run_scenarios(scenarios))

        # Zone résultats
        self.scenario_results = tk.Frame(self.main, bg=self.theme.bg_primary)
        self.scenario_results.pack(fill="both", expand=True, padx=40, pady=20)

    def _run_scenarios(self, scenarios):
        """Exécute les scénarios."""
        for widget in self.scenario_results.winfo_children():
            widget.destroy()

        tk.Label(self.scenario_results, text="⏳ Simulation en cours...",
                font=("Segoe UI", 14), fg=self.theme.text_muted,
                bg=self.theme.bg_primary).pack(pady=20)

        self.root.update()

        # Comparer
        resultats = self.scenarios.comparer_scenarios(scenarios, duree_jours=90)

        for widget in self.scenario_results.winfo_children():
            widget.destroy()

        tk.Label(self.scenario_results, text="📊 Résultats", font=("Segoe UI", 16, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", pady=(0, 10))

        for i, res in enumerate(resultats[:5], 1):
            card = tk.Frame(self.scenario_results, bg=self.theme.bg_card, padx=20, pady=15)
            card.pack(fill="x", pady=5)

            # Header
            header = tk.Frame(card, bg=self.theme.bg_card)
            header.pack(fill="x")

            medailles = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            tk.Label(header, text=f"{medailles[i-1]} {res.scenario.nom}",
                    font=("Segoe UI", 13, "bold"), fg=self.theme.text_primary,
                    bg=self.theme.bg_card).pack(side="left")

            tk.Label(header, text=f"Score: {res.score_global:.0f}/100",
                    font=("Segoe UI", 11, "bold"), fg=self.theme.success if res.score_global >= 70 else self.theme.warning,
                    bg=self.theme.bg_card).pack(side="right")

            # Métriques
            metrics = tk.Frame(card, bg=self.theme.bg_card)
            metrics.pack(fill="x", pady=(10, 0))

            infos = [
                ("CA", f"{res.chiffre_affaires_total:,.0f}€"),
                ("Marge", f"{res.marge_totale:,.0f}€ ({res.taux_marge_moyen:.1f}%)"),
                ("Ruptures", f"{res.ruptures_count} fois"),
                ("CA perdu", f"{res.ventes_perdues:,.0f}€"),
            ]

            for label, value in infos:
                col = tk.Frame(metrics, bg=self.theme.bg_card)
                col.pack(side="left", padx=15)

                tk.Label(col, text=label, font=("Segoe UI", 9),
                        fg=self.theme.text_muted, bg=self.theme.bg_card).pack()
                tk.Label(col, text=value, font=("Segoe UI", 10, "bold"),
                        fg=self.theme.text_primary, bg=self.theme.bg_card).pack()

    def _show_settings(self):
        """Affiche les paramètres."""
        self._clear_main()

        tk.Label(self.main, text="⚙️ Réglages", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=30)

        # Boutons d'action
        actions_frame = tk.Frame(self.main, bg=self.theme.bg_primary)
        actions_frame.pack(fill="x", padx=40, pady=20)

        actions = [
            ("💾 Sauvegarder", self._sauvegarder_inventaire),
            ("📄 Exporter CSV", self._export_csv),
            ("🔄 Actualiser Stats", lambda: self.predictions.mettre_a_jour_tous_les_articles()),
        ]

        for text, command in actions:
            btn = tk.Label(actions_frame, text=text, font=("Segoe UI", 11, "bold"),
                          fg=self.theme.text_primary, bg=self.theme.accent,
                          padx=20, pady=10, cursor="hand2")
            btn.pack(side="left", padx=5)
            btn.bind("<Button-1>", lambda e, c=command: self._exec_action(c))

    def _exec_action(self, command):
        """Exécute une action."""
        try:
            command()
            messagebox.showinfo("Succès", "Action effectuée !")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def _export_csv(self):
        """Exporte en CSV."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
        if filename:
            self.timeline.exporter_csv(filename, jours=90)

    def run(self):
        """Lance l'application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = StockFlowApp()
    app.run()
