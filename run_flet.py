"""
Lanceur pour ProjectFlow Pro - Interface Flet
"""

import flet as ft
from projectflow.gui_flet import main

if __name__ == "__main__":
    # Lancer l'application Flet
    # Mode desktop natif
    ft.app(target=main)

    # Alternative : Mode web (décommentez pour tester)
    # ft.app(target=main, view=ft.WEB_BROWSER, port=8080)
