"""
Module themes - Système de thèmes personnalisables.

Ce module gère :
- Thèmes prédéfinis (sombre, clair, etc.)
- Personnalisation des couleurs
- Sauvegarde des préférences
"""

from typing import Dict, Optional
import json
import os


class Theme:
    """Représente un thème de l'application."""

    def __init__(self, nom: str, couleurs: Dict[str, str]):
        self.nom = nom
        self.couleurs = couleurs

    @property
    def bg_primary(self) -> str:
        return self.couleurs.get("bg_primary", "#1a1a2e")

    @property
    def bg_secondary(self) -> str:
        return self.couleurs.get("bg_secondary", "#16213e")

    @property
    def bg_card(self) -> str:
        return self.couleurs.get("bg_card", "#1f2940")

    @property
    def bg_input(self) -> str:
        return self.couleurs.get("bg_input", "#2d3a4f")

    @property
    def accent(self) -> str:
        return self.couleurs.get("accent", "#4361ee")

    @property
    def accent_hover(self) -> str:
        return self.couleurs.get("accent_hover", "#3a56d4")

    @property
    def success(self) -> str:
        return self.couleurs.get("success", "#06d6a0")

    @property
    def warning(self) -> str:
        return self.couleurs.get("warning", "#ffd166")

    @property
    def danger(self) -> str:
        return self.couleurs.get("danger", "#ef476f")

    @property
    def text_primary(self) -> str:
        return self.couleurs.get("text_primary", "#ffffff")

    @property
    def text_secondary(self) -> str:
        return self.couleurs.get("text_secondary", "#a0aec0")

    @property
    def text_muted(self) -> str:
        return self.couleurs.get("text_muted", "#718096")

    @property
    def border(self) -> str:
        return self.couleurs.get("border", "#2d3a4f")

    def to_dict(self) -> dict:
        return {
            "nom": self.nom,
            "couleurs": self.couleurs
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Theme':
        return cls(
            nom=data.get("nom", "Custom"),
            couleurs=data.get("couleurs", {})
        )


# Thèmes prédéfinis
THEMES = {
    "dark": Theme("Sombre", {
        "bg_primary": "#1a1a2e",
        "bg_secondary": "#16213e",
        "bg_card": "#1f2940",
        "bg_input": "#2d3a4f",
        "accent": "#4361ee",
        "accent_hover": "#3a56d4",
        "success": "#06d6a0",
        "warning": "#ffd166",
        "danger": "#ef476f",
        "text_primary": "#ffffff",
        "text_secondary": "#a0aec0",
        "text_muted": "#718096",
        "border": "#2d3a4f"
    }),

    "light": Theme("Clair", {
        "bg_primary": "#f7fafc",
        "bg_secondary": "#edf2f7",
        "bg_card": "#ffffff",
        "bg_input": "#e2e8f0",
        "accent": "#4361ee",
        "accent_hover": "#3a56d4",
        "success": "#38a169",
        "warning": "#d69e2e",
        "danger": "#e53e3e",
        "text_primary": "#1a202c",
        "text_secondary": "#4a5568",
        "text_muted": "#718096",
        "border": "#e2e8f0"
    }),

    "midnight": Theme("Minuit", {
        "bg_primary": "#0d1117",
        "bg_secondary": "#161b22",
        "bg_card": "#21262d",
        "bg_input": "#30363d",
        "accent": "#58a6ff",
        "accent_hover": "#4c8ed9",
        "success": "#3fb950",
        "warning": "#d29922",
        "danger": "#f85149",
        "text_primary": "#c9d1d9",
        "text_secondary": "#8b949e",
        "text_muted": "#6e7681",
        "border": "#30363d"
    }),

    "ocean": Theme("Océan", {
        "bg_primary": "#0a192f",
        "bg_secondary": "#112240",
        "bg_card": "#1d3557",
        "bg_input": "#233554",
        "accent": "#64ffda",
        "accent_hover": "#4cd9b7",
        "success": "#64ffda",
        "warning": "#ffd166",
        "danger": "#ff6b6b",
        "text_primary": "#ccd6f6",
        "text_secondary": "#8892b0",
        "text_muted": "#495670",
        "border": "#233554"
    }),

    "sunset": Theme("Coucher de soleil", {
        "bg_primary": "#1a1423",
        "bg_secondary": "#2d1f3d",
        "bg_card": "#3d2a54",
        "bg_input": "#4a3563",
        "accent": "#ff6b6b",
        "accent_hover": "#ee5a5a",
        "success": "#51cf66",
        "warning": "#fcc419",
        "danger": "#ff6b6b",
        "text_primary": "#ffffff",
        "text_secondary": "#c4b5d4",
        "text_muted": "#8e7aa8",
        "border": "#4a3563"
    }),

    "forest": Theme("Forêt", {
        "bg_primary": "#1a2f1a",
        "bg_secondary": "#1e3d1e",
        "bg_card": "#264d26",
        "bg_input": "#2e5c2e",
        "accent": "#68d391",
        "accent_hover": "#56c47e",
        "success": "#68d391",
        "warning": "#f6e05e",
        "danger": "#fc8181",
        "text_primary": "#f0fff4",
        "text_secondary": "#9ae6b4",
        "text_muted": "#68d391",
        "border": "#2e5c2e"
    }),

    "nord": Theme("Nord", {
        "bg_primary": "#2e3440",
        "bg_secondary": "#3b4252",
        "bg_card": "#434c5e",
        "bg_input": "#4c566a",
        "accent": "#88c0d0",
        "accent_hover": "#81a1c1",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "danger": "#bf616a",
        "text_primary": "#eceff4",
        "text_secondary": "#d8dee9",
        "text_muted": "#7b88a1",
        "border": "#4c566a"
    }),

    "rose": Theme("Rose", {
        "bg_primary": "#1f1a24",
        "bg_secondary": "#2a2231",
        "bg_card": "#352b3d",
        "bg_input": "#40354a",
        "accent": "#f472b6",
        "accent_hover": "#ec4899",
        "success": "#34d399",
        "warning": "#fbbf24",
        "danger": "#f87171",
        "text_primary": "#fdf2f8",
        "text_secondary": "#f9a8d4",
        "text_muted": "#9d7aa0",
        "border": "#40354a"
    })
}


class ThemeManager:
    """Gestionnaire des thèmes."""

    def __init__(self, fichier_config: str = "projectflow_theme.json"):
        self.fichier_config = fichier_config
        self.theme_actuel = THEMES["dark"]
        self.themes_personnalises = {}
        self.charger_preferences()

    def charger_preferences(self):
        """Charge les préférences de thème."""
        if os.path.exists(self.fichier_config):
            try:
                with open(self.fichier_config, "r", encoding="utf-8") as f:
                    data = json.load(f)

                theme_nom = data.get("theme_actuel", "dark")
                if theme_nom in THEMES:
                    self.theme_actuel = THEMES[theme_nom]
                elif theme_nom in self.themes_personnalises:
                    self.theme_actuel = self.themes_personnalises[theme_nom]

                # Charger thèmes personnalisés
                for nom, theme_data in data.get("themes_personnalises", {}).items():
                    self.themes_personnalises[nom] = Theme.from_dict(theme_data)

            except (json.JSONDecodeError, IOError):
                pass

    def sauvegarder_preferences(self):
        """Sauvegarde les préférences de thème."""
        data = {
            "theme_actuel": self.theme_actuel.nom,
            "themes_personnalises": {
                nom: theme.to_dict()
                for nom, theme in self.themes_personnalises.items()
            }
        }

        try:
            with open(self.fichier_config, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError:
            pass

    def changer_theme(self, nom: str):
        """Change le thème actuel."""
        if nom in THEMES:
            self.theme_actuel = THEMES[nom]
        elif nom in self.themes_personnalises:
            self.theme_actuel = self.themes_personnalises[nom]

        self.sauvegarder_preferences()

    def creer_theme_personnalise(self, nom: str, couleurs: Dict[str, str]):
        """Crée un thème personnalisé."""
        self.themes_personnalises[nom] = Theme(nom, couleurs)
        self.sauvegarder_preferences()

    def supprimer_theme_personnalise(self, nom: str):
        """Supprime un thème personnalisé."""
        if nom in self.themes_personnalises:
            del self.themes_personnalises[nom]
            self.sauvegarder_preferences()

    def lister_themes(self) -> Dict[str, Theme]:
        """Liste tous les thèmes disponibles."""
        tous = {}
        tous.update(THEMES)
        tous.update(self.themes_personnalises)
        return tous

    @property
    def theme(self) -> Theme:
        """Retourne le thème actuel."""
        return self.theme_actuel


# Instance globale
_theme_manager: Optional[ThemeManager] = None


def obtenir_theme_manager() -> ThemeManager:
    """Retourne l'instance globale du gestionnaire de thèmes."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def obtenir_theme() -> Theme:
    """Retourne le thème actuel."""
    return obtenir_theme_manager().theme
