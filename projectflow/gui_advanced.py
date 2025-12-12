"""
ProjectFlow - Interface Graphique Avancée

Features:
- Dashboard avec graphiques
- Système de thèmes
- Timer Pomodoro
- Badges et gamification
- Multi-objectifs
- Scénarios What-if
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import json
from datetime import datetime

# Imports des modules ProjectFlow
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projectflow import storage, finance, planning, export_html
from projectflow.themes import obtenir_theme_manager, obtenir_theme, THEMES
from projectflow.charts import LineChart, PieChart, BarChart, ProgressRing, SparkLine
from projectflow.achievements import AchievementManager, BADGES, obtenir_titre_niveau, obtenir_couleur_niveau
from projectflow.timer import TimeTracker, formater_duree
from projectflow.finance_advanced import (
    CATEGORIES_DEPENSES, DepensesCategories, Scenario,
    comparer_scenarios, generer_recommandations
)


class ModernButton(tk.Frame):
    """Bouton moderne avec effets visuels."""

    def __init__(self, parent, text, command, bg_color, fg_color, **kwargs):
        super().__init__(parent, bg=parent["bg"], cursor="hand2")

        # Effet d'ombre (border simulée) - couleur grise solide
        shadow = tk.Frame(self, bg="#d0d0d0", height=2)
        shadow.pack(side="bottom", fill="x")

        # Bouton principal
        self.button = tk.Label(self, text=text, font=("Segoe UI", 11, "bold"),
                              fg=fg_color, bg=bg_color, padx=30, pady=12)
        self.button.pack()

        # Bindings
        self.button.bind("<Button-1>", lambda e: command())
        self.button.bind("<Enter>", self._on_enter)
        self.button.bind("<Leave>", lambda e: self.button.config(bg=bg_color))

        self.original_bg = bg_color
        self.hover_bg = self._lighten_color(bg_color)

    def _lighten_color(self, color):
        """Éclaircit une couleur pour l'effet hover."""
        # Conversion simple pour simuler un éclaircissement
        if color.startswith('#'):
            try:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                r = min(255, r + 20)
                g = min(255, g + 20)
                b = min(255, b + 20)
                return f"#{r:02x}{g:02x}{b:02x}"
            except:
                pass
        return color

    def _on_enter(self, e):
        self.button.config(bg=self.hover_bg)


class ModernCard(tk.Frame):
    """Carte moderne avec ombre et bordures arrondies simulées."""

    def __init__(self, parent, bg_color, shadow_color=None, **kwargs):
        super().__init__(parent, bg=parent["bg"])

        # Déterminer la couleur d'ombre automatiquement si non fournie
        if shadow_color is None:
            # Si bg_color est sombre, utiliser une ombre très sombre, sinon gris clair
            shadow_color = self._get_shadow_color(bg_color)

        # Container pour l'effet d'ombre
        shadow = tk.Frame(self, bg=shadow_color)
        shadow.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 3))

        # Carte principale
        self.card = tk.Frame(shadow, bg=bg_color, **kwargs)
        self.card.pack(fill="both", expand=True)

    def _get_shadow_color(self, bg_color):
        """Détermine la couleur d'ombre en fonction de la luminosité du fond."""
        if not bg_color.startswith('#'):
            return "#d0d0d0"  # Par défaut

        try:
            # Calculer la luminosité
            r = int(bg_color[1:3], 16)
            g = int(bg_color[3:5], 16)
            b = int(bg_color[5:7], 16)
            luminosity = (r * 0.299 + g * 0.587 + b * 0.114) / 255

            # Si sombre (luminosité < 0.5), ombre très sombre, sinon gris clair
            if luminosity < 0.5:
                return "#0a0a0a"  # Ombre sombre pour thèmes sombres
            else:
                return "#e0e0e0"  # Ombre claire pour thèmes clairs
        except:
            return "#d0d0d0"

    def get_card(self):
        """Retourne le frame intérieur pour ajouter du contenu."""
        return self.card


