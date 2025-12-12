"""
ProjectFlow Pro - Interface Flet Ultra-Moderne

Nouvelle interface basée sur Flet (Flutter) avec :
- Material Design 3
- Animations fluides
- Thèmes sombre/clair
- Effets visuels modernes
- Cross-platform (desktop/web/mobile)
"""

import flet as ft
from datetime import datetime
import os
import sys

# Imports des modules ProjectFlow
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projectflow import storage, finance
from projectflow.themes import obtenir_theme_manager, THEMES
from projectflow.achievements import AchievementManager, obtenir_titre_niveau, obtenir_couleur_niveau
from projectflow.timer import TimeTracker


class ModernCard(ft.Container):
    """Carte moderne Flet avec ombre et coins arrondis."""

    def __init__(self, content, **kwargs):
        super().__init__(
            content=content,
            border_radius=ft.border_radius.all(16),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            padding=20,
            **kwargs
        )


class StatCard(ft.Container):
    """Carte de statistique moderne avec icône et valeur."""

    def __init__(self, label: str, value: str, icon: str, color: str):
        # Icône avec background coloré
        icon_container = ft.Container(
            content=ft.Text(icon, size=28),
            bgcolor=color,
            border_radius=12,
            padding=12,
            width=60,
            height=60,
        )

        # Valeur en grand
        value_text = ft.Text(
            value,
            size=32,
            weight=ft.FontWeight.BOLD,
            color=color,
        )

        # Label
        label_text = ft.Text(
            label,
            size=12,
            color=ft.colors.ON_SURFACE_VARIANT,
        )

        super().__init__(
            content=ft.Column([
                icon_container,
                ft.Container(height=12),  # Spacing
                value_text,
                label_text,
            ], tight=True),
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            padding=22,
            expand=1,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
        )


class NavigationButton(ft.Container):
    """Bouton de navigation moderne avec indicateur."""

    def __init__(self, icon: str, label: str, is_active: bool, on_click):
        self.is_active = is_active

        # Indicateur actif (barre latérale)
        indicator = ft.Container(
            width=4,
            bgcolor=ft.colors.PRIMARY if is_active else ft.colors.TRANSPARENT,
            border_radius=ft.border_radius.only(top_right=2, bottom_right=2),
        )

        # Bouton
        button_content = ft.Row([
            ft.Text(f"  {icon}  {label}",
                   size=14,
                   weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                   color=ft.colors.PRIMARY if is_active else ft.colors.ON_SURFACE_VARIANT),
        ], expand=True)

        super().__init__(
            content=ft.Row([
                indicator,
                button_content,
            ], spacing=0),
            bgcolor=ft.colors.SURFACE_VARIANT if is_active else ft.colors.TRANSPARENT,
            border_radius=ft.border_radius.only(top_right=12, bottom_right=12),
            padding=ft.padding.only(top=14, bottom=14, right=18),
            on_click=on_click,
            ink=True,
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
        )


