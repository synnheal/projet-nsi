"""
ProjectFlow - Interface Graphique Moderne

Design ultra clean avec:
- Sidebar de navigation
- Cards modernes
- Thème sombre élégant
- Animations fluides
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import sys

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from projectflow import storage, finance, planning, export_html


class ModernTheme:
    """Thème moderne pour l'application."""

    # Couleurs principales
    BG_DARK = "#1a1a2e"
    BG_SIDEBAR = "#16213e"
    BG_CARD = "#1f2940"
    BG_INPUT = "#2d3a4f"

    ACCENT = "#4361ee"
    ACCENT_HOVER = "#3a56d4"
    SUCCESS = "#06d6a0"
    WARNING = "#ffd166"
    DANGER = "#ef476f"

    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0aec0"
    TEXT_MUTED = "#718096"

    # Fonts
    FONT_TITLE = ("Segoe UI", 24, "bold")
    FONT_SUBTITLE = ("Segoe UI", 16, "bold")
    FONT_BODY = ("Segoe UI", 11)
    FONT_SMALL = ("Segoe UI", 10)
    FONT_BUTTON = ("Segoe UI", 11, "bold")


class ModernButton(tk.Canvas):
    """Bouton moderne avec effet hover."""

    def __init__(self, parent, text, command=None, width=150, height=40,
                 bg=ModernTheme.ACCENT, fg=ModernTheme.TEXT_PRIMARY, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=parent.cget("bg"), highlightthickness=0, **kwargs)

        self.command = command
        self.bg_color = bg
        self.fg_color = fg
        self.width = width
        self.height = height
        self.text = text

        self.draw_button()

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def draw_button(self, color=None):
        """Dessine le bouton avec coins arrondis."""
        self.delete("all")
        color = color or self.bg_color

        # Rectangle arrondi
        radius = 8
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, radius, fill=color, outline="")

        # Texte
        self.create_text(self.width//2, self.height//2, text=self.text,
                        fill=self.fg_color, font=ModernTheme.FONT_BUTTON)

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Crée un rectangle avec coins arrondis."""
        points = [
            x1+radius, y1, x2-radius, y1,
            x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2,
            x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius,
            x1, y1+radius, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, event):
        """Effet au survol."""
        self.draw_button(ModernTheme.ACCENT_HOVER)

    def on_leave(self, event):
        """Retour à la normale."""
        self.draw_button(self.bg_color)

    def on_click(self, event):
        """Exécute la commande."""
        if self.command:
            self.command()


class ModernEntry(tk.Frame):
    """Champ de saisie moderne avec label."""

    def __init__(self, parent, label="", placeholder="", **kwargs):
        super().__init__(parent, bg=ModernTheme.BG_CARD)

        # Label
        if label:
            self.label = tk.Label(self, text=label, font=ModernTheme.FONT_SMALL,
                                 fg=ModernTheme.TEXT_SECONDARY, bg=ModernTheme.BG_CARD)
            self.label.pack(anchor="w", pady=(0, 5))

        # Container pour l'entrée
        self.entry_frame = tk.Frame(self, bg=ModernTheme.BG_INPUT, padx=12, pady=10)
        self.entry_frame.pack(fill="x")

        # Entry
        self.entry = tk.Entry(self.entry_frame, font=ModernTheme.FONT_BODY,
                             bg=ModernTheme.BG_INPUT, fg=ModernTheme.TEXT_PRIMARY,
                             insertbackground=ModernTheme.TEXT_PRIMARY,
                             relief="flat", border=0)
        self.entry.pack(fill="x")

        # Placeholder
        if placeholder:
            self.placeholder = placeholder
            self.entry.insert(0, placeholder)
            self.entry.config(fg=ModernTheme.TEXT_MUTED)
            self.entry.bind("<FocusIn>", self.on_focus_in)
            self.entry.bind("<FocusOut>", self.on_focus_out)

    def on_focus_in(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, "end")
            self.entry.config(fg=ModernTheme.TEXT_PRIMARY)

    def on_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=ModernTheme.TEXT_MUTED)

    def get(self):
        value = self.entry.get()
        if hasattr(self, 'placeholder') and value == self.placeholder:
            return ""
        return value

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
        self.entry.config(fg=ModernTheme.TEXT_PRIMARY)


class ProgressBar(tk.Canvas):
    """Barre de progression moderne."""

    def __init__(self, parent, width=200, height=8, value=0, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=ModernTheme.BG_CARD, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.value = value
        self.draw()

    def draw(self):
        self.delete("all")

        # Background
        self.create_rounded_rect(0, 0, self.width, self.height, 4,
                                fill=ModernTheme.BG_INPUT, outline="")

        # Progress
        if self.value > 0:
            progress_width = int(self.width * min(self.value, 1))
            if progress_width > 8:
                color = ModernTheme.SUCCESS if self.value >= 1 else ModernTheme.ACCENT
                self.create_rounded_rect(0, 0, progress_width, self.height, 4,
                                        fill=color, outline="")

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def set_value(self, value):
        self.value = value
        self.draw()


class ProjectCard(tk.Frame):
    """Carte de projet moderne."""

    def __init__(self, parent, projet, on_click=None, on_delete=None, **kwargs):
        super().__init__(parent, bg=ModernTheme.BG_CARD, padx=20, pady=15, **kwargs)

        self.projet = projet
        self.on_click = on_click
        self.on_delete = on_delete

        # Header
        header = tk.Frame(self, bg=ModernTheme.BG_CARD)
        header.pack(fill="x", pady=(0, 10))

        # Nom du projet
        nom = tk.Label(header, text=projet["nom"], font=ModernTheme.FONT_SUBTITLE,
                      fg=ModernTheme.TEXT_PRIMARY, bg=ModernTheme.BG_CARD)
        nom.pack(side="left")

        # Date
        date = tk.Label(header, text=projet.get("date_creation", ""),
                       font=ModernTheme.FONT_SMALL, fg=ModernTheme.TEXT_MUTED,
                       bg=ModernTheme.BG_CARD)
        date.pack(side="right")

        # Progression
        progression = projet.get("progression", 0)
        progress_frame = tk.Frame(self, bg=ModernTheme.BG_CARD)
        progress_frame.pack(fill="x", pady=5)

        progress_label = tk.Label(progress_frame, text=f"Progression: {progression*100:.0f}%",
                                 font=ModernTheme.FONT_SMALL, fg=ModernTheme.TEXT_SECONDARY,
                                 bg=ModernTheme.BG_CARD)
        progress_label.pack(anchor="w")

        self.progress_bar = ProgressBar(progress_frame, width=300, value=progression)
        self.progress_bar.pack(fill="x", pady=(5, 0))

        # Objectif
        finances = projet.get("finances", {})
        objectif = finances.get("objectif", 0)
        obj_label = tk.Label(self, text=f"Objectif: {objectif:,.0f} €",
                            font=ModernTheme.FONT_BODY, fg=ModernTheme.ACCENT,
                            bg=ModernTheme.BG_CARD)
        obj_label.pack(anchor="w", pady=(10, 0))

        # Boutons
        btn_frame = tk.Frame(self, bg=ModernTheme.BG_CARD)
        btn_frame.pack(fill="x", pady=(15, 0))

        open_btn = ModernButton(btn_frame, "Ouvrir", command=self._on_click,
                               width=100, height=35)
        open_btn.pack(side="left")

        del_btn = ModernButton(btn_frame, "Supprimer", command=self._on_delete,
                              width=100, height=35, bg=ModernTheme.DANGER)
        del_btn.pack(side="right")

        # Effet hover sur la carte
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        for child in self.winfo_children():
            child.bind("<Enter>", self.on_enter)

    def on_enter(self, event):
        self.config(bg=ModernTheme.BG_INPUT)
        for child in self.winfo_children():
            try:
                child.config(bg=ModernTheme.BG_INPUT)
                for subchild in child.winfo_children():
                    try:
                        subchild.config(bg=ModernTheme.BG_INPUT)
                    except:
                        pass
            except:
                pass

    def on_leave(self, event):
        self.config(bg=ModernTheme.BG_CARD)
        for child in self.winfo_children():
            try:
                child.config(bg=ModernTheme.BG_CARD)
                for subchild in child.winfo_children():
                    try:
                        subchild.config(bg=ModernTheme.BG_CARD)
                    except:
                        pass
            except:
                pass

    def _on_click(self):
        if self.on_click:
            self.on_click(self.projet)

    def _on_delete(self):
        if self.on_delete:
            self.on_delete(self.projet)


class ProjectFlowApp:
    """Application principale ProjectFlow."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ProjectFlow")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        self.root.configure(bg=ModernTheme.BG_DARK)

        # Centrer la fenêtre
        self.center_window()

        # Variables
        self.current_projet = None
        self.current_page = "home"

        # Interface
        self.setup_ui()
        self.show_home()

    def center_window(self):
        """Centre la fenêtre sur l'écran."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=ModernTheme.BG_SIDEBAR, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo/Titre
        logo_frame = tk.Frame(self.sidebar, bg=ModernTheme.BG_SIDEBAR)
        logo_frame.pack(fill="x", pady=30, padx=20)

        logo = tk.Label(logo_frame, text="ProjectFlow", font=ModernTheme.FONT_TITLE,
                       fg=ModernTheme.ACCENT, bg=ModernTheme.BG_SIDEBAR)
        logo.pack()

        subtitle = tk.Label(logo_frame, text="Gestion de projets", font=ModernTheme.FONT_SMALL,
                           fg=ModernTheme.TEXT_MUTED, bg=ModernTheme.BG_SIDEBAR)
        subtitle.pack()

        # Navigation
        nav_frame = tk.Frame(self.sidebar, bg=ModernTheme.BG_SIDEBAR)
        nav_frame.pack(fill="x", pady=20)

        self.nav_buttons = {}
        nav_items = [
            ("home", "🏠  Accueil"),
            ("new", "➕  Nouveau projet"),
        ]

        for key, text in nav_items:
            btn = tk.Label(nav_frame, text=text, font=ModernTheme.FONT_BODY,
                          fg=ModernTheme.TEXT_SECONDARY, bg=ModernTheme.BG_SIDEBAR,
                          cursor="hand2", padx=20, pady=12)
            btn.pack(fill="x")
            btn.bind("<Button-1>", lambda e, k=key: self.navigate(k))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=ModernTheme.BG_CARD))
            btn.bind("<Leave>", lambda e, b=btn: self.update_nav_style(b))
            self.nav_buttons[key] = btn

        # Version
        version = tk.Label(self.sidebar, text="v1.0.0", font=ModernTheme.FONT_SMALL,
                          fg=ModernTheme.TEXT_MUTED, bg=ModernTheme.BG_SIDEBAR)
        version.pack(side="bottom", pady=20)

        # Zone principale
        self.main_area = tk.Frame(self.root, bg=ModernTheme.BG_DARK)
        self.main_area.pack(side="right", fill="both", expand=True)

    def update_nav_style(self, btn):
        """Met à jour le style du bouton de navigation."""
        for key, b in self.nav_buttons.items():
            if b == btn:
                if key == self.current_page:
                    b.config(bg=ModernTheme.BG_CARD, fg=ModernTheme.ACCENT)
                else:
                    b.config(bg=ModernTheme.BG_SIDEBAR, fg=ModernTheme.TEXT_SECONDARY)

    def navigate(self, page):
        """Navigation entre les pages."""
        self.current_page = page

        # Mettre à jour les styles de navigation
        for key, btn in self.nav_buttons.items():
            if key == page:
                btn.config(bg=ModernTheme.BG_CARD, fg=ModernTheme.ACCENT)
            else:
                btn.config(bg=ModernTheme.BG_SIDEBAR, fg=ModernTheme.TEXT_SECONDARY)

        if page == "home":
            self.show_home()
        elif page == "new":
            self.show_new_project()

    def clear_main(self):
        """Efface la zone principale."""
        for widget in self.main_area.winfo_children():
            widget.destroy()

    def show_home(self):
        """Affiche la page d'accueil."""
        self.clear_main()
        self.current_page = "home"

        # Header
        header = tk.Frame(self.main_area, bg=ModernTheme.BG_DARK)
        header.pack(fill="x", padx=40, pady=30)

        title = tk.Label(header, text="Mes Projets", font=ModernTheme.FONT_TITLE,
                        fg=ModernTheme.TEXT_PRIMARY, bg=ModernTheme.BG_DARK)
        title.pack(side="left")

        # Bouton nouveau projet
        new_btn = ModernButton(header, "➕ Nouveau", command=lambda: self.navigate("new"),
                              width=130, height=40)
        new_btn.pack(side="right")

        # Liste des projets
        projects_frame = tk.Frame(self.main_area, bg=ModernTheme.BG_DARK)
        projects_frame.pack(fill="both", expand=True, padx=40)

        # Canvas avec scroll
        canvas = tk.Canvas(projects_frame, bg=ModernTheme.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(projects_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.BG_DARK)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Charger les projets
        projets = storage.lister_projets()

        if not projets:
            empty_label = tk.Label(scrollable_frame,
                                  text="Aucun projet\n\nCliquez sur '➕ Nouveau' pour créer votre premier projet",
                                  font=ModernTheme.FONT_BODY, fg=ModernTheme.TEXT_MUTED,
                                  bg=ModernTheme.BG_DARK, justify="center")
            empty_label.pack(pady=100)
        else:
            for projet in projets:
                card = ProjectCard(scrollable_frame, projet,
                                  on_click=self.open_project,
                                  on_delete=self.delete_project)
                card.pack(fill="x", pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Scroll avec molette
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def show_new_project(self):
        """Affiche le formulaire de nouveau projet."""
        self.clear_main()
        self.current_projet = None

        # Header
        header = tk.Frame(self.main_area, bg=ModernTheme.BG_DARK)
        header.pack(fill="x", padx=40, pady=30)

        title = tk.Label(header, text="Nouveau Projet", font=ModernTheme.FONT_TITLE,
                        fg=ModernTheme.TEXT_PRIMARY, bg=ModernTheme.BG_DARK)
        title.pack(side="left")

        # Formulaire dans un canvas scrollable
        form_container = tk.Frame(self.main_area, bg=ModernTheme.BG_DARK)
        form_container.pack(fill="both", expand=True, padx=40)

        canvas = tk.Canvas(form_container, bg=ModernTheme.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        form_frame = tk.Frame(canvas, bg=ModernTheme.BG_DARK)

        form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Card formulaire
        form_card = tk.Frame(form_frame, bg=ModernTheme.BG_CARD, padx=30, pady=25)
        form_card.pack(fill="x", pady=10)

        # Nom du projet
        section_title = tk.Label(form_card, text="Informations générales",
                                font=ModernTheme.FONT_SUBTITLE, fg=ModernTheme.ACCENT,
                                bg=ModernTheme.BG_CARD)
        section_title.pack(anchor="w", pady=(0, 15))

        self.entry_nom = ModernEntry(form_card, label="Nom du projet", placeholder="Mon projet")
        self.entry_nom.pack(fill="x", pady=5)

        # Section finances
        finance_card = tk.Frame(form_frame, bg=ModernTheme.BG_CARD, padx=30, pady=25)
        finance_card.pack(fill="x", pady=10)

        section_title = tk.Label(finance_card, text="Données financières",
                                font=ModernTheme.FONT_SUBTITLE, fg=ModernTheme.ACCENT,
                                bg=ModernTheme.BG_CARD)
        section_title.pack(anchor="w", pady=(0, 15))

        # Grid pour les champs financiers
        fields_frame = tk.Frame(finance_card, bg=ModernTheme.BG_CARD)
        fields_frame.pack(fill="x")

        self.entry_revenus = ModernEntry(fields_frame, label="Revenus mensuels (€)", placeholder="0")
        self.entry_revenus.pack(fill="x", pady=5)

        self.entry_fixes = ModernEntry(fields_frame, label="Dépenses fixes (€)", placeholder="0")
        self.entry_fixes.pack(fill="x", pady=5)

        self.entry_variables = ModernEntry(fields_frame, label="Dépenses variables (€)", placeholder="0")
        self.entry_variables.pack(fill="x", pady=5)

        self.entry_objectif = ModernEntry(fields_frame, label="Objectif (€)", placeholder="0")
        self.entry_objectif.pack(fill="x", pady=5)

        self.entry_duree = ModernEntry(fields_frame, label="Durée simulation (mois)", placeholder="12")
        self.entry_duree.pack(fill="x", pady=5)

        # Section planning
        planning_card = tk.Frame(form_frame, bg=ModernTheme.BG_CARD, padx=30, pady=25)
        planning_card.pack(fill="x", pady=10)

        section_title = tk.Label(planning_card, text="Planning hebdomadaire",
                                font=ModernTheme.FONT_SUBTITLE, fg=ModernTheme.ACCENT,
                                bg=ModernTheme.BG_CARD)
        section_title.pack(anchor="w", pady=(0, 15))

        # Jours disponibles
        jours_label = tk.Label(planning_card, text="Jours disponibles:",
                              font=ModernTheme.FONT_SMALL, fg=ModernTheme.TEXT_SECONDARY,
                              bg=ModernTheme.BG_CARD)
        jours_label.pack(anchor="w")

        jours_frame = tk.Frame(planning_card, bg=ModernTheme.BG_CARD)
        jours_frame.pack(fill="x", pady=10)

        self.jours_vars = {}
        jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

        for jour in jours:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(jours_frame, text=jour, variable=var,
                               font=ModernTheme.FONT_BODY, fg=ModernTheme.TEXT_PRIMARY,
                               bg=ModernTheme.BG_CARD, selectcolor=ModernTheme.BG_INPUT,
                               activebackground=ModernTheme.BG_CARD,
                               activeforeground=ModernTheme.TEXT_PRIMARY)
            cb.pack(side="left", padx=5)
            self.jours_vars[jour.lower()] = var

        self.entry_heures = ModernEntry(planning_card, label="Heures par semaine", placeholder="10")
        self.entry_heures.pack(fill="x", pady=10)

        # Boutons
        btn_frame = tk.Frame(form_frame, bg=ModernTheme.BG_DARK)
        btn_frame.pack(fill="x", pady=20)

        cancel_btn = ModernButton(btn_frame, "Annuler", command=lambda: self.navigate("home"),
                                 width=120, height=45, bg=ModernTheme.BG_CARD)
        cancel_btn.pack(side="left")

        save_btn = ModernButton(btn_frame, "Créer le projet", command=self.save_project,
                               width=160, height=45, bg=ModernTheme.SUCCESS)
        save_btn.pack(side="right")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Scroll avec molette
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def save_project(self):
        """Sauvegarde un nouveau projet."""
        nom = self.entry_nom.get()
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
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")
            return

        # Créer le projet
        projet = storage.creer_projet(nom)
        projet["finances"] = {
            "revenus": revenus,
            "depenses_fixes": fixes,
            "depenses_variables": variables,
            "objectif": objectif,
            "duree_mois": duree
        }

        # Planning
        jours_dispo = [jour for jour, var in self.jours_vars.items() if var.get()]
        if jours_dispo and heures > 0:
            projet["planning"] = planning.generer_planning(jours_dispo, heures)
        else:
            projet["planning"] = planning.creer_planning_vide()

        # Simulation
        projet["simulation"] = finance.analyser_finances(projet)
        projet["progression"] = finance.calculer_progression(
            projet["simulation"], objectif
        )

        # Sauvegarder
        if storage.ajouter_projet(projet):
            messagebox.showinfo("Succès", f"Projet '{nom}' créé avec succès!")
            self.navigate("home")
        else:
            messagebox.showerror("Erreur", "Erreur lors de la sauvegarde.")

    def open_project(self, projet):
        """Ouvre un projet pour le visualiser."""
        self.current_projet = projet
        self.show_project_details(projet)

    def show_project_details(self, projet):
        """Affiche les détails d'un projet."""
        self.clear_main()

        # Header
        header = tk.Frame(self.main_area, bg=ModernTheme.BG_DARK)
        header.pack(fill="x", padx=40, pady=30)

        back_btn = tk.Label(header, text="← Retour", font=ModernTheme.FONT_BODY,
                           fg=ModernTheme.TEXT_SECONDARY, bg=ModernTheme.BG_DARK,
                           cursor="hand2")
        back_btn.pack(side="left")
        back_btn.bind("<Button-1>", lambda e: self.navigate("home"))

        title = tk.Label(header, text=projet["nom"], font=ModernTheme.FONT_TITLE,
                        fg=ModernTheme.TEXT_PRIMARY, bg=ModernTheme.BG_DARK)
        title.pack(side="left", padx=20)

        # Bouton export
        export_btn = ModernButton(header, "📄 Exporter HTML", command=lambda: self.export_project(projet),
                                 width=150, height=40)
        export_btn.pack(side="right")

        # Contenu scrollable
        content = tk.Frame(self.main_area, bg=ModernTheme.BG_DARK)
        content.pack(fill="both", expand=True, padx=40)

        canvas = tk.Canvas(content, bg=ModernTheme.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=ModernTheme.BG_DARK)

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Card: Résumé
        summary_card = tk.Frame(scrollable, bg=ModernTheme.BG_CARD, padx=25, pady=20)
        summary_card.pack(fill="x", pady=10)

        tk.Label(summary_card, text="Résumé", font=ModernTheme.FONT_SUBTITLE,
                fg=ModernTheme.ACCENT, bg=ModernTheme.BG_CARD).pack(anchor="w", pady=(0, 15))

        finances = projet.get("finances", {})
        simulation = projet.get("simulation", {})

        # Grid infos
        info_frame = tk.Frame(summary_card, bg=ModernTheme.BG_CARD)
        info_frame.pack(fill="x")

        infos = [
            ("Revenus", f"{finances.get('revenus', 0):,.0f} €"),
            ("Dépenses fixes", f"{finances.get('depenses_fixes', 0):,.0f} €"),
            ("Dépenses variables", f"{finances.get('depenses_variables', 0):,.0f} €"),
            ("Objectif", f"{finances.get('objectif', 0):,.0f} €"),
            ("Épargne mensuelle", f"{simulation.get('epargne_mensuelle', 0):,.0f} €"),
        ]

        for i, (label, value) in enumerate(infos):
            row = tk.Frame(info_frame, bg=ModernTheme.BG_CARD)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=label, font=ModernTheme.FONT_BODY,
                    fg=ModernTheme.TEXT_SECONDARY, bg=ModernTheme.BG_CARD).pack(side="left")
            tk.Label(row, text=value, font=ModernTheme.FONT_BODY,
                    fg=ModernTheme.TEXT_PRIMARY, bg=ModernTheme.BG_CARD).pack(side="right")

        # Progression
        progression = projet.get("progression", 0)
        prog_frame = tk.Frame(summary_card, bg=ModernTheme.BG_CARD)
        prog_frame.pack(fill="x", pady=(15, 0))

        tk.Label(prog_frame, text=f"Progression: {progression*100:.0f}%",
                font=ModernTheme.FONT_BODY, fg=ModernTheme.SUCCESS if progression >= 1 else ModernTheme.ACCENT,
                bg=ModernTheme.BG_CARD).pack(anchor="w")

        ProgressBar(prog_frame, width=400, value=progression).pack(fill="x", pady=5)

        # Message
        if simulation.get("message"):
            msg_color = ModernTheme.SUCCESS if simulation.get("possible") else ModernTheme.DANGER
            tk.Label(summary_card, text=simulation["message"], font=ModernTheme.FONT_BODY,
                    fg=msg_color, bg=ModernTheme.BG_CARD, wraplength=500).pack(anchor="w", pady=(10, 0))

        # Card: Simulation
        if simulation.get("tableau_mensuel"):
            sim_card = tk.Frame(scrollable, bg=ModernTheme.BG_CARD, padx=25, pady=20)
            sim_card.pack(fill="x", pady=10)

            tk.Label(sim_card, text="Simulation mensuelle", font=ModernTheme.FONT_SUBTITLE,
                    fg=ModernTheme.ACCENT, bg=ModernTheme.BG_CARD).pack(anchor="w", pady=(0, 15))

            # Tableau
            columns = ("Mois", "Économie", "Cumul", "Statut")
            tree = ttk.Treeview(sim_card, columns=columns, show="headings", height=8)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            for ligne in simulation["tableau_mensuel"][:12]:  # Afficher 12 premiers mois
                statut = "✓ Atteint" if ligne.get("objectif_atteint") else ""
                tree.insert("", "end", values=(
                    f"Mois {ligne['mois']}",
                    f"{ligne['economie']:.0f} €",
                    f"{ligne['cumul']:.0f} €",
                    statut
                ))

            tree.pack(fill="x")

        # Card: Planning
        plan = projet.get("planning", {})
        if any(plan.values()):
            plan_card = tk.Frame(scrollable, bg=ModernTheme.BG_CARD, padx=25, pady=20)
            plan_card.pack(fill="x", pady=10)

            tk.Label(plan_card, text="Planning hebdomadaire", font=ModernTheme.FONT_SUBTITLE,
                    fg=ModernTheme.ACCENT, bg=ModernTheme.BG_CARD).pack(anchor="w", pady=(0, 15))

            jours_ordre = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

            for jour in jours_ordre:
                creneaux = plan.get(jour, [])
                if creneaux:
                    jour_frame = tk.Frame(plan_card, bg=ModernTheme.BG_CARD)
                    jour_frame.pack(fill="x", pady=5)

                    tk.Label(jour_frame, text=f"{jour.capitalize()}:",
                            font=ModernTheme.FONT_BODY, fg=ModernTheme.TEXT_PRIMARY,
                            bg=ModernTheme.BG_CARD, width=12, anchor="w").pack(side="left")

                    for creneau in creneaux:
                        periode = creneau.get("periode", "").replace("_", " ").capitalize()
                        duree = creneau.get("duree", 0)
                        tk.Label(jour_frame, text=f"{periode}: {duree}h",
                                font=ModernTheme.FONT_SMALL, fg=ModernTheme.TEXT_SECONDARY,
                                bg=ModernTheme.BG_INPUT, padx=8, pady=2).pack(side="left", padx=5)

            total = planning.calculer_total_heures(plan)
            tk.Label(plan_card, text=f"Total: {total}h / semaine",
                    font=ModernTheme.FONT_BODY, fg=ModernTheme.ACCENT,
                    bg=ModernTheme.BG_CARD).pack(anchor="w", pady=(15, 0))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def delete_project(self, projet):
        """Supprime un projet."""
        if messagebox.askyesno("Confirmation",
                              f"Supprimer le projet '{projet['nom']}' ?\nCette action est irréversible."):
            if storage.supprimer_projet(projet["id"]):
                messagebox.showinfo("Succès", "Projet supprimé.")
                self.show_home()
            else:
                messagebox.showerror("Erreur", "Erreur lors de la suppression.")

    def export_project(self, projet):
        """Exporte un projet en HTML."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")],
            initialfilename=f"rapport_{projet['nom'].replace(' ', '_')}.html"
        )

        if filename:
            try:
                export_html.exporter_rapport(projet, filename)
                messagebox.showinfo("Succès", f"Rapport exporté:\n{filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{e}")

    def run(self):
        """Lance l'application."""
        self.root.mainloop()


def main():
    """Point d'entrée."""
    app = ProjectFlowApp()
    app.run()


if __name__ == "__main__":
    main()
