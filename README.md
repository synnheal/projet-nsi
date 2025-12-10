# ProjectFlow

Application de gestion de projets personnels avec simulation budgétaire et planification hebdomadaire.

## Présentation

ProjectFlow est une application permettant de :
- Créer et gérer plusieurs projets personnels
- Simuler l'atteinte d'objectifs financiers
- Organiser un planning hebdomadaire adapté
- Exporter des rapports HTML complets

**Deux interfaces disponibles :**
- Interface graphique moderne (recommandée)
- Interface console

## Lancement

### Interface graphique (recommandée)

```bash
python run_gui.py
```

### Interface console

```bash
python run.py
```

## Captures d'écran

L'interface graphique propose :
- Design sombre moderne et élégant
- Navigation par sidebar
- Cartes de projets avec barres de progression
- Formulaires intuitifs
- Export HTML en un clic

## Architecture

L'application est structurée autour de 6 modules principaux :

| Module | Rôle |
|--------|------|
| `main` | Interface console et logique centrale |
| `gui` | Interface graphique moderne (tkinter) |
| `finance` | Traitement et simulation des données financières |
| `planning` | Génération et organisation du planning hebdomadaire |
| `storage` | Gestion de la persistance et restauration des projets |
| `export_html` | Génération d'un rapport HTML structuré |

## Documentation

📘 **[Documentation technique complète](docs/architecture.md)**

## Prérequis

- Python 3.x
- tkinter (inclus par défaut sur Windows)

## Compatibilité

- Windows
- Linux
- macOS
