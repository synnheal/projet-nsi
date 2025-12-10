# ProjectFlow

Application de gestion de projets personnels avec simulation budgétaire et planification hebdomadaire.

## Présentation

ProjectFlow est une application console modulaire permettant de :
- Créer et gérer plusieurs projets personnels
- Simuler l'atteinte d'objectifs financiers
- Organiser un planning hebdomadaire adapté
- Exporter des rapports HTML complets

## Architecture

L'application est structurée autour de 5 modules principaux :

| Module | Rôle |
|--------|------|
| `main` | Point d'entrée, navigation et logique centrale |
| `finance` | Traitement et simulation des données financières |
| `planning` | Génération et organisation du planning hebdomadaire |
| `storage` | Gestion de la persistance et restauration des projets |
| `export_html` | Génération d'un rapport HTML structuré |

## Documentation

📘 **[Documentation technique complète](docs/architecture.md)**

## Prérequis

- Python 3.x
- Aucune dépendance lourde

## Compatibilité

- Windows
- Linux
- macOS
