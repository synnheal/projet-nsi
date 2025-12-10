# ProjectFlow Pro

Application de gestion de projets personnels avec simulation budgétaire, planification et gamification.

## Fonctionnalités

### Core
- Créer et gérer plusieurs projets personnels
- Simuler l'atteinte d'objectifs financiers
- Organiser un planning hebdomadaire
- Exporter des rapports HTML

### Pro (Nouveau!)
- **Dashboard interactif** avec graphiques
- **8 thèmes** personnalisables (sombre, clair, océan, forêt...)
- **Timer Pomodoro** intégré avec statistiques
- **20+ badges** et système de gamification
- **Streaks** et défis hebdomadaires
- **Scénarios What-if** pour comparer des stratégies
- **Recommandations personnalisées**
- **Multi-objectifs** avec répartition automatique
- **Catégories de dépenses** détaillées

## Lancement

### Interface Pro (recommandée)

```bash
python run_pro.py
```

### Interface standard

```bash
python run_gui.py
```

### Interface console

```bash
python run.py
```

## Captures d'écran

L'interface Pro propose :
- Dashboard avec KPIs et graphiques interactifs
- Courbes d'évolution de l'épargne
- Camemberts de répartition des dépenses
- Système de niveau et badges
- Timer Pomodoro visuel
- Comparateur de scénarios

## Architecture

| Module | Description |
|--------|-------------|
| `main` | Interface console |
| `gui` | Interface graphique standard |
| `gui_advanced` | Interface Pro avec toutes les features |
| `finance` | Simulation budgétaire de base |
| `finance_advanced` | Multi-objectifs, catégories, scénarios |
| `planning` | Planning hebdomadaire |
| `storage` | Persistance JSON |
| `export_html` | Rapports HTML |
| `charts` | Graphiques (ligne, camembert, barres) |
| `achievements` | Badges et gamification |
| `themes` | Système de thèmes |
| `timer` | Pomodoro et suivi du temps |

## Thèmes disponibles

| Thème | Description |
|-------|-------------|
| Dark | Sombre élégant (défaut) |
| Light | Clair et lumineux |
| Midnight | Noir profond |
| Ocean | Bleu océan |
| Sunset | Violet/rose |
| Forest | Vert forêt |
| Nord | Style nordique |
| Rose | Rose pastel |

## Badges

20+ badges à débloquer :
- 🎯 Premiers Pas
- 🏆 Objectif Atteint
- 💰 Petit Épargnant → 💎 Maître Épargnant
- 🔥 Streaks (7, 30, 100 jours)
- 🧠 Sage Financier (20% épargne)
- Et bien plus...

## Documentation

📘 **[Documentation technique](docs/architecture.md)**

## Prérequis

- Python 3.x
- tkinter (inclus par défaut sur Windows)

## Compatibilité

- Windows
- Linux
- macOS
