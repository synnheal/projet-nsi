# Documentation Technique — ProjectFlow

> Version sans code, orientée architecture et fonctionnement interne

---

## Table des matières

1. [Architecture générale](#1-architecture-générale)
2. [Description des modules](#2-description-des-modules)
3. [Structures de données](#3-structures-de-données)
4. [Fonctionnement général (workflow)](#4-fonctionnement-général-workflow)
5. [Contraintes techniques et choix de conception](#5-contraintes-techniques-et-choix-de-conception)
6. [Évolutions possibles](#6-évolutions-possibles)

---

## 1. Architecture générale

ProjectFlow repose sur une **architecture modulaire** afin de garantir :

- La lisibilité du projet
- La facilité de maintenance
- La possibilité d'évolutions futures
- La séparation logique entre calculs, interface, stockage et export

### Modules principaux

L'application est structurée autour de **5 modules** :

```
┌─────────────────────────────────────────────────────────────┐
│                         main                                │
│              (coordination & interface)                     │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│   finance   │   planning  │   storage   │   export_html   │
│  (calculs)  │ (organisation)│ (persistance)│   (rendu)     │
└─────────────┴─────────────┴─────────────┴─────────────────┘
```

| Module | Description |
|--------|-------------|
| `main` | Point d'entrée, navigation et logique centrale |
| `finance` | Traitement et simulation des données financières |
| `planning` | Génération et organisation du planning hebdomadaire |
| `storage` | Gestion de la persistance et de la restauration des projets |
| `export_html` | Génération d'un rapport HTML structuré |

---

## 2. Description des modules

### 2.1 Module `main` (coordination globale)

Ce module constitue le cœur de l'application et orchestre l'ensemble des interactions.

#### Fonctionnalités

- Charge les projets existants via le module `storage`
- Gère le menu principal en console
- Orchestre les appels aux modules `finance`, `planning` et `export_html`
- Permet de créer, modifier ou supprimer des projets
- Met à jour l'état d'un projet avant sauvegarde automatique

#### Responsabilités principales

| Responsabilité | Description |
|----------------|-------------|
| Enchaînement des processus | Logique de navigation entre les étapes |
| Interface console | Affichage et saisie utilisateur |
| Gestion des projets | Sélection, chargement, duplication |
| Cohérence des données | Synchronisation entre modules |

---

### 2.2 Module `finance` (simulation budgétaire)

Ce module permet d'analyser et de simuler un objectif financier sur plusieurs mois.

#### Entrées typiques

- Revenus mensuels
- Dépenses fixes
- Dépenses variables
- Montant de l'objectif
- Durée de simulation en mois

#### Traitements effectués

1. **Calcul de l'épargne mensuelle**
   ```
   épargne = revenus - dépenses_fixes - dépenses_variables
   ```

2. **Génération d'un tableau mensuel** avec cumul d'épargne

3. **Détection du moment** où l'objectif est atteint

4. **Identification des cas impossibles** (épargne < 0)

#### Sorties du module

- Structure de données représentant chaque mois de la simulation
- Montant total épargné
- Estimation du nombre de mois nécessaires

---

### 2.3 Module `planning` (organisation du temps)

Ce module organise un planning hebdomadaire à partir des disponibilités de l'utilisateur.

#### Entrées

- Jours disponibles
- Heures disponibles par jour
- Total d'heures à consacrer à l'objectif par semaine

#### Traitements

- Répartition équitable ou pondérée des heures
- Construction de créneaux structurés (matin / après-midi / soir ou plages horaires simples)
- Génération d'une structure de type "calendrier hebdomadaire"

#### Sorties

- Dictionnaire représentant le planning complet
- Liste de créneaux par jour

#### Exemple de structure de sortie

```
Semaine
├── Lundi
│   ├── Matin: 2h
│   └── Soir: 1h
├── Mercredi
│   └── Après-midi: 3h
└── Samedi
    └── Matin: 4h
```

---

### 2.4 Module `storage` (sauvegarde & chargement)

Module essentiel pour la **gestion multi-projets**.

#### Rôle

- Enregistrer automatiquement les projets dans un fichier JSON
- Charger les projets lors du démarrage de l'application
- Permettre la gestion complète des projets

#### Opérations supportées

| Opération | Description |
|-----------|-------------|
| Ajout | Création d'un nouveau projet |
| Suppression | Retrait définitif d'un projet |
| Duplication | Copie d'un projet existant |
| Renommage | Modification du nom d'un projet |

#### Données stockées

Pour chaque projet :

- Nom du projet
- Date de création
- Paramètres financiers
- Résultats de simulation
- Planning généré
- État général du projet (progression)

> Ce module assure la **continuité entre les sessions** de l'utilisateur.

---

### 2.5 Module `export_html` (génération du rapport)

Construit un **rapport HTML complet** et portable.

#### Sections du rapport

1. **Informations générales** du projet
2. **Données financières**
3. **Simulation détaillée** (tableau des mois)
4. **Planning hebdomadaire**
5. **Observations ou messages d'avertissement** (ex : "objectif impossible")

#### Structure technique

| Composant | Description |
|-----------|-------------|
| Modèle HTML | Template de base pour le rapport |
| Insertion dynamique | Injection des données du projet |
| Style CSS | Mise en forme intégrée dans le fichier |

#### Fonctionnalités optionnelles

- Graphique (via image PNG si module avancé activé)
- Tableaux stylisés

#### Objectif

Produire un document **lisible, propre et portable**, compatible avec tous les navigateurs.

---

## 3. Structures de données

### 3.1 Objet "Projet"

Un projet contient les informations suivantes :

```
Projet
├── Identifiant
│   ├── id (interne)
│   ├── nom
│   └── date_creation
├── Informations budgétaires
│   ├── revenus
│   ├── depenses_fixes
│   ├── depenses_variables
│   └── objectif
├── Résultats de simulation
│   ├── tableau_mensuel[]
│   ├── total_epargne
│   └── mois_objectif_atteint
├── Planning hebdomadaire
│   └── jours{}
└── Métadonnées
    ├── version
    └── progression
```

> Représenté sous forme d'un dictionnaire exportable en **JSON**.

---

### 3.2 Données financières

Structure tabulaire contenant :

| Champ | Type | Description |
|-------|------|-------------|
| `mois` | entier | Index du mois (1, 2, 3...) |
| `revenu` | décimal | Revenus du mois |
| `depenses` | décimal | Total des dépenses |
| `economie` | décimal | Épargne du mois |
| `cumul` | décimal | Cumul d'épargne depuis le début |
| `objectif_atteint` | booléen | Indicateur d'atteinte de l'objectif |

---

### 3.3 Planning hebdomadaire

Structure arborescente :

```
planning
└── semaine
    ├── lundi
    │   └── creneaux[]
    ├── mardi
    │   └── creneaux[]
    ├── mercredi
    │   └── creneaux[]
    ├── jeudi
    │   └── creneaux[]
    ├── vendredi
    │   └── creneaux[]
    ├── samedi
    │   └── creneaux[]
    └── dimanche
        └── creneaux[]
```

Chaque créneau contient :
- Période (matin / après-midi / soir)
- Durée en heures

> Permet un rendu facile dans un tableau HTML.

---

## 4. Fonctionnement général (workflow)

```
┌─────────────────────────────────────────────────────────────┐
│                    1. DÉMARRAGE                             │
│         Chargement des projets existants (storage)          │
│              Affichage du menu principal                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              2. CRÉATION / SÉLECTION                        │
│           Saisie des données financières                    │
│         Saisie des disponibilités hebdomadaires             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    3. SIMULATION                            │
│      Module finance → résultats budgétaires                 │
│      Module planning → organisation hebdomadaire            │
│      Fusion dans la structure du projet                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   4. SAUVEGARDE                             │
│       Enregistrement automatique (fichier JSON)             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                     5. EXPORT                               │
│      À la demande : génération du rapport HTML              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│               6. FERMETURE / REPRISE                        │
│    Reprise exacte de la session précédente possible         │
└─────────────────────────────────────────────────────────────┘
```

### Détail des étapes

1. **Démarrage de l'application**
   - Chargement des projets existants
   - Affichage du menu principal

2. **Création ou sélection d'un projet**
   - Saisie des données financières
   - Saisie des disponibilités hebdomadaires

3. **Simulation**
   - Le module `finance` produit les résultats
   - Le module `planning` génère l'organisation
   - Les deux sont fusionnés dans la structure du projet

4. **Sauvegarde**
   - Enregistrement automatique dans le fichier JSON

5. **Export**
   - À la demande, génération d'un rapport HTML complet

6. **Fermeture / reprise**
   - Possibilité de reprendre exactement où l'utilisateur s'était arrêté

---

## 5. Contraintes techniques et choix de conception

### Principes directeurs

| Principe | Mise en œuvre |
|----------|---------------|
| **Portabilité maximale** | Fonctionne sous Windows, Linux, macOS |
| **Installation légère** | Python + dépendances minimales |
| **Simplicité utilisateur** | Navigation console intuitive |
| **Modularité** | Maintenance facilitée |

### Séparation logique stricte

```
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Calculs    │   │  Interface   │   │   Stockage   │   │  Rendu HTML  │
│   (finance   │   │   (main)     │   │  (storage)   │   │(export_html) │
│   planning)  │   │              │   │              │   │              │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

Cette séparation garantit :
- L'indépendance des modules
- La testabilité de chaque composant
- La possibilité de remplacer un module sans impacter les autres

---

## 6. Évolutions possibles

### Améliorations fonctionnelles

| Évolution | Description |
|-----------|-------------|
| Revenus variables | Gestion de revenus différents chaque mois |
| Multi-objectifs | Plusieurs objectifs dans un même projet |
| Export PDF | Génération de rapports au format PDF |
| Graphiques avancés | Visualisations supplémentaires |

### Améliorations techniques

| Évolution | Description |
|-----------|-------------|
| Interface avancée | Console enrichie (couleurs, menus interactifs) |
| Interface web locale | Application web légère |
| Base de données | Migration de JSON vers SQLite |
| API REST | Exposition des fonctionnalités via API |

---

## Annexes

### Schéma récapitulatif des dépendances

```
                    ┌─────────┐
                    │  main   │
                    └────┬────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌───────────┐
    │ finance │    │planning │    │export_html│
    └─────────┘    └─────────┘    └───────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
                   ┌─────────┐
                   │ storage │
                   └─────────┘
```

### Format du fichier de sauvegarde (JSON)

```json
{
  "projets": [
    {
      "id": "uuid",
      "nom": "Mon projet",
      "date_creation": "2025-01-15",
      "finances": {
        "revenus": 2500,
        "depenses_fixes": 1200,
        "depenses_variables": 500,
        "objectif": 5000
      },
      "simulation": {
        "tableau_mensuel": [...],
        "total_epargne": 4800,
        "mois_objectif_atteint": 7
      },
      "planning": {
        "lundi": [...],
        "mercredi": [...]
      },
      "progression": 0.65
    }
  ],
  "version": "1.0",
  "derniere_modification": "2025-01-20T14:30:00"
}
```

---

*Documentation générée pour le projet NSI — ProjectFlow*
