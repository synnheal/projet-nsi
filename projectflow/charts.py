"""
Module charts - Génération de graphiques pour ProjectFlow.

Ce module crée des graphiques en utilisant tkinter Canvas,
sans dépendances externes (pas besoin de matplotlib).
"""

import math
from typing import List, Tuple, Optional


class ChartColors:
    """Couleurs pour les graphiques."""
    PRIMARY = "#4361ee"
    SUCCESS = "#06d6a0"
    WARNING = "#ffd166"
    DANGER = "#ef476f"
    PURPLE = "#7209b7"
    CYAN = "#00b4d8"
    ORANGE = "#fb8500"
    PINK = "#ff006e"

    PALETTE = [PRIMARY, SUCCESS, WARNING, DANGER, PURPLE, CYAN, ORANGE, PINK]

    BG_DARK = "#1a1a2e"
    BG_CARD = "#1f2940"
    TEXT = "#ffffff"
    TEXT_MUTED = "#718096"
    GRID = "#2d3a4f"


class LineChart:
    """Graphique en ligne pour l'évolution de l'épargne."""

    def __init__(self, canvas, x, y, width, height):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = 50

    def draw(self, data: List[dict], title: str = "", objectif: float = None):
        """
        Dessine le graphique linéaire.

        Args:
            data: Liste de dictionnaires avec 'mois' et 'cumul'
            title: Titre du graphique
            objectif: Ligne horizontale pour l'objectif
        """
        if not data:
            return

        # Zone de dessin
        chart_x = self.x + self.padding
        chart_y = self.y + 30
        chart_width = self.width - self.padding * 2
        chart_height = self.height - 80

        # Valeurs min/max
        values = [d.get('cumul', 0) for d in data]
        max_val = max(max(values), objectif or 0) * 1.1
        min_val = 0

        # Titre
        if title:
            self.canvas.create_text(
                self.x + self.width // 2, self.y + 15,
                text=title, fill=ChartColors.TEXT,
                font=("Segoe UI", 12, "bold")
            )

        # Grille horizontale
        num_lines = 5
        for i in range(num_lines + 1):
            y_pos = chart_y + chart_height - (i * chart_height / num_lines)
            val = min_val + (i * (max_val - min_val) / num_lines)

            # Ligne de grille
            self.canvas.create_line(
                chart_x, y_pos, chart_x + chart_width, y_pos,
                fill=ChartColors.GRID, dash=(2, 4)
            )

            # Label
            self.canvas.create_text(
                chart_x - 10, y_pos,
                text=f"{val:,.0f}€", fill=ChartColors.TEXT_MUTED,
                font=("Segoe UI", 8), anchor="e"
            )

        # Ligne d'objectif
        if objectif and objectif <= max_val:
            obj_y = chart_y + chart_height - (objectif / max_val * chart_height)
            self.canvas.create_line(
                chart_x, obj_y, chart_x + chart_width, obj_y,
                fill=ChartColors.SUCCESS, width=2, dash=(5, 3)
            )
            self.canvas.create_text(
                chart_x + chart_width + 5, obj_y,
                text="Objectif", fill=ChartColors.SUCCESS,
                font=("Segoe UI", 8), anchor="w"
            )

        # Points et lignes
        points = []
        for i, d in enumerate(data):
            x_pos = chart_x + (i / max(len(data) - 1, 1)) * chart_width
            y_pos = chart_y + chart_height - (d['cumul'] / max_val * chart_height)
            points.append((x_pos, y_pos))

        # Aire sous la courbe (gradient effect)
        if len(points) >= 2:
            polygon_points = [(chart_x, chart_y + chart_height)]
            polygon_points.extend(points)
            polygon_points.append((chart_x + chart_width, chart_y + chart_height))

            self.canvas.create_polygon(
                polygon_points, fill=ChartColors.PRIMARY,
                stipple="gray25", outline=""
            )

        # Lignes entre points
        for i in range(len(points) - 1):
            color = ChartColors.SUCCESS if data[i+1].get('objectif_atteint') else ChartColors.PRIMARY
            self.canvas.create_line(
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1],
                fill=color, width=3, smooth=True
            )

        # Points
        for i, (px, py) in enumerate(points):
            color = ChartColors.SUCCESS if data[i].get('objectif_atteint') else ChartColors.PRIMARY
            self.canvas.create_oval(
                px - 5, py - 5, px + 5, py + 5,
                fill=color, outline=ChartColors.TEXT, width=2
            )

        # Labels X (mois)
        step = max(1, len(data) // 6)
        for i in range(0, len(data), step):
            x_pos = chart_x + (i / max(len(data) - 1, 1)) * chart_width
            self.canvas.create_text(
                x_pos, chart_y + chart_height + 15,
                text=f"M{data[i]['mois']}", fill=ChartColors.TEXT_MUTED,
                font=("Segoe UI", 8)
            )


class PieChart:
    """Graphique camembert pour la répartition des dépenses."""

    def __init__(self, canvas, x, y, size):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size

    def draw(self, data: List[Tuple[str, float]], title: str = ""):
        """
        Dessine le camembert.

        Args:
            data: Liste de tuples (label, valeur)
            title: Titre du graphique
        """
        if not data:
            return

        total = sum(v for _, v in data)
        if total == 0:
            return

        # Titre
        if title:
            self.canvas.create_text(
                self.x + self.size // 2, self.y + 15,
                text=title, fill=ChartColors.TEXT,
                font=("Segoe UI", 12, "bold")
            )

        # Centre et rayon
        cx = self.x + self.size // 2
        cy = self.y + self.size // 2 + 20
        radius = self.size // 2 - 40

        # Dessiner les parts
        start_angle = 90
        for i, (label, value) in enumerate(data):
            extent = (value / total) * 360
            color = ChartColors.PALETTE[i % len(ChartColors.PALETTE)]

            # Arc
            self.canvas.create_arc(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                start=start_angle, extent=-extent,
                fill=color, outline=ChartColors.BG_DARK, width=2
            )

            # Label avec pourcentage
            mid_angle = math.radians(start_angle - extent / 2)
            label_radius = radius + 25
            lx = cx + label_radius * math.cos(mid_angle)
            ly = cy - label_radius * math.sin(mid_angle)

            pct = (value / total) * 100
            self.canvas.create_text(
                lx, ly, text=f"{label}\n{pct:.1f}%",
                fill=ChartColors.TEXT, font=("Segoe UI", 8),
                justify="center"
            )

            start_angle -= extent

        # Cercle central (donut effect)
        inner_radius = radius * 0.5
        self.canvas.create_oval(
            cx - inner_radius, cy - inner_radius,
            cx + inner_radius, cy + inner_radius,
            fill=ChartColors.BG_CARD, outline=""
        )

        # Total au centre
        self.canvas.create_text(
            cx, cy, text=f"{total:,.0f}€",
            fill=ChartColors.TEXT, font=("Segoe UI", 14, "bold")
        )


class BarChart:
    """Graphique en barres pour comparaison mensuelle."""

    def __init__(self, canvas, x, y, width, height):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.padding = 50

    def draw(self, data: List[Tuple[str, float]], title: str = "",
             color: str = None, show_values: bool = True):
        """
        Dessine le graphique en barres.

        Args:
            data: Liste de tuples (label, valeur)
            title: Titre du graphique
            color: Couleur des barres
            show_values: Afficher les valeurs sur les barres
        """
        if not data:
            return

        color = color or ChartColors.PRIMARY

        # Zone de dessin
        chart_x = self.x + self.padding
        chart_y = self.y + 30
        chart_width = self.width - self.padding * 2
        chart_height = self.height - 70

        # Titre
        if title:
            self.canvas.create_text(
                self.x + self.width // 2, self.y + 15,
                text=title, fill=ChartColors.TEXT,
                font=("Segoe UI", 12, "bold")
            )

        # Max value
        values = [v for _, v in data]
        max_val = max(values) * 1.2 if values else 1

        # Largeur des barres
        bar_width = chart_width / len(data) * 0.7
        gap = chart_width / len(data) * 0.3

        # Dessiner les barres
        for i, (label, value) in enumerate(data):
            bar_height = (value / max_val) * chart_height
            bx = chart_x + i * (bar_width + gap) + gap / 2
            by = chart_y + chart_height - bar_height

            # Barre avec dégradé simulé
            self.canvas.create_rectangle(
                bx, by, bx + bar_width, chart_y + chart_height,
                fill=color, outline=""
            )

            # Valeur
            if show_values:
                self.canvas.create_text(
                    bx + bar_width / 2, by - 10,
                    text=f"{value:,.0f}€", fill=ChartColors.TEXT,
                    font=("Segoe UI", 8)
                )

            # Label
            self.canvas.create_text(
                bx + bar_width / 2, chart_y + chart_height + 15,
                text=label, fill=ChartColors.TEXT_MUTED,
                font=("Segoe UI", 8)
            )


class ProgressRing:
    """Anneau de progression circulaire."""

    def __init__(self, canvas, x, y, size):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size

    def draw(self, value: float, max_value: float = 100,
             title: str = "", color: str = None):
        """
        Dessine l'anneau de progression.

        Args:
            value: Valeur actuelle
            max_value: Valeur maximale
            title: Titre
            color: Couleur de la progression
        """
        percentage = min(value / max_value, 1) if max_value > 0 else 0
        color = color or (ChartColors.SUCCESS if percentage >= 1 else ChartColors.PRIMARY)

        cx = self.x + self.size // 2
        cy = self.y + self.size // 2
        radius = self.size // 2 - 10
        thickness = 12

        # Fond de l'anneau
        self.canvas.create_arc(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            start=90, extent=-360,
            style="arc", outline=ChartColors.GRID,
            width=thickness
        )

        # Progression
        extent = -360 * percentage
        self.canvas.create_arc(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            start=90, extent=extent,
            style="arc", outline=color,
            width=thickness
        )

        # Pourcentage au centre
        self.canvas.create_text(
            cx, cy - 5,
            text=f"{percentage * 100:.0f}%",
            fill=ChartColors.TEXT,
            font=("Segoe UI", 16, "bold")
        )

        # Titre
        if title:
            self.canvas.create_text(
                cx, cy + 20,
                text=title, fill=ChartColors.TEXT_MUTED,
                font=("Segoe UI", 9)
            )


class SparkLine:
    """Mini graphique en ligne (sparkline)."""

    def __init__(self, canvas, x, y, width, height):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, values: List[float], color: str = None):
        """
        Dessine une sparkline.

        Args:
            values: Liste de valeurs
            color: Couleur de la ligne
        """
        if len(values) < 2:
            return

        color = color or ChartColors.PRIMARY

        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val or 1

        points = []
        for i, v in enumerate(values):
            x = self.x + (i / (len(values) - 1)) * self.width
            y = self.y + self.height - ((v - min_val) / range_val) * self.height
            points.append((x, y))

        # Ligne
        for i in range(len(points) - 1):
            self.canvas.create_line(
                points[i][0], points[i][1],
                points[i+1][0], points[i+1][1],
                fill=color, width=2, smooth=True
            )

        # Point final
        last = points[-1]
        end_color = ChartColors.SUCCESS if values[-1] > values[0] else ChartColors.DANGER
        self.canvas.create_oval(
            last[0] - 3, last[1] - 3,
            last[0] + 3, last[1] + 3,
            fill=end_color, outline=""
        )