class App:
    """Application principale ProjectFlow avancée."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ProjectFlow Pro ✨")
        self.root.geometry("1450x850")
        self.root.minsize(1300, 750)

        # Gestionnaires
        self.theme_manager = obtenir_theme_manager()
        self.achievements = self._charger_achievements()
        self.time_tracker = self._charger_time_tracker()

        # État
        self.current_page = "dashboard"
        self.current_projet = None
        self.timer_running = False
        self.timer_job = None

        # Appliquer le thème
        self.theme = self.theme_manager.theme
        self.root.configure(bg=self.theme.bg_primary)

        # Construire l'interface
        self._build_ui()
        self._show_dashboard()

        # Centrer
        self._center_window()

    def _charger_achievements(self) -> AchievementManager:
        """Charge les achievements depuis le fichier."""
        try:
            if os.path.exists("projectflow_achievements.json"):
                with open("projectflow_achievements.json", "r", encoding="utf-8") as f:
                    return AchievementManager.from_dict(json.load(f))
        except:
            pass
        return AchievementManager()

    def _sauvegarder_achievements(self):
        """Sauvegarde les achievements."""
        try:
            with open("projectflow_achievements.json", "w", encoding="utf-8") as f:
                json.dump(self.achievements.to_dict(), f, ensure_ascii=False, indent=2)
        except:
            pass

    def _charger_time_tracker(self) -> TimeTracker:
        """Charge le time tracker."""
        try:
            if os.path.exists("projectflow_time.json"):
                with open("projectflow_time.json", "r", encoding="utf-8") as f:
                    return TimeTracker.from_dict(json.load(f))
        except:
            pass
        return TimeTracker()

    def _sauvegarder_time_tracker(self):
        """Sauvegarde le time tracker."""
        try:
            with open("projectflow_time.json", "w", encoding="utf-8") as f:
                json.dump(self.time_tracker.to_dict(), f, ensure_ascii=False, indent=2)
        except:
            pass

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
        # Header avec niveau - Version moderne
        header = tk.Frame(self.sidebar, bg=self.theme.bg_secondary)
        header.pack(fill="x", padx=20, pady=25)

        # Logo avec style moderne
        logo_container = tk.Frame(header, bg=self.theme.bg_secondary)
        logo_container.pack()

        logo = tk.Label(logo_container, text="✨ ProjectFlow", font=("Segoe UI", 22, "bold"),
                       fg=self.theme.accent, bg=self.theme.bg_secondary)
        logo.pack()

        version = tk.Label(logo_container, text="PRO", font=("Segoe UI", 8, "bold"),
                          fg=self.theme.text_primary, bg=self.theme.accent,
                          padx=8, pady=2)
        version.pack(pady=5)

        # Niveau utilisateur - Card moderne
        niveau_info = self.achievements.obtenir_progression_niveau()
        titre = obtenir_titre_niveau(niveau_info["niveau"])
        couleur = obtenir_couleur_niveau(niveau_info["niveau"])

        niveau_card = ModernCard(header, self.theme.bg_card)
        niveau_inner = niveau_card.get_card()
        niveau_inner.config(padx=15, pady=12)
        niveau_card.pack(fill="x", pady=15)

        niveau_label = tk.Label(niveau_inner, text=f"Niveau {niveau_info['niveau']}",
                               font=("Segoe UI", 10, "bold"), fg=self.theme.text_secondary,
                               bg=self.theme.bg_card)
        niveau_label.pack(anchor="w")

        titre_label = tk.Label(niveau_inner, text=titre,
                              font=("Segoe UI", 14, "bold"), fg=couleur,
                              bg=self.theme.bg_card)
        titre_label.pack(anchor="w", pady=(2, 8))

        # Barre de progression moderne avec pourcentage
        prog_container = tk.Frame(niveau_inner, bg=self.theme.bg_card)
        prog_container.pack(fill="x")

        prog_bg = tk.Canvas(prog_container, width=200, height=8,
                           bg=self.theme.bg_input, highlightthickness=0)
        prog_bg.pack()

        prog_width = int(200 * niveau_info["progression"])
        if prog_width > 0:
            # Barre avec gradient simulé
            prog_bg.create_rectangle(0, 0, prog_width, 8, fill=couleur, outline="")

        points_label = tk.Label(niveau_inner, text=f"{niveau_info['points_totaux']} points",
                               font=("Segoe UI", 9), fg=self.theme.text_muted,
                               bg=self.theme.bg_card)
        points_label.pack(anchor="w", pady=(5, 0))

        # Navigation moderne
        nav_frame = tk.Frame(self.sidebar, bg=self.theme.bg_secondary)
        nav_frame.pack(fill="x", pady=20, padx=12)

        nav_items = [
            ("dashboard", "📊", "Dashboard"),
            ("projects", "📁", "Projets"),
            ("new", "➕", "Nouveau"),
            ("timer", "⏱️", "Timer"),
            ("achievements", "🏆", "Badges"),
            ("scenarios", "🔮", "Scénarios"),
            ("settings", "⚙️", "Réglages"),
        ]

        self.nav_buttons = {}
        for key, icon, text in nav_items:
            # Container pour effet hover moderne
            btn_container = tk.Frame(nav_frame, bg=self.theme.bg_secondary, cursor="hand2")
            btn_container.pack(fill="x", pady=3)

            # Indicateur actif (barre latérale)
            indicator = tk.Frame(btn_container, bg=self.theme.accent if key == self.current_page else self.theme.bg_secondary,
                               width=4)
            indicator.pack(side="left", fill="y")

            inner = tk.Label(btn_container, text=f"  {icon}  {text}", font=("Segoe UI", 11, "bold" if key == self.current_page else "normal"),
                           fg=self.theme.accent if key == self.current_page else self.theme.text_secondary,
                           bg=self.theme.bg_card if key == self.current_page else self.theme.bg_secondary,
                           anchor="w", padx=18, pady=14)
            inner.pack(side="left", fill="x", expand=True)

            inner.bind("<Button-1>", lambda e, k=key: self._navigate(k))
            inner.bind("<Enter>", lambda e, b=inner, i=indicator: self._nav_hover(b, i, True))
            inner.bind("<Leave>", lambda e, b=inner, k=key, i=indicator: self._nav_hover(b, i, False, k))

            self.nav_buttons[key] = (inner, indicator)

        # Streak card moderne en bas
        streak_card = ModernCard(self.sidebar, self.theme.bg_card)
        streak_inner = streak_card.get_card()
        streak_inner.config(padx=18, pady=15)
        streak_card.pack(side="bottom", fill="x", padx=15, pady=20)

        # Titre avec icône animée
        streak_header = tk.Frame(streak_inner, bg=self.theme.bg_card)
        streak_header.pack(fill="x")

        tk.Label(streak_header, text="🔥", font=("Segoe UI", 20),
                bg=self.theme.bg_card).pack(side="left")

        tk.Label(streak_header, text="Streak", font=("Segoe UI", 11, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_card).pack(side="left", padx=5)

        # Nombre de jours - Grande taille
        tk.Label(streak_inner, text=f"{self.achievements.streak_actuel}",
                font=("Segoe UI", 36, "bold"), fg=self.theme.warning,
                bg=self.theme.bg_card).pack(anchor="w", pady=(8, 0))

        tk.Label(streak_inner, text="jours consécutifs",
                font=("Segoe UI", 10), fg=self.theme.text_secondary,
                bg=self.theme.bg_card).pack(anchor="w")

        # Record
        if self.achievements.meilleur_streak > self.achievements.streak_actuel:
            record_frame = tk.Frame(streak_inner, bg=self.theme.bg_input, padx=10, pady=5)
            record_frame.pack(fill="x", pady=(10, 0))

            tk.Label(record_frame, text=f"🏆 Record: {self.achievements.meilleur_streak} jours",
                    font=("Segoe UI", 9, "bold"), fg=self.theme.text_muted,
                    bg=self.theme.bg_input).pack()

    def _nav_hover(self, button, indicator, is_enter, key=None):
        """Gère l'effet hover de la navigation."""
        if is_enter:
            button.config(bg=self.theme.bg_card)
            indicator.config(bg=self.theme.accent)
        else:
            if key and key == self.current_page:
                button.config(bg=self.theme.bg_card)
                indicator.config(bg=self.theme.accent)
            else:
                button.config(bg=self.theme.bg_secondary)
                indicator.config(bg=self.theme.bg_secondary)

    def _update_nav_style(self, btn, key):
        """Met à jour le style de navigation (legacy - pour compatibilité)."""
        if isinstance(self.nav_buttons.get(key), tuple):
            button, indicator = self.nav_buttons[key]
            if key == self.current_page:
                button.config(bg=self.theme.bg_card, fg=self.theme.accent, font=("Segoe UI", 11, "bold"))
                indicator.config(bg=self.theme.accent)
            else:
                button.config(bg=self.theme.bg_secondary, fg=self.theme.text_secondary, font=("Segoe UI", 11, "normal"))
                indicator.config(bg=self.theme.bg_secondary)

    def _navigate(self, page):
        """Navigation entre les pages."""
        self.current_page = page

        # Mettre à jour styles des boutons de navigation
        for key, nav_item in self.nav_buttons.items():
            if isinstance(nav_item, tuple):
                button, indicator = nav_item
                if key == page:
                    button.config(bg=self.theme.bg_card, fg=self.theme.accent, font=("Segoe UI", 11, "bold"))
                    indicator.config(bg=self.theme.accent)
                else:
                    button.config(bg=self.theme.bg_secondary, fg=self.theme.text_secondary, font=("Segoe UI", 11, "normal"))
                    indicator.config(bg=self.theme.bg_secondary)

        # Afficher la page
        pages = {
            "dashboard": self._show_dashboard,
            "projects": self._show_projects,
            "new": self._show_new_project,
            "timer": self._show_timer,
            "achievements": self._show_achievements,
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
        """Affiche le tableau de bord."""
        self._clear_main()

        # Scroll
        canvas = tk.Canvas(self.main, bg=self.theme.bg_primary, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.theme.bg_primary)

        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Header moderne
        header = tk.Frame(content, bg=self.theme.bg_primary)
        header.pack(fill="x", padx=50, pady=35)

        # Titre avec icône
        title_frame = tk.Frame(header, bg=self.theme.bg_primary)
        title_frame.pack(side="left")

        tk.Label(title_frame, text="📊", font=("Segoe UI", 28),
                bg=self.theme.bg_primary).pack(side="left", padx=(0, 10))

        tk.Label(title_frame, text="Tableau de bord", font=("Segoe UI", 28, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(side="left")

        # Date moderne
        date_frame = tk.Frame(header, bg=self.theme.bg_input, padx=15, pady=8)
        date_frame.pack(side="right")

        date_str = datetime.now().strftime("%d %B %Y")
        tk.Label(date_frame, text=f"📅 {date_str}", font=("Segoe UI", 11, "bold"),
                fg=self.theme.text_secondary, bg=self.theme.bg_input).pack()

        # Stats rapides - Cartes modernes
        stats_frame = tk.Frame(content, bg=self.theme.bg_primary)
        stats_frame.pack(fill="x", padx=50, pady=15)

        projets = storage.lister_projets()
        total_epargne = sum(p.get("simulation", {}).get("total_epargne", 0) for p in projets)
        objectifs_atteints = sum(1 for p in projets if p.get("progression", 0) >= 1)

        stats = [
            ("Projets actifs", len(projets), self.theme.accent, "📁"),
            ("Épargne totale", f"{total_epargne:,.0f}€", self.theme.success, "💰"),
            ("Objectifs atteints", objectifs_atteints, self.theme.warning, "🎯"),
            ("Badges débloqués", len(self.achievements.badges_obtenus), self.theme.danger, "🏆"),
        ]

        for i, (label, value, color, icon) in enumerate(stats):
            # Utiliser ModernCard pour un effet d'ombre
            modern_card = ModernCard(stats_frame, self.theme.bg_card)
            card_inner = modern_card.get_card()
            card_inner.config(padx=22, pady=18)
            modern_card.pack(side="left", padx=8, expand=True, fill="both")

            # Icône avec background coloré
            icon_bg = tk.Frame(card_inner, bg=color, padx=12, pady=8)
            icon_bg.pack(anchor="w")

            tk.Label(icon_bg, text=icon, font=("Segoe UI", 22),
                    bg=color).pack()

            # Valeur en grand
            tk.Label(card_inner, text=str(value), font=("Segoe UI", 32, "bold"),
                    fg=color, bg=self.theme.bg_card).pack(anchor="w", pady=(12, 4))

            # Label descriptif
            tk.Label(card_inner, text=label, font=("Segoe UI", 10),
                    fg=self.theme.text_secondary, bg=self.theme.bg_card).pack(anchor="w")

        # Graphiques
        charts_frame = tk.Frame(content, bg=self.theme.bg_primary)
        charts_frame.pack(fill="x", padx=40, pady=20)

        # Graphique d'épargne
        if projets:
            chart_card = tk.Frame(charts_frame, bg=self.theme.bg_card, padx=20, pady=20)
            chart_card.pack(side="left", padx=10, expand=True, fill="both")

            tk.Label(chart_card, text="Évolution de l'épargne", font=("Segoe UI", 14, "bold"),
                    fg=self.theme.text_primary, bg=self.theme.bg_card).pack(anchor="w", pady=(0, 10))

            # Trouver le projet avec le plus de données
            best_projet = max(projets, key=lambda p: len(p.get("simulation", {}).get("tableau_mensuel", [])))
            simulation = best_projet.get("simulation", {})

            if simulation.get("tableau_mensuel"):
                chart_canvas = tk.Canvas(chart_card, width=450, height=250,
                                        bg=self.theme.bg_card, highlightthickness=0)
                chart_canvas.pack()

                chart = LineChart(chart_canvas, 0, 0, 450, 250)
                chart.draw(
                    simulation["tableau_mensuel"][:12],
                    objectif=best_projet.get("finances", {}).get("objectif", 0)
                )

        # Répartition dépenses
        depenses_card = tk.Frame(charts_frame, bg=self.theme.bg_card, padx=20, pady=20)
        depenses_card.pack(side="left", padx=10, expand=True, fill="both")

        tk.Label(depenses_card, text="Répartition type", font=("Segoe UI", 14, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_card).pack(anchor="w", pady=(0, 10))

        pie_canvas = tk.Canvas(depenses_card, width=300, height=250,
                              bg=self.theme.bg_card, highlightthickness=0)
        pie_canvas.pack()

        # Données exemple
        pie_data = [
            ("Logement", 800),
            ("Alimentation", 400),
            ("Transport", 200),
            ("Loisirs", 150),
            ("Autres", 100)
        ]

        pie = PieChart(pie_canvas, 0, 0, 300)
        pie.draw(pie_data)

        # Projets récents
        recent_frame = tk.Frame(content, bg=self.theme.bg_primary)
        recent_frame.pack(fill="x", padx=40, pady=20)

        tk.Label(recent_frame, text="Projets récents", font=("Segoe UI", 16, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", pady=(0, 15))

        for projet in projets[:3]:
            self._create_project_card(recent_frame, projet)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    def _create_project_card(self, parent, projet):
        """Crée une carte de projet."""
        card = tk.Frame(parent, bg=self.theme.bg_card, padx=20, pady=15)
        card.pack(fill="x", pady=5)

        # Header
        header = tk.Frame(card, bg=self.theme.bg_card)
        header.pack(fill="x")

        tk.Label(header, text=projet["nom"], font=("Segoe UI", 14, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_card).pack(side="left")

        progression = projet.get("progression", 0)
        prog_text = f"{progression*100:.0f}%"
        prog_color = self.theme.success if progression >= 1 else self.theme.accent

        tk.Label(header, text=prog_text, font=("Segoe UI", 12, "bold"),
                fg=prog_color, bg=self.theme.bg_card).pack(side="right")

        # Barre de progression
        prog_frame = tk.Frame(card, bg=self.theme.bg_card)
        prog_frame.pack(fill="x", pady=10)

        prog_canvas = tk.Canvas(prog_frame, width=400, height=8,
                               bg=self.theme.bg_input, highlightthickness=0)
        prog_canvas.pack(fill="x")

        prog_width = int(400 * progression)
        if prog_width > 0:
            prog_canvas.create_rectangle(0, 0, prog_width, 8, fill=prog_color, outline="")

        # Info
        finances = projet.get("finances", {})
        tk.Label(card, text=f"Objectif: {finances.get('objectif', 0):,.0f}€",
                font=("Segoe UI", 11), fg=self.theme.text_secondary,
                bg=self.theme.bg_card).pack(anchor="w")

        # Bouton
        btn = tk.Label(card, text="Ouvrir →", font=("Segoe UI", 10),
                      fg=self.theme.accent, bg=self.theme.bg_card, cursor="hand2")
        btn.pack(anchor="e", pady=(10, 0))
        btn.bind("<Button-1>", lambda e, p=projet: self._open_project(p))

    def _show_projects(self):
        """Affiche la liste des projets."""
        self._clear_main()

        header = tk.Frame(self.main, bg=self.theme.bg_primary)
        header.pack(fill="x", padx=40, pady=30)

        tk.Label(header, text="Mes Projets", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(side="left")

        # Bouton nouveau
        new_btn = tk.Label(header, text="➕ Nouveau", font=("Segoe UI", 11, "bold"),
                          fg=self.theme.text_primary, bg=self.theme.accent,
                          padx=20, pady=8, cursor="hand2")
        new_btn.pack(side="right")
        new_btn.bind("<Button-1>", lambda e: self._navigate("new"))

        # Liste
        list_frame = tk.Frame(self.main, bg=self.theme.bg_primary)
        list_frame.pack(fill="both", expand=True, padx=40)

        projets = storage.lister_projets()

        if not projets:
            tk.Label(list_frame, text="Aucun projet\n\nCréez votre premier projet !",
                    font=("Segoe UI", 14), fg=self.theme.text_muted,
                    bg=self.theme.bg_primary, justify="center").pack(pady=100)
        else:
            for projet in projets:
                self._create_project_card(list_frame, projet)

    def _show_new_project(self):
        """Formulaire nouveau projet."""
        self._clear_main()

        # Scroll
        canvas = tk.Canvas(self.main, bg=self.theme.bg_primary, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.theme.bg_primary)

        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Header
        tk.Label(content, text="Nouveau Projet", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=30)

        # Formulaire
        form = tk.Frame(content, bg=self.theme.bg_card, padx=30, pady=25)
        form.pack(fill="x", padx=40, pady=10)

        # Nom
        tk.Label(form, text="Nom du projet", font=("Segoe UI", 11),
                fg=self.theme.text_secondary, bg=self.theme.bg_card).pack(anchor="w")

        self.entry_nom = tk.Entry(form, font=("Segoe UI", 12), bg=self.theme.bg_input,
                                 fg=self.theme.text_primary, relief="flat",
                                 insertbackground=self.theme.text_primary)
        self.entry_nom.pack(fill="x", pady=(5, 15), ipady=8)

        # Finances
        tk.Label(form, text="Données financières", font=("Segoe UI", 14, "bold"),
                fg=self.theme.accent, bg=self.theme.bg_card).pack(anchor="w", pady=(20, 10))

        fields = [
            ("Revenus mensuels (€)", "entry_revenus"),
            ("Dépenses fixes (€)", "entry_fixes"),
            ("Dépenses variables (€)", "entry_variables"),
            ("Objectif (€)", "entry_objectif"),
            ("Durée simulation (mois)", "entry_duree")
        ]

        for label, attr in fields:
            tk.Label(form, text=label, font=("Segoe UI", 11),
                    fg=self.theme.text_secondary, bg=self.theme.bg_card).pack(anchor="w")

            entry = tk.Entry(form, font=("Segoe UI", 12), bg=self.theme.bg_input,
                           fg=self.theme.text_primary, relief="flat",
                           insertbackground=self.theme.text_primary)
            entry.pack(fill="x", pady=(5, 10), ipady=8)
            setattr(self, attr, entry)

        # Planning
        tk.Label(form, text="Planning", font=("Segoe UI", 14, "bold"),
                fg=self.theme.accent, bg=self.theme.bg_card).pack(anchor="w", pady=(20, 10))

        jours_frame = tk.Frame(form, bg=self.theme.bg_card)
        jours_frame.pack(fill="x", pady=10)

        self.jours_vars = {}
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]

        for jour in jours:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(jours_frame, text=jour, variable=var,
                               font=("Segoe UI", 10), fg=self.theme.text_primary,
                               bg=self.theme.bg_card, selectcolor=self.theme.bg_input,
                               activebackground=self.theme.bg_card)
            cb.pack(side="left", padx=5)
            self.jours_vars[jour.lower()] = var

        tk.Label(form, text="Heures par semaine", font=("Segoe UI", 11),
                fg=self.theme.text_secondary, bg=self.theme.bg_card).pack(anchor="w", pady=(10, 0))

        self.entry_heures = tk.Entry(form, font=("Segoe UI", 12), bg=self.theme.bg_input,
                                    fg=self.theme.text_primary, relief="flat",
                                    insertbackground=self.theme.text_primary)
        self.entry_heures.pack(fill="x", pady=(5, 10), ipady=8)

        # Boutons
        btn_frame = tk.Frame(content, bg=self.theme.bg_primary)
        btn_frame.pack(fill="x", padx=40, pady=20)

        cancel = tk.Label(btn_frame, text="Annuler", font=("Segoe UI", 11, "bold"),
                         fg=self.theme.text_primary, bg=self.theme.bg_card,
                         padx=25, pady=10, cursor="hand2")
        cancel.pack(side="left")
        cancel.bind("<Button-1>", lambda e: self._navigate("projects"))

        save = tk.Label(btn_frame, text="Créer le projet", font=("Segoe UI", 11, "bold"),
                       fg=self.theme.text_primary, bg=self.theme.success,
                       padx=25, pady=10, cursor="hand2")
        save.pack(side="right")
        save.bind("<Button-1>", lambda e: self._save_project())

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _save_project(self):
        """Sauvegarde un nouveau projet."""
        nom = self.entry_nom.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Veuillez entrer un nom de projet.")
            return

        try:
            revenus = float(self.entry_revenus.get() or 0)
            fixes = float(self.entry_fixes.get() or 0)
            variables = float(self.entry_variables.get() or 0)
            objectif = float(self.entry_objectif.get() or 0)
            duree = int(self.entry_duree.get() or 12)
            heures = float(self.entry_heures.get() or 0)
        except ValueError:
            messagebox.showerror("Erreur", "Valeurs numériques invalides.")
            return

        projet = storage.creer_projet(nom)
        projet["finances"] = {
            "revenus": revenus,
            "depenses_fixes": fixes,
            "depenses_variables": variables,
            "objectif": objectif,
            "duree_mois": duree
        }

        jours_map = {"lun": "lundi", "mar": "mardi", "mer": "mercredi",
                    "jeu": "jeudi", "ven": "vendredi", "sam": "samedi", "dim": "dimanche"}
        jours_dispo = [jours_map[j] for j, v in self.jours_vars.items() if v.get()]

        if jours_dispo and heures > 0:
            projet["planning"] = planning.generer_planning(jours_dispo, heures)
        else:
            projet["planning"] = planning.creer_planning_vide()

        projet["simulation"] = finance.analyser_finances(projet)
        projet["progression"] = finance.calculer_progression(projet["simulation"], objectif)

        if storage.ajouter_projet(projet):
            # Achievement
            self.achievements.enregistrer_activite("projet_cree")
            self._sauvegarder_achievements()

            messagebox.showinfo("Succès", f"Projet '{nom}' créé !")
            self._navigate("projects")
        else:
            messagebox.showerror("Erreur", "Erreur lors de la sauvegarde.")

    def _show_timer(self):
        """Affiche le timer Pomodoro."""
        self._clear_main()

        content = tk.Frame(self.main, bg=self.theme.bg_primary)
        content.pack(fill="both", expand=True)

        tk.Label(content, text="Timer Pomodoro", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(pady=30)

        # Timer display
        timer_frame = tk.Frame(content, bg=self.theme.bg_card, padx=60, pady=40)
        timer_frame.pack(pady=20)

        self.timer_label = tk.Label(timer_frame, text="25:00", font=("Segoe UI", 72, "bold"),
                                   fg=self.theme.accent, bg=self.theme.bg_card)
        self.timer_label.pack()

        self.timer_status = tk.Label(timer_frame, text="Prêt à démarrer",
                                    font=("Segoe UI", 14), fg=self.theme.text_secondary,
                                    bg=self.theme.bg_card)
        self.timer_status.pack(pady=10)

        # Boutons
        btn_frame = tk.Frame(content, bg=self.theme.bg_primary)
        btn_frame.pack(pady=20)

        start_btn = tk.Label(btn_frame, text="▶️ Démarrer", font=("Segoe UI", 12, "bold"),
                            fg=self.theme.text_primary, bg=self.theme.success,
                            padx=30, pady=12, cursor="hand2")
        start_btn.pack(side="left", padx=10)
        start_btn.bind("<Button-1>", lambda e: self._start_timer())

        pause_btn = tk.Label(btn_frame, text="⏸️ Pause", font=("Segoe UI", 12, "bold"),
                            fg=self.theme.text_primary, bg=self.theme.warning,
                            padx=30, pady=12, cursor="hand2")
        pause_btn.pack(side="left", padx=10)
        pause_btn.bind("<Button-1>", lambda e: self._pause_timer())

        reset_btn = tk.Label(btn_frame, text="🔄 Reset", font=("Segoe UI", 12, "bold"),
                            fg=self.theme.text_primary, bg=self.theme.danger,
                            padx=30, pady=12, cursor="hand2")
        reset_btn.pack(side="left", padx=10)
        reset_btn.bind("<Button-1>", lambda e: self._reset_timer())

        # Stats
        stats = self.time_tracker.calculer_statistiques_semaine()

        stats_frame = tk.Frame(content, bg=self.theme.bg_primary)
        stats_frame.pack(pady=30)

        tk.Label(stats_frame, text="Cette semaine", font=("Segoe UI", 16, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(pady=10)

        stats_grid = tk.Frame(stats_frame, bg=self.theme.bg_primary)
        stats_grid.pack()

        stat_items = [
            ("Temps total", f"{stats['temps_total']:.1f}h"),
            ("Sessions", str(stats["sessions_count"])),
            ("Pomodoros", str(stats["pomodoros_completes"]))
        ]

        for label, value in stat_items:
            card = tk.Frame(stats_grid, bg=self.theme.bg_card, padx=25, pady=15)
            card.pack(side="left", padx=10)

            tk.Label(card, text=value, font=("Segoe UI", 24, "bold"),
                    fg=self.theme.accent, bg=self.theme.bg_card).pack()
            tk.Label(card, text=label, font=("Segoe UI", 10),
                    fg=self.theme.text_muted, bg=self.theme.bg_card).pack()

    def _start_timer(self):
        """Démarre le timer."""
        if not self.timer_running:
            self.timer_running = True
            self.time_tracker.pomodoro.demarrer_travail()
            self._update_timer()
            self.timer_status.config(text="En cours...")

    def _pause_timer(self):
        """Met en pause le timer."""
        self.timer_running = False
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.timer_status.config(text="En pause")

    def _reset_timer(self):
        """Reset le timer."""
        self.timer_running = False
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.time_tracker.pomodoro.reinitialiser()
        self.timer_label.config(text="25:00")
        self.timer_status.config(text="Prêt à démarrer")

    def _update_timer(self):
        """Met à jour l'affichage du timer."""
        if self.timer_running:
            self.time_tracker.pomodoro.tick()
            self.timer_label.config(text=self.time_tracker.pomodoro.temps_formate)

            if self.time_tracker.pomodoro.temps_restant <= 0:
                self.timer_running = False
                self.timer_status.config(text="Terminé ! 🎉")
                self._sauvegarder_time_tracker()
                messagebox.showinfo("Pomodoro", "Session terminée !")
            else:
                self.timer_job = self.root.after(1000, self._update_timer)

    def _show_achievements(self):
        """Affiche les badges."""
        self._clear_main()

        canvas = tk.Canvas(self.main, bg=self.theme.bg_primary, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.theme.bg_primary)

        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Header
        tk.Label(content, text="Mes Badges", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=30)

        # Stats
        niveau = self.achievements.obtenir_progression_niveau()
        stats_frame = tk.Frame(content, bg=self.theme.bg_primary)
        stats_frame.pack(fill="x", padx=40, pady=10)

        stat_items = [
            ("Niveau", str(niveau["niveau"]), obtenir_couleur_niveau(niveau["niveau"])),
            ("Points", str(niveau["points_totaux"]), self.theme.accent),
            ("Badges", f"{len(self.achievements.badges_obtenus)}/{len(BADGES)}", self.theme.warning),
            ("Streak", f"{self.achievements.streak_actuel}j", self.theme.danger)
        ]

        for label, value, color in stat_items:
            card = tk.Frame(stats_frame, bg=self.theme.bg_card, padx=25, pady=15)
            card.pack(side="left", padx=10, expand=True)

            tk.Label(card, text=value, font=("Segoe UI", 28, "bold"),
                    fg=color, bg=self.theme.bg_card).pack()
            tk.Label(card, text=label, font=("Segoe UI", 11),
                    fg=self.theme.text_secondary, bg=self.theme.bg_card).pack()

        # Badges par catégorie
        categories = self.achievements.obtenir_badges_par_categorie()

        for cat_name, badges in categories.items():
            cat_frame = tk.Frame(content, bg=self.theme.bg_primary)
            cat_frame.pack(fill="x", padx=40, pady=15)

            tk.Label(cat_frame, text=cat_name.capitalize(), font=("Segoe UI", 16, "bold"),
                    fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", pady=10)

            badges_grid = tk.Frame(cat_frame, bg=self.theme.bg_primary)
            badges_grid.pack(fill="x")

            for badge in badges:
                self._create_badge_card(badges_grid, badge)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_badge_card(self, parent, badge):
        """Crée une carte de badge."""
        obtenu = badge.get("obtenu", False)
        bg = self.theme.bg_card if obtenu else self.theme.bg_input
        fg = self.theme.text_primary if obtenu else self.theme.text_muted

        card = tk.Frame(parent, bg=bg, padx=15, pady=12)
        card.pack(side="left", padx=5, pady=5)

        tk.Label(card, text=badge["icone"], font=("Segoe UI", 24),
                bg=bg).pack()

        tk.Label(card, text=badge["nom"], font=("Segoe UI", 10, "bold"),
                fg=fg, bg=bg).pack()

        tk.Label(card, text=f"+{badge['points']}pts", font=("Segoe UI", 8),
                fg=self.theme.text_muted, bg=bg).pack()

    def _show_scenarios(self):
        """Affiche les scénarios What-if."""
        self._clear_main()

        tk.Label(self.main, text="Scénarios What-if", font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(anchor="w", padx=40, pady=30)

        projets = storage.lister_projets()
        if not projets:
            tk.Label(self.main, text="Créez d'abord un projet pour utiliser les scénarios.",
                    font=("Segoe UI", 14), fg=self.theme.text_muted,
                    bg=self.theme.bg_primary).pack(pady=50)
            return

        # Sélection projet
        select_frame = tk.Frame(self.main, bg=self.theme.bg_primary)
        select_frame.pack(fill="x", padx=40, pady=10)

        tk.Label(select_frame, text="Projet:", font=("Segoe UI", 12),
                fg=self.theme.text_secondary, bg=self.theme.bg_primary).pack(side="left")

        self.scenario_projet_var = tk.StringVar()
        self.scenario_projet_var.set(projets[0]["nom"])

        projet_menu = ttk.Combobox(select_frame, textvariable=self.scenario_projet_var,
                                  values=[p["nom"] for p in projets], state="readonly")
        projet_menu.pack(side="left", padx=10)

        # Scénarios prédéfinis
        scenarios_frame = tk.Frame(self.main, bg=self.theme.bg_card, padx=30, pady=20)
        scenarios_frame.pack(fill="x", padx=40, pady=20)

        tk.Label(scenarios_frame, text="Comparer des scénarios", font=("Segoe UI", 14, "bold"),
                fg=self.theme.accent, bg=self.theme.bg_card).pack(anchor="w", pady=(0, 15))

        scenarios_options = [
            ("Réduire dépenses de 100€", {"depenses_ajustement": -100}),
            ("Réduire dépenses de 200€", {"depenses_ajustement": -200}),
            ("Augmenter revenus de 200€", {"revenus_ajustement": 200}),
            ("Objectif +50%", {"objectif_ajustement": 0.5})  # sera calculé
        ]

        self.scenario_vars = []
        for label, mods in scenarios_options:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(scenarios_frame, text=label, variable=var,
                               font=("Segoe UI", 11), fg=self.theme.text_primary,
                               bg=self.theme.bg_card, selectcolor=self.theme.bg_input)
            cb.pack(anchor="w", pady=2)
            self.scenario_vars.append((label, mods, var))

        # Bouton comparer
        compare_btn = tk.Label(scenarios_frame, text="📊 Comparer", font=("Segoe UI", 11, "bold"),
                              fg=self.theme.text_primary, bg=self.theme.accent,
                              padx=20, pady=10, cursor="hand2")
        compare_btn.pack(anchor="w", pady=15)
        compare_btn.bind("<Button-1>", lambda e: self._run_comparison())

        # Zone résultats
        self.scenario_results = tk.Frame(self.main, bg=self.theme.bg_primary)
        self.scenario_results.pack(fill="both", expand=True, padx=40, pady=10)

    def _run_comparison(self):
        """Exécute la comparaison de scénarios."""
        # Trouver le projet
        projets = storage.lister_projets()
        projet = next((p for p in projets if p["nom"] == self.scenario_projet_var.get()), None)

        if not projet:
            return

        finances = projet.get("finances", {})

        # Créer les scénarios sélectionnés
        scenarios = []
        for label, mods, var in self.scenario_vars:
            if var.get():
                if "objectif_ajustement" in mods and mods["objectif_ajustement"] == 0.5:
                    mods = {"objectif_ajustement": finances.get("objectif", 0) * 0.5}
                scenarios.append(Scenario(label, mods))

        if not scenarios:
            messagebox.showinfo("Info", "Sélectionnez au moins un scénario.")
            return

        # Comparer
        resultats = comparer_scenarios(finances, scenarios, finances.get("duree_mois", 12))

        # Afficher
        for widget in self.scenario_results.winfo_children():
            widget.destroy()

        tk.Label(self.scenario_results, text="Résultats de la comparaison",
                font=("Segoe UI", 14, "bold"), fg=self.theme.text_primary,
                bg=self.theme.bg_primary).pack(anchor="w", pady=10)

        # Graphique
        chart_canvas = tk.Canvas(self.scenario_results, width=600, height=300,
                                bg=self.theme.bg_card, highlightthickness=0)
        chart_canvas.pack(pady=10)

        from projectflow.charts import ComparisonChart
        chart = ComparisonChart(chart_canvas, 0, 0, 600, 300)
        chart.draw(resultats, "Évolution de l'épargne")

        # Tableau récap
        for r in resultats:
            row = tk.Frame(self.scenario_results, bg=self.theme.bg_card, padx=15, pady=10)
            row.pack(fill="x", pady=2)

            tk.Label(row, text=r["nom"], font=("Segoe UI", 11, "bold"),
                    fg=r.get("color", self.theme.text_primary),
                    bg=self.theme.bg_card, width=25, anchor="w").pack(side="left")

            mois_text = f"Mois {r['mois_objectif']}" if r.get("mois_objectif") else "Non atteint"
            tk.Label(row, text=mois_text, font=("Segoe UI", 11),
                    fg=self.theme.text_secondary, bg=self.theme.bg_card,
                    width=15).pack(side="left")

            tk.Label(row, text=f"{r['total']:,.0f}€", font=("Segoe UI", 11, "bold"),
                    fg=self.theme.success, bg=self.theme.bg_card).pack(side="right")

    def _show_settings(self):
        """Affiche les paramètres."""
        self._clear_main()

        # Header moderne
        header = tk.Frame(self.main, bg=self.theme.bg_primary)
        header.pack(fill="x", padx=50, pady=35)

        title_frame = tk.Frame(header, bg=self.theme.bg_primary)
        title_frame.pack(side="left")

        tk.Label(title_frame, text="⚙️", font=("Segoe UI", 28),
                bg=self.theme.bg_primary).pack(side="left", padx=(0, 10))

        tk.Label(title_frame, text="Réglages", font=("Segoe UI", 28, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(side="left")

        # Section Thèmes - Carte moderne
        theme_card = ModernCard(self.main, self.theme.bg_card)
        theme_inner = theme_card.get_card()
        theme_inner.config(padx=35, pady=25)
        theme_card.pack(fill="x", padx=50, pady=15)

        # Titre section
        section_header = tk.Frame(theme_inner, bg=self.theme.bg_card)
        section_header.pack(fill="x", pady=(0, 20))

        tk.Label(section_header, text="🎨", font=("Segoe UI", 18),
                bg=self.theme.bg_card).pack(side="left", padx=(0, 8))

        tk.Label(section_header, text="Thème d'apparence", font=("Segoe UI", 16, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_card).pack(side="left")

        tk.Label(section_header, text="Changement instantané", font=("Segoe UI", 9),
                fg=self.theme.success, bg=self.theme.bg_card).pack(side="left", padx=10)

        # Grille de thèmes moderne
        themes_grid = tk.Frame(theme_inner, bg=self.theme.bg_card)
        themes_grid.pack(fill="x")

        current_theme_name = None
        for name, t in THEMES.items():
            if t.nom == self.theme.nom:
                current_theme_name = name
                break

        for theme_name, theme in THEMES.items():
            # Carte de thème avec effet hover
            theme_option = ModernCard(themes_grid, theme.bg_primary)
            theme_option_inner = theme_option.get_card()
            theme_option_inner.config(padx=18, pady=15, cursor="hand2")
            theme_option.pack(side="left", padx=6, pady=5)

            # Indicateur de thème actif
            if theme_name == current_theme_name:
                active_indicator = tk.Label(theme_option_inner, text="✓ Actif",
                                           font=("Segoe UI", 8, "bold"),
                                           fg=theme.text_primary, bg=theme.success,
                                           padx=8, pady=2)
                active_indicator.pack(anchor="e")

            # Preview couleurs - Palette moderne
            preview = tk.Frame(theme_option_inner, bg=theme.bg_primary)
            preview.pack(pady=(5, 8))

            colors_to_show = [theme.accent, theme.success, theme.warning, theme.danger]
            for color in colors_to_show:
                color_box = tk.Frame(preview, bg=color, width=12, height=35)
                color_box.pack(side="left", padx=1)

            # Nom du thème
            name_label = tk.Label(theme_option_inner, text=theme.nom,
                                 font=("Segoe UI", 11, "bold"),
                                 fg=theme.text_primary, bg=theme.bg_primary)
            name_label.pack(pady=(0, 2))

            # Description de l'ambiance
            theme_descriptions = {
                "dark": "Sombre",
                "light": "Clair",
                "midnight": "Nuit profonde",
                "ocean": "Océan",
                "sunset": "Crépuscule",
                "forest": "Nature",
                "nord": "Nordique",
                "rose": "Romantique"
            }

            desc = theme_descriptions.get(theme_name, "")
            tk.Label(theme_option_inner, text=desc, font=("Segoe UI", 8),
                    fg=theme.text_muted, bg=theme.bg_primary).pack()

            # Binding pour changer le thème
            theme_option_inner.bind("<Button-1>", lambda e, n=theme_name: self._change_theme(n))
            name_label.bind("<Button-1>", lambda e, n=theme_name: self._change_theme(n))

            # Effet hover
            def on_enter(e, widget=theme_option_inner):
                widget.config(cursor="hand2")

            theme_option_inner.bind("<Enter>", on_enter)

        # Section Pomodoro - Carte moderne
        pomo_card = ModernCard(self.main, self.theme.bg_card)
        pomo_inner = pomo_card.get_card()
        pomo_inner.config(padx=35, pady=25)
        pomo_card.pack(fill="x", padx=50, pady=15)

        # Titre section
        pomo_header = tk.Frame(pomo_inner, bg=self.theme.bg_card)
        pomo_header.pack(fill="x", pady=(0, 20))

        tk.Label(pomo_header, text="⏱️", font=("Segoe UI", 18),
                bg=self.theme.bg_card).pack(side="left", padx=(0, 8))

        tk.Label(pomo_header, text="Configuration Timer", font=("Segoe UI", 16, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_card).pack(side="left")

        # Settings avec style moderne
        pomo_settings = [
            ("⏳ Durée de travail", self.time_tracker.pomodoro.DUREE_TRAVAIL, "minutes"),
            ("☕ Durée de pause courte", self.time_tracker.pomodoro.DUREE_PAUSE, "minutes"),
            ("🌙 Durée de pause longue", self.time_tracker.pomodoro.DUREE_PAUSE_LONGUE, "minutes")
        ]

        for icon_label, value, unit in pomo_settings:
            row = tk.Frame(pomo_inner, bg=self.theme.bg_input, padx=20, pady=12)
            row.pack(fill="x", pady=4)

            tk.Label(row, text=icon_label, font=("Segoe UI", 11, "bold"),
                    fg=self.theme.text_primary, bg=self.theme.bg_input).pack(side="left")

            value_frame = tk.Frame(row, bg=self.theme.accent, padx=12, pady=4)
            value_frame.pack(side="right")

            tk.Label(value_frame, text=f"{value} {unit}", font=("Segoe UI", 11, "bold"),
                    fg=self.theme.text_primary, bg=self.theme.accent).pack()

        # Footer avec version
        footer = tk.Frame(self.main, bg=self.theme.bg_primary)
        footer.pack(pady=40)

        version_card = tk.Frame(footer, bg=self.theme.bg_card, padx=25, pady=12)
        version_card.pack()

        tk.Label(version_card, text="✨ ProjectFlow Pro v2.0.0",
                font=("Segoe UI", 11, "bold"), fg=self.theme.accent,
                bg=self.theme.bg_card).pack()

    def _refresh_theme(self):
        """Rafraîchit l'interface avec le nouveau thème."""
        # Recharger le thème
        self.theme = self.theme_manager.theme

        # Mettre à jour la couleur de fond principale
        self.root.configure(bg=self.theme.bg_primary)

        # Reconstruire la sidebar
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        self._build_sidebar()

        # Rafraîchir la page courante
        current = self.current_page
        self._navigate(current)

    def _change_theme(self, theme_name):
        """Change le thème."""
        self.theme_manager.changer_theme(theme_name)
        self._refresh_theme()
        messagebox.showinfo("Thème", f"Thème '{THEMES[theme_name].nom}' appliqué !")

    def _open_project(self, projet):
        """Ouvre un projet."""
        self.current_projet = projet
        self._show_project_details()

    def _show_project_details(self):
        """Affiche les détails d'un projet."""
        self._clear_main()

        projet = self.current_projet
        if not projet:
            return

        # Scroll
        canvas = tk.Canvas(self.main, bg=self.theme.bg_primary, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=self.theme.bg_primary)

        content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Header
        header = tk.Frame(content, bg=self.theme.bg_primary)
        header.pack(fill="x", padx=40, pady=30)

        back = tk.Label(header, text="← Retour", font=("Segoe UI", 11),
                       fg=self.theme.text_secondary, bg=self.theme.bg_primary, cursor="hand2")
        back.pack(side="left")
        back.bind("<Button-1>", lambda e: self._navigate("projects"))

        tk.Label(header, text=projet["nom"], font=("Segoe UI", 24, "bold"),
                fg=self.theme.text_primary, bg=self.theme.bg_primary).pack(side="left", padx=20)

        # Export
        export_btn = tk.Label(header, text="📄 Exporter", font=("Segoe UI", 11, "bold"),
                             fg=self.theme.text_primary, bg=self.theme.accent,
                             padx=15, pady=8, cursor="hand2")
        export_btn.pack(side="right")
        export_btn.bind("<Button-1>", lambda e: self._export_project())

        # Contenu
        finances = projet.get("finances", {})
        simulation = projet.get("simulation", {})

        # Stats
        stats_frame = tk.Frame(content, bg=self.theme.bg_primary)
        stats_frame.pack(fill="x", padx=40, pady=10)

        progression = projet.get("progression", 0)
        epargne_mens = simulation.get("epargne_mensuelle", 0)

        stats = [
            ("Progression", f"{progression*100:.0f}%", self.theme.success if progression >= 1 else self.theme.accent),
            ("Épargne/mois", f"{epargne_mens:,.0f}€", self.theme.success),
            ("Objectif", f"{finances.get('objectif', 0):,.0f}€", self.theme.warning),
            ("Total épargné", f"{simulation.get('total_epargne', 0):,.0f}€", self.theme.accent)
        ]

        for label, value, color in stats:
            card = tk.Frame(stats_frame, bg=self.theme.bg_card, padx=20, pady=15)
            card.pack(side="left", padx=5, expand=True)

            tk.Label(card, text=value, font=("Segoe UI", 22, "bold"),
                    fg=color, bg=self.theme.bg_card).pack()
            tk.Label(card, text=label, font=("Segoe UI", 10),
                    fg=self.theme.text_secondary, bg=self.theme.bg_card).pack()

        # Graphique
        if simulation.get("tableau_mensuel"):
            chart_frame = tk.Frame(content, bg=self.theme.bg_card, padx=20, pady=20)
            chart_frame.pack(fill="x", padx=40, pady=15)

            tk.Label(chart_frame, text="Évolution de l'épargne", font=("Segoe UI", 14, "bold"),
                    fg=self.theme.text_primary, bg=self.theme.bg_card).pack(anchor="w", pady=(0, 10))

            chart_canvas = tk.Canvas(chart_frame, width=700, height=280,
                                    bg=self.theme.bg_card, highlightthickness=0)
            chart_canvas.pack()

            chart = LineChart(chart_canvas, 0, 0, 700, 280)
            chart.draw(simulation["tableau_mensuel"], objectif=finances.get("objectif", 0))

        # Recommandations
        recommandations = generer_recommandations(finances, simulation)
        if recommandations:
            reco_frame = tk.Frame(content, bg=self.theme.bg_card, padx=20, pady=20)
            reco_frame.pack(fill="x", padx=40, pady=15)

            tk.Label(reco_frame, text="💡 Recommandations", font=("Segoe UI", 14, "bold"),
                    fg=self.theme.text_primary, bg=self.theme.bg_card).pack(anchor="w", pady=(0, 10))

            for reco in recommandations[:3]:
                reco_card = tk.Frame(reco_frame, bg=self.theme.bg_input, padx=15, pady=10)
                reco_card.pack(fill="x", pady=5)

                type_colors = {
                    "success": self.theme.success,
                    "warning": self.theme.warning,
                    "danger": self.theme.danger,
                    "info": self.theme.accent
                }
                color = type_colors.get(reco["type"], self.theme.accent)

                tk.Label(reco_card, text=reco["titre"], font=("Segoe UI", 11, "bold"),
                        fg=color, bg=self.theme.bg_input).pack(anchor="w")
                tk.Label(reco_card, text=reco["message"], font=("Segoe UI", 10),
                        fg=self.theme.text_secondary, bg=self.theme.bg_input,
                        wraplength=600).pack(anchor="w")

                if reco.get("impact"):
                    tk.Label(reco_card, text=f"Impact: {reco['impact']}", font=("Segoe UI", 9),
                            fg=self.theme.text_muted, bg=self.theme.bg_input).pack(anchor="w")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _export_project(self):
        """Exporte le projet."""
        if not self.current_projet:
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML", "*.html")],
            initialfilename=f"rapport_{self.current_projet['nom'].replace(' ', '_')}.html"
        )

        if filename:
            try:
                export_html.exporter_rapport(self.current_projet, filename)

                # Achievement
                self.achievements.enregistrer_activite("export_realise")
                self._sauvegarder_achievements()

                messagebox.showinfo("Succès", f"Rapport exporté:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def run(self):
        """Lance l'application."""
        self.root.mainloop()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
