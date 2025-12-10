"""
Module export_html - Génération d'un rapport HTML structuré.

Ce module génère un rapport HTML complet contenant :
- Informations générales du projet
- Données financières
- Simulation détaillée (tableau des mois)
- Planning hebdomadaire
- Observations et avertissements
"""

import os
from datetime import datetime

# Jours de la semaine pour le planning
JOURS_SEMAINE = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]


def generer_css() -> str:
    """
    Génère le CSS pour le rapport HTML.

    Returns:
        Chaîne CSS
    """
    return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 2px solid #ecf0f1;
        }
        .info-box {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .info-box p {
            margin: 5px 0;
        }
        .info-box strong {
            color: #2c3e50;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background: #f9f9f9;
        }
        tr:hover {
            background: #f1f1f1;
        }
        .success {
            color: #27ae60;
            font-weight: bold;
        }
        .warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .message {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .planning-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin: 15px 0;
        }
        .jour-card {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
        }
        .jour-card h4 {
            color: #3498db;
            margin-bottom: 8px;
            text-transform: capitalize;
        }
        .jour-card.vide {
            background: #f9f9f9;
            color: #999;
        }
        .creneau {
            background: #e8f4f8;
            padding: 5px 8px;
            margin: 3px 0;
            border-radius: 3px;
            font-size: 0.9em;
        }
        .progression-bar {
            background: #ecf0f1;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progression-fill {
            background: linear-gradient(90deg, #3498db, #2ecc71);
            height: 100%;
            transition: width 0.3s ease;
        }
        footer {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    """


def generer_section_infos(projet: dict) -> str:
    """
    Génère la section des informations générales.

    Args:
        projet: Dictionnaire du projet

    Returns:
        HTML de la section
    """
    progression = projet.get("progression", 0) * 100

    return f"""
        <section>
            <h2>Informations générales</h2>
            <div class="info-box">
                <p><strong>Nom du projet :</strong> {projet.get('nom', 'Sans nom')}</p>
                <p><strong>Date de création :</strong> {projet.get('date_creation', 'N/A')}</p>
                <p><strong>Progression :</strong> {progression:.0f}%</p>
                <div class="progression-bar">
                    <div class="progression-fill" style="width: {progression}%;"></div>
                </div>
            </div>
        </section>
    """


def generer_section_finances(projet: dict) -> str:
    """
    Génère la section des données financières.

    Args:
        projet: Dictionnaire du projet

    Returns:
        HTML de la section
    """
    finances = projet.get("finances", {})

    return f"""
        <section>
            <h2>Données financières</h2>
            <table>
                <tr>
                    <th>Paramètre</th>
                    <th>Valeur</th>
                </tr>
                <tr>
                    <td>Revenus mensuels</td>
                    <td>{finances.get('revenus', 0):.2f} €</td>
                </tr>
                <tr>
                    <td>Dépenses fixes</td>
                    <td>{finances.get('depenses_fixes', 0):.2f} €</td>
                </tr>
                <tr>
                    <td>Dépenses variables</td>
                    <td>{finances.get('depenses_variables', 0):.2f} €</td>
                </tr>
                <tr>
                    <td>Objectif</td>
                    <td><strong>{finances.get('objectif', 0):.2f} €</strong></td>
                </tr>
                <tr>
                    <td>Durée de simulation</td>
                    <td>{finances.get('duree_mois', 12)} mois</td>
                </tr>
            </table>
        </section>
    """


def generer_section_simulation(projet: dict) -> str:
    """
    Génère la section de simulation détaillée.

    Args:
        projet: Dictionnaire du projet

    Returns:
        HTML de la section
    """
    simulation = projet.get("simulation")

    if not simulation:
        return """
            <section>
                <h2>Simulation</h2>
                <div class="warning">Aucune simulation n'a été effectuée.</div>
            </section>
        """

    if not simulation.get("possible"):
        return f"""
            <section>
                <h2>Simulation</h2>
                <div class="error">{simulation.get('message', 'Simulation impossible')}</div>
            </section>
        """

    # Générer le tableau mensuel
    lignes_tableau = ""
    for ligne in simulation.get("tableau_mensuel", []):
        statut = '<span class="success">✓ Atteint</span>' if ligne.get("objectif_atteint") else ""
        lignes_tableau += f"""
            <tr>
                <td>{ligne.get('mois', '')}</td>
                <td>{ligne.get('revenu', 0):.2f} €</td>
                <td>{ligne.get('depenses', 0):.2f} €</td>
                <td>{ligne.get('economie', 0):.2f} €</td>
                <td>{ligne.get('cumul', 0):.2f} €</td>
                <td>{statut}</td>
            </tr>
        """

    return f"""
        <section>
            <h2>Simulation détaillée</h2>
            <div class="info-box">
                <p><strong>Épargne mensuelle :</strong> {simulation.get('epargne_mensuelle', 0):.2f} €</p>
                <p><strong>Total épargné :</strong> {simulation.get('total_epargne', 0):.2f} €</p>
            </div>
            <div class="message">{simulation.get('message', '')}</div>
            <table>
                <tr>
                    <th>Mois</th>
                    <th>Revenu</th>
                    <th>Dépenses</th>
                    <th>Économie</th>
                    <th>Cumul</th>
                    <th>Statut</th>
                </tr>
                {lignes_tableau}
            </table>
        </section>
    """


def generer_section_planning(projet: dict) -> str:
    """
    Génère la section du planning hebdomadaire.

    Args:
        projet: Dictionnaire du projet

    Returns:
        HTML de la section
    """
    planning = projet.get("planning")

    if not planning:
        return """
            <section>
                <h2>Planning hebdomadaire</h2>
                <div class="warning">Aucun planning n'a été défini.</div>
            </section>
        """

    # Calculer le total d'heures
    total_heures = 0
    for creneaux in planning.values():
        for creneau in creneaux:
            total_heures += creneau.get("duree", 0)

    # Générer les cartes pour chaque jour
    cartes_jours = ""
    for jour in JOURS_SEMAINE:
        creneaux = planning.get(jour, [])
        if creneaux:
            creneaux_html = ""
            for creneau in creneaux:
                periode = formater_periode(creneau.get("periode", ""))
                creneaux_html += f"""
                    <div class="creneau">
                        {periode}: {creneau.get('duree', 0)}h<br>
                        <small>{creneau.get('debut', '')} - {creneau.get('fin', '')}</small>
                    </div>
                """
            cartes_jours += f"""
                <div class="jour-card">
                    <h4>{jour.capitalize()}</h4>
                    {creneaux_html}
                </div>
            """
        else:
            cartes_jours += f"""
                <div class="jour-card vide">
                    <h4>{jour.capitalize()}</h4>
                    <small>Libre</small>
                </div>
            """

    return f"""
        <section>
            <h2>Planning hebdomadaire</h2>
            <div class="info-box">
                <p><strong>Total hebdomadaire :</strong> {total_heures}h</p>
            </div>
            <div class="planning-grid">
                {cartes_jours}
            </div>
        </section>
    """


def formater_periode(periode: str) -> str:
    """
    Formate le nom d'une période pour l'affichage.

    Args:
        periode: Nom de la période

    Returns:
        Nom formaté
    """
    periodes = {
        "matin": "Matin",
        "apres_midi": "Après-midi",
        "soir": "Soir"
    }
    return periodes.get(periode, periode.capitalize())


def generer_rapport(projet: dict) -> str:
    """
    Génère le rapport HTML complet.

    Args:
        projet: Dictionnaire du projet

    Returns:
        Contenu HTML complet
    """
    date_generation = datetime.now().strftime("%d/%m/%Y à %H:%M")

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport - {projet.get('nom', 'Projet')}</title>
    <style>
        {generer_css()}
    </style>
</head>
<body>
    <div class="container">
        <h1>Rapport de projet : {projet.get('nom', 'Sans nom')}</h1>

        {generer_section_infos(projet)}
        {generer_section_finances(projet)}
        {generer_section_simulation(projet)}
        {generer_section_planning(projet)}

        <footer>
            <p>Rapport généré le {date_generation} par ProjectFlow</p>
        </footer>
    </div>
</body>
</html>"""


def exporter_rapport(projet: dict, chemin: str = None) -> str:
    """
    Exporte le rapport HTML dans un fichier.

    Args:
        projet: Dictionnaire du projet
        chemin: Chemin du fichier (optionnel)

    Returns:
        Chemin du fichier créé
    """
    if not chemin:
        nom_fichier = f"rapport_{projet.get('nom', 'projet').replace(' ', '_').lower()}.html"
        chemin = os.path.join(os.getcwd(), nom_fichier)

    contenu = generer_rapport(projet)

    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)

    return chemin