class ComparisonChart:
    """Graphique de comparaison de scénarios."""

    def __init__(self, canvas, x, y, width, height):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, scenarios: List[dict], title: str = ""):
        """
        Dessine la comparaison de scénarios.

        Args:
            scenarios: Liste de dictionnaires avec 'nom', 'data', 'color'
            title: Titre
        """
        if not scenarios:
            return

        padding = 50
        chart_x = self.x + padding
        chart_y = self.y + 40
        chart_width = self.width - padding * 2
        chart_height = self.height - 100

        # Titre
        if title:
            self.canvas.create_text(
                self.x + self.width // 2, self.y + 15,
                text=title, fill=ChartColors.TEXT,
                font=("Segoe UI", 12, "bold")
            )

        # Trouver les valeurs max
        all_values = []
        max_len = 0
        for s in scenarios:
            all_values.extend(s.get('data', []))
            max_len = max(max_len, len(s.get('data', [])))

        max_val = max(all_values) * 1.1 if all_values else 1

        # Dessiner chaque scénario
        for s_idx, scenario in enumerate(scenarios):
            data = scenario.get('data', [])
            color = scenario.get('color', ChartColors.PALETTE[s_idx])
            name = scenario.get('nom', f'Scénario {s_idx + 1}')

            if len(data) < 2:
                continue

            points = []
            for i, v in enumerate(data):
                x = chart_x + (i / (max_len - 1)) * chart_width
                y = chart_y + chart_height - (v / max_val * chart_height)
                points.append((x, y))

            # Ligne
            for i in range(len(points) - 1):
                self.canvas.create_line(
                    points[i][0], points[i][1],
                    points[i+1][0], points[i+1][1],
                    fill=color, width=2, smooth=True
                )

            # Légende
            legend_x = self.x + 60 + s_idx * 120
            legend_y = self.y + self.height - 20

            self.canvas.create_rectangle(
                legend_x, legend_y - 5,
                legend_x + 20, legend_y + 5,
                fill=color, outline=""
            )
            self.canvas.create_text(
                legend_x + 30, legend_y,
                text=name, fill=ChartColors.TEXT,
                font=("Segoe UI", 9), anchor="w"
            )