class ProjectFlowApp:
    """Application principale ProjectFlow Pro avec Flet."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.current_page = "dashboard"

        # Configuration de la page
        self.page.title = "✨ ProjectFlow Pro"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 1450
        self.page.window_height = 850
        self.page.window_min_width = 1300
        self.page.window_min_height = 750

        # Gestionnaires
        self.theme_manager = obtenir_theme_manager()
        self.achievements = self._charger_achievements()
        self.time_tracker = self._charger_time_tracker()

        # Construire l'interface
        self._build_ui()

    def _charger_achievements(self) -> AchievementManager:
        """Charge les achievements."""
        try:
            if os.path.exists("projectflow_achievements.json"):
                import json
                with open("projectflow_achievements.json", "r", encoding="utf-8") as f:
                    return AchievementManager.from_dict(json.load(f))
        except:
            pass
        return AchievementManager()

    def _charger_time_tracker(self) -> TimeTracker:
        """Charge le time tracker."""
        try:
            if os.path.exists("projectflow_time.json"):
                import json
                with open("projectflow_time.json", "r", encoding="utf-8") as f:
                    return TimeTracker.from_dict(json.load(f))
        except:
            pass
        return TimeTracker()

    def _build_ui(self):
        """Construit l'interface principale."""
        # Navigation Rail (Sidebar)
        sidebar = self._build_sidebar()

        # Zone principale
        self.main_content = ft.Container(
            content=self._build_dashboard(),
            expand=True,
            bgcolor=ft.colors.SURFACE,
        )

        # Layout principal
        layout = ft.Row([
            sidebar,
            self.main_content,
        ], spacing=0, expand=True)

        self.page.add(layout)

    def _build_sidebar(self):
        """Construit la sidebar moderne."""
        # Header avec logo
        logo = ft.Container(
            content=ft.Column([
                ft.Text("✨ ProjectFlow",
                       size=22,
                       weight=ft.FontWeight.BOLD,
                       color=ft.colors.PRIMARY),
                ft.Container(
                    content=ft.Text("PRO",
                                   size=10,
                                   weight=ft.FontWeight.BOLD,
                                   color=ft.colors.ON_PRIMARY),
                    bgcolor=ft.colors.PRIMARY,
                    border_radius=4,
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            padding=20,
        )

        # Carte de niveau
        niveau_info = self.achievements.obtenir_progression_niveau()
        titre = obtenir_titre_niveau(niveau_info["niveau"])
        couleur_hex = obtenir_couleur_niveau(niveau_info["niveau"])

        niveau_card = ModernCard(
            content=ft.Column([
                ft.Text(f"Niveau {niveau_info['niveau']}",
                       size=10,
                       weight=ft.FontWeight.BOLD,
                       color=ft.colors.ON_SURFACE_VARIANT),
                ft.Text(titre,
                       size=14,
                       weight=ft.FontWeight.BOLD,
                       color=couleur_hex),
                ft.Container(height=8),
                ft.ProgressBar(
                    value=niveau_info["progression"],
                    color=couleur_hex,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    height=8,
                    border_radius=4,
                ),
                ft.Container(height=5),
                ft.Text(f"{niveau_info['points_totaux']} points",
                       size=9,
                       color=ft.colors.ON_SURFACE_VARIANT),
            ], spacing=2),
            padding=15,
        )

        # Navigation
        nav_items = [
            ("dashboard", "📊", "Dashboard"),
            ("projects", "📁", "Projets"),
            ("new", "➕", "Nouveau"),
            ("timer", "⏱️", "Timer"),
            ("achievements", "🏆", "Badges"),
            ("scenarios", "🔮", "Scénarios"),
            ("settings", "⚙️", "Réglages"),
        ]

        nav_buttons = ft.Column(
            [NavigationButton(icon, label, key == self.current_page,
                             lambda e, k=key: self._navigate(k))
             for key, icon, label in nav_items],
            spacing=3,
        )

        # Streak card
        streak_card = ModernCard(
            content=ft.Column([
                ft.Row([
                    ft.Text("🔥", size=20),
                    ft.Text("Streak", size=11, weight=ft.FontWeight.BOLD),
                ], spacing=5),
                ft.Text(
                    str(self.achievements.streak_actuel),
                    size=36,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.AMBER,
                ),
                ft.Text(
                    "jours consécutifs",
                    size=10,
                    color=ft.colors.ON_SURFACE_VARIANT,
                ),
                ft.Container(
                    content=ft.Text(
                        f"🏆 Record: {self.achievements.meilleur_streak} jours",
                        size=9,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE_VARIANT,
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    margin=ft.margin.only(top=10),
                ) if self.achievements.meilleur_streak > self.achievements.streak_actuel else ft.Container(),
            ], horizontal_alignment=ft.CrossAxisAlignment.START, spacing=4),
            padding=18,
        )

        # Sidebar complète
        sidebar = ft.Container(
            content=ft.Column([
                logo,
                niveau_card,
                ft.Container(height=20),
                nav_buttons,
                ft.Container(expand=True),  # Spacer
                streak_card,
            ], spacing=0),
            width=280,
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=ft.padding.only(left=12, top=25, right=12, bottom=20),
        )

        return sidebar

    def _build_dashboard(self):
        """Construit le tableau de bord."""
        # Header avec date
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Text("📊", size=28),
                    ft.Text("Tableau de bord",
                           size=28,
                           weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Container(
                    content=ft.Text(
                        f"📅 {datetime.now().strftime('%d %B %Y')}",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SURFACE_VARIANT,
                    ),
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=50, vertical=35),
        )

        # Stats rapides
        projets = storage.lister_projets()
        total_epargne = sum(p.get("simulation", {}).get("total_epargne", 0) for p in projets)
        objectifs_atteints = sum(1 for p in projets if p.get("progression", 0) >= 1)

        stats = ft.Row([
            StatCard("Projets actifs", str(len(projets)), "📁", ft.colors.BLUE),
            StatCard("Épargne totale", f"{total_epargne:,.0f}€", "💰", ft.colors.GREEN),
            StatCard("Objectifs atteints", str(objectifs_atteints), "🎯", ft.colors.ORANGE),
            StatCard("Badges débloqués", str(len(self.achievements.badges_obtenus)), "🏆", ft.colors.RED),
        ], spacing=15)

        stats_container = ft.Container(
            content=stats,
            padding=ft.padding.symmetric(horizontal=50),
        )

        # Message de bienvenue si pas de projets
        if not projets:
            welcome_card = ModernCard(
                content=ft.Column([
                    ft.Text("👋 Bienvenue sur ProjectFlow Pro !",
                           size=24,
                           weight=ft.FontWeight.BOLD),
                    ft.Container(height=10),
                    ft.Text("Créez votre premier projet pour commencer votre aventure financière !",
                           size=14,
                           color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "➕ Créer mon premier projet",
                        icon=ft.icons.ADD,
                        on_click=lambda e: self._navigate("new"),
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=30, vertical=15),
                        ),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=50,
            )

            welcome_container = ft.Container(
                content=welcome_card,
                padding=ft.padding.symmetric(horizontal=50, vertical=20),
            )

            return ft.Column([
                header,
                stats_container,
                welcome_container,
            ], scroll=ft.ScrollMode.AUTO)

        # Liste des projets récents
        projets_list = ft.Column(spacing=10)

        for projet in projets[:3]:
            progression = projet.get("progression", 0)
            finances = projet.get("finances", {})

            projet_card = ModernCard(
                content=ft.Column([
                    ft.Row([
                        ft.Text(projet["nom"],
                               size=16,
                               weight=ft.FontWeight.BOLD),
                        ft.Text(f"{progression*100:.0f}%",
                               size=14,
                               weight=ft.FontWeight.BOLD,
                               color=ft.colors.GREEN if progression >= 1 else ft.colors.PRIMARY),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Container(height=10),
                    ft.ProgressBar(
                        value=progression,
                        color=ft.colors.GREEN if progression >= 1 else ft.colors.PRIMARY,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        height=8,
                        border_radius=4,
                    ),
                    ft.Container(height=10),
                    ft.Text(f"Objectif: {finances.get('objectif', 0):,.0f}€",
                           size=12,
                           color=ft.colors.ON_SURFACE_VARIANT),
                ]),
            )

            projets_list.controls.append(projet_card)

        projets_section = ft.Container(
            content=ft.Column([
                ft.Text("Projets récents",
                       size=16,
                       weight=ft.FontWeight.BOLD),
                ft.Container(height=15),
                projets_list,
            ]),
            padding=ft.padding.symmetric(horizontal=50, vertical=20),
        )

        # Dashboard complet avec scroll
        return ft.Column([
            header,
            stats_container,
            projets_section,
        ], scroll=ft.ScrollMode.AUTO, expand=True)

    def _navigate(self, page_key: str):
        """Navigation entre les pages."""
        self.current_page = page_key

        # Mettre à jour le contenu principal
        if page_key == "dashboard":
            new_content = self._build_dashboard()
        elif page_key == "settings":
            new_content = self._build_settings()
        else:
            # Pages non implémentées - placeholder
            new_content = ft.Container(
                content=ft.Column([
                    ft.Text(f"Page {page_key}", size=28, weight=ft.FontWeight.BOLD),
                    ft.Text("En construction... 🚧", size=16, color=ft.colors.ON_SURFACE_VARIANT),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=50,
                alignment=ft.alignment.center,
                expand=True,
            )

        self.main_content.content = new_content

        # Reconstruire la sidebar pour mettre à jour les indicateurs
        self.page.controls.clear()
        self._build_ui()
        self.page.update()

    def _build_settings(self):
        """Construit la page de paramètres."""
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Text("⚙️", size=28),
                ft.Text("Réglages", size=28, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=50, vertical=35),
        )

        # Switch thème sombre/clair
        def toggle_theme(e):
            self.page.theme_mode = (
                ft.ThemeMode.LIGHT
                if self.page.theme_mode == ft.ThemeMode.DARK
                else ft.ThemeMode.DARK
            )
            self.page.update()

        theme_card = ModernCard(
            content=ft.Column([
                ft.Row([
                    ft.Text("🎨", size=18),
                    ft.Text("Thème d'apparence",
                           size=16,
                           weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Container(height=10),
                ft.Row([
                    ft.Text("Mode sombre", size=14),
                    ft.Switch(
                        value=self.page.theme_mode == ft.ThemeMode.DARK,
                        on_change=toggle_theme,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(
                    content=ft.Text(
                        "✨ Changement instantané",
                        size=9,
                        color=ft.colors.GREEN,
                    ),
                    margin=ft.margin.only(top=5),
                ),
            ]),
            padding=35,
        )

        # Timer Pomodoro
        pomo_card = ModernCard(
            content=ft.Column([
                ft.Row([
                    ft.Text("⏱️", size=18),
                    ft.Text("Configuration Timer",
                           size=16,
                           weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Container(height=20),
                ft.Row([
                    ft.Text("⏳ Durée de travail", size=14),
                    ft.Container(
                        content=ft.Text(f"{self.time_tracker.pomodoro.DUREE_TRAVAIL} minutes",
                                       size=12,
                                       weight=ft.FontWeight.BOLD,
                                       color=ft.colors.ON_PRIMARY),
                        bgcolor=ft.colors.PRIMARY,
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Row([
                    ft.Text("☕ Durée de pause courte", size=14),
                    ft.Container(
                        content=ft.Text(f"{self.time_tracker.pomodoro.DUREE_PAUSE} minutes",
                                       size=12,
                                       weight=ft.FontWeight.BOLD,
                                       color=ft.colors.ON_PRIMARY),
                        bgcolor=ft.colors.PRIMARY,
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Row([
                    ft.Text("🌙 Durée de pause longue", size=14),
                    ft.Container(
                        content=ft.Text(f"{self.time_tracker.pomodoro.DUREE_PAUSE_LONGUE} minutes",
                                       size=12,
                                       weight=ft.FontWeight.BOLD,
                                       color=ft.colors.ON_PRIMARY),
                        bgcolor=ft.colors.PRIMARY,
                        border_radius=8,
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ]),
            padding=35,
        )

        # Version
        version_card = ft.Container(
            content=ft.Text(
                "✨ ProjectFlow Pro v2.0.0 - Flet Edition",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.PRIMARY,
            ),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=25, vertical=12),
        )

        settings_content = ft.Container(
            content=ft.Column([
                theme_card,
                ft.Container(height=15),
                pomo_card,
            ]),
            padding=ft.padding.symmetric(horizontal=50),
        )

        footer = ft.Container(
            content=version_card,
            padding=40,
            alignment=ft.alignment.center,
        )

        return ft.Column([
            header,
            settings_content,
            footer,
        ], scroll=ft.ScrollMode.AUTO, expand=True)


def main(page: ft.Page):
    """Point d'entrée de l'application Flet."""
    ProjectFlowApp(page)


if __name__ == "__main__":
    ft.app(target=main)
