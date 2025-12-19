# Documentation Technique — StockFlow Pro

> Architecture et fonctionnement interne du système intelligent de gestion de stock

---

## Table des matières

1. [Architecture générale](#1-architecture-générale)
2. [Description des modules](#2-description-des-modules)
3. [Structures de données](#3-structures-de-données)
4. [Algorithmes clés](#4-algorithmes-clés)
5. [Fonctionnement général (workflow)](#5-fonctionnement-général-workflow)
6. [Contraintes techniques et choix de conception](#6-contraintes-techniques-et-choix-de-conception)
7. [Évolutions possibles](#7-évolutions-possibles)

---

## 1. Architecture générale

StockFlow Pro repose sur une **architecture modulaire MVC** (Modèle-Vue-Contrôleur) afin de garantir :

- La lisibilité et maintenabilité du projet
- La séparation des responsabilités
- La testabilité des composants
- L'évolutivité et l'extensibilité
- La réutilisabilité du code métier

### Modules principaux

L'application est structurée autour de **6 modules métier + 1 interface graphique** :

```
┌─────────────────────────────────────────────────────────────────┐
│                      stockflow_gui.py                           │
│                 (Interface Graphique - VUE)                     │
├────────┬──────────┬──────────┬───────────┬──────────┬──────────┤
│ stock  │predictions│analytics │restocking │timeline  │scenarios │
│(modèle)│   (IA)   │  (KPI)   │  (réappro)│(journal) │(simul.)  │
└────────┴──────────┴──────────┴───────────┴──────────┴──────────┘
```

| Module | Lignes | Description |
|--------|--------|-------------|
| **stock.py** | 412 | Gestion inventaire, articles, mouvements (MODÈLE) |
| **predictions.py** | 367 | Seuils automatiques, prévisions, anomalies (IA) |
| **analytics.py** | 518 | KPI financiers, analyse ABC, rotation |
| **restocking.py** | 423 | Recommandations intelligentes, EOQ |
| **timeline.py** | 354 | Journal chronologique, export CSV |
| **scenarios.py** | 401 | Simulations What-If avec scoring |
| **stockflow_gui.py** | 1047 | Interface graphique moderne (VUE + CONTRÔLEUR) |

**Total : ~3500 lignes de code métier**

---

## 2. Description des modules

### 2.1 Module `stock.py` (Modèle de données)

Ce module constitue le **cœur du système** et gère l'inventaire complet.

#### Classes principales

**`Article`** (Dataclass)
```python
@dataclass
class Article:
    id: str                         # UUID unique
    nom: str                        # Nom commercial
    reference: str                  # Référence produit
    categorie: str                  # Catégorie (électronique, alimentaire...)
    quantite: int                   # Stock actuel
    seuil_min: Optional[int]        # Seuil manuel
    seuil_min_auto: Optional[int]   # Seuil calculé automatiquement
    stock_optimal: int              # Stock optimal cible
    prix_achat: float               # Prix d'achat unitaire
    prix_vente: float               # Prix de vente unitaire
    fournisseur: str                # Nom du fournisseur
    delai_reappro_jours: int        # Délai de livraison
    ventes_jour: float              # Ventes moyennes/jour (calculé)
    rotation_stock: float           # Rotation annuelle (calculé)
```

**`Mouvement`** (Dataclass)
```python
@dataclass
class Mouvement:
    id: str                    # UUID unique
    article_id: str            # Référence article
    type: str                  # "entree" ou "sortie"
    quantite: int              # Quantité déplacée
    date: str                  # ISO 8601 (YYYY-MM-DD HH:MM:SS)
    prix_unitaire: float       # Prix à ce moment
    motif: str                 # Raison du mouvement
```

**`Inventaire`** (Classe principale)
- Gère la collection d'articles (dictionnaire indexé par UUID)
- Gère l'historique des mouvements (liste chronologique)
- Opérations CRUD (Create, Read, Update, Delete)
- Persistance JSON automatique

#### Responsabilités

| Responsabilité | Description |
|----------------|-------------|
| Gestion articles | Ajout, modification, suppression, recherche |
| Gestion mouvements | Entrées, sorties, historique |
| Validation données | Vérification cohérence (stock négatif, prix, etc.) |
| Persistance | Sauvegarde/chargement JSON |
| Calcul propriétés | Valeur stock, marge, statut |

#### Méthodes clés

```python
# CRUD Articles
ajouter_article(article: Article) -> bool
modifier_article(article_id: str, **kwargs) -> bool
supprimer_article(article_id: str) -> bool
obtenir_article(article_id: str) -> Optional[Article]
lister_articles() -> List[Article]

# Gestion Mouvements
ajouter_mouvement(mouvement: Mouvement) -> bool
obtenir_mouvements(article_id: str) -> List[Mouvement]
obtenir_tous_mouvements() -> List[Mouvement]

# Persistance
sauvegarder(fichier: str) -> bool
charger(fichier: str) -> bool
```

---

### 2.2 Module `predictions.py` (Intelligence Artificielle)

Ce module implémente les **algorithmes prédictifs** et de détection.

#### Fonctionnalités

##### 1. Calcul Seuils Automatiques

**Formule mathématique :**
```
Seuil_min = (Ventes_moyennes_jour × Délai_réappro) × Marge_sécurité
```

**Paramètres :**
- Historique des ventes sur 30 jours
- Délai fournisseur (en jours)
- Marge de sécurité (par défaut 1.5)

**Algorithme :**
1. Calculer ventes moyennes/jour sur fenêtre glissante 30j
2. Multiplier par délai de réapprovisionnement
3. Appliquer marge de sécurité (150%)
4. Borner entre 1 et stock_optimal

##### 2. Prévisions de Ventes

**Méthode : Moyenne Mobile + Régression Linéaire**

**Étapes :**
1. Calcul moyenne mobile sur 30 jours
2. Détection tendance (coefficient directeur)
3. Projection sur 30 jours futurs
4. Génération liste de prévisions avec dates

**Complexité :** O(n) où n = nombre de mouvements

##### 3. Détection d'Anomalies

**6 types d'anomalies détectées :**

| Type | Condition | Sévérité |
|------|-----------|----------|
| **STOCK_NEGATIF** | quantité < 0 | CRITIQUE 🔴 |
| **RUPTURE** | quantité = 0 | ÉLEVÉE 🟠 |
| **STOCK_CRITIQUE** | quantité < seuil_min | MOYENNE 🟡 |
| **SURSTOCK** | quantité > 2× optimal | FAIBLE 🔵 |
| **STOCK_DORMANT** | 0 vente en 90j | MOYENNE 🟡 |
| **VARIATION_ANORMALE** | ±200% de la moyenne | MOYENNE 🟡 |

**Structure Anomalie :**
```python
@dataclass
class Anomalie:
    type: TypeAnomalie
    severite: Severite
    article_id: str
    message: str
    date_detection: str
    valeur_actuelle: float
    valeur_attendue: Optional[float]
```

#### Méthodes principales

```python
# Seuils automatiques
calculer_seuil_automatique(article_id: str, marge: float = 1.5) -> int
calculer_ventes_moyennes_jour(article_id: str, jours: int = 30) -> float
appliquer_seuils_automatiques() -> int

# Prévisions
prevoir_ventes(article_id: str, jours_futur: int = 30) -> List[Prevision]

# Anomalies
detecter_anomalies() -> List[Anomalie]
analyser_variation_stock(article_id: str) -> Optional[Anomalie]
```

---

### 2.3 Module `analytics.py` (Analyses et KPI)

Module dédié aux **calculs financiers** et **analyses statistiques**.

#### KPI Calculés

##### 1. KPI Globaux

| KPI | Formule | Signification |
|-----|---------|---------------|
| **Valeur stock total** | Σ(quantité × prix_achat) | Immobilisation capital |
| **Taux marge moyen** | Σ(marges) / nb_articles | Rentabilité moyenne |
| **Rotation moyenne** | Σ(rotations) / nb_articles | Renouvellement stock |
| **Taux service** | (1 - jours_rupture/jours_total) × 100 | Disponibilité produits |
| **Nombre ruptures** | Count(quantité = 0) | Risque commercial |

##### 2. KPI par Article

```python
@dataclass
class KPIArticle:
    article_id: str
    valeur_stock: float          # quantité × prix_achat
    marge_unitaire: float        # prix_vente - prix_achat
    taux_marge: float            # (marge / prix_achat) × 100
    rotation_annuelle: float     # ventes_an / stock_moyen
    ventes_30j: int              # total ventes dernier mois
    ca_30j: float                # chiffre d'affaires 30j
```

##### 3. Analyse ABC (Pareto)

**Principe :** Classification 80/20

```
A : 20% des articles = 80% de la valeur    → Surveillance quotidienne
B : 30% des articles = 15% de la valeur    → Surveillance hebdo
C : 50% des articles = 5% de la valeur     → Surveillance mensuelle
```

**Algorithme :**
1. Trier articles par valeur stock décroissante
2. Calculer valeur totale
3. Parcourir et cumuler jusqu'à seuils (80%, 95%, 100%)
4. Classer dans catégories A, B, C

**Complexité :** O(n log n) (tri)

##### 4. Top Produits

- Top 5 ventes (quantité)
- Top 5 chiffre d'affaires
- Top 5 marge
- Top 5 rotation

#### Méthodes principales

```python
# KPI globaux
generer_rapport_financier() -> RapportFinancier
calculer_valeur_stock_totale() -> float
calculer_taux_marge_moyen() -> float

# KPI par article
calculer_kpi_article(article_id: str) -> KPIArticle
calculer_rotation_stock(article_id: str) -> float
calculer_ca_periode(article_id: str, jours: int = 30) -> float

# Analyses
calculer_abc_analysis() -> Dict[str, List[Dict]]
obtenir_top_ventes(limite: int = 5) -> List[Dict]
obtenir_top_ca(limite: int = 5) -> List[Dict]
```

---

### 2.4 Module `restocking.py` (Réapprovisionnement)

Module d'**optimisation des commandes fournisseurs**.

#### Fonctionnalités

##### 1. Recommandations Intelligentes

**Priorisation par urgence :**

```python
class Urgence(Enum):
    CRITIQUE = 1    # Rupture de stock imminente
    ELEVEE = 2      # En dessous du seuil critique
    MOYENNE = 3     # Approche du seuil minimum
    FAIBLE = 4      # Réapprovisionnement préventif
```

**Critères de déclenchement :**
- CRITIQUE : quantité ≤ 0
- ÉLEVÉE : quantité < seuil_min × 0.5
- MOYENNE : quantité < seuil_min
- FAIBLE : quantité < seuil_min × 1.5 (préventif)

##### 2. Calcul Quantité Optimale

**Deux méthodes disponibles :**

**Méthode 1 : Stock Optimal**
```
Quantité = stock_optimal - quantité_actuelle
```

**Méthode 2 : EOQ (Economic Order Quantity / Formule de Wilson)**

```
        _______________
       ╱ 2 × D × S
EOQ = ╱  ─────────
    ╲╱      H

D = Demande annuelle (ventes/j × 365)
S = Coût de passation commande (fixe, ex: 50€)
H = Coût de stockage unitaire annuel (20% prix_achat)
```

**Avantages EOQ :**
- Minimise coûts totaux (stockage + commandes)
- Optimise la trésorerie
- Réduit le nombre de commandes

##### 3. Génération Bons de Commande

Structure complète avec :
- Liste des articles à commander
- Quantités optimales
- Montant total par fournisseur
- Priorisation par urgence
- Format exportable (CSV, texte)

#### Structures de données

```python
@dataclass
class RecommandationReappro:
    article_id: str
    nom_article: str
    quantite_actuelle: int
    seuil_min: int
    quantite_recommandee: int
    urgence: Urgence
    fournisseur: str
    delai_jours: int
    cout_estime: float
    date_commande_suggeree: str

@dataclass
class BonCommande:
    id: str
    date_creation: str
    fournisseur: str
    articles: List[LigneCommande]
    montant_total: float
    statut: str  # "brouillon", "envoyé", "reçu"
```

#### Méthodes principales

```python
# Recommandations
generer_recommandations(inclure_preventif: bool = True) -> List[RecommandationReappro]
filtrer_par_urgence(urgence_min: Urgence) -> List[RecommandationReappro]

# Calculs
calculer_quantite_optimale(article_id: str, methode: str = "stock_optimal") -> int
calculer_eoq(article_id: str, cout_commande: float = 50.0) -> int

# Bons de commande
generer_bon_commande(fournisseur: str) -> BonCommande
exporter_csv(fichier: str, fournisseur: Optional[str] = None)
```

---

### 2.5 Module `timeline.py` (Journal Chronologique)

Gestion de l'**historique complet** des mouvements de stock.

#### Fonctionnalités

##### 1. Timeline Unifiée

Transforme les mouvements bruts en entrées de journal enrichies :

```python
@dataclass
class EntreeTimeline:
    date: str                # Date complète ISO 8601
    type: str                # "entree" ou "sortie"
    article_nom: str         # Nom lisible
    article_ref: str         # Référence produit
    quantite: int            # Quantité déplacée
    prix_unitaire: float     # Prix à ce moment
    valeur_totale: float     # quantité × prix
    stock_apres: int         # Stock résultant
    motif: str               # Raison du mouvement
    icone: str               # 📥 ou 📤 (visuel)
```

##### 2. Filtrage et Recherche

**Filtres disponibles :**
- Par période (date_debut, date_fin)
- Par type (entrée/sortie)
- Par article (article_id)
- Par motif (vente, achat, retour, inventaire, etc.)
- Limite et pagination

##### 3. Export et Reporting

**Formats supportés :**
- CSV (Excel/LibreOffice)
- JSON (analyse programmatique)
- Texte formaté (console)

**Statistiques générées :**
- Total entrées/sorties par période
- Valeur totale des mouvements
- Articles les plus actifs
- Analyse par motif

#### Méthodes principales

```python
# Timeline
obtenir_timeline(
    limite: int = None,
    date_debut: str = None,
    date_fin: str = None,
    type_filtre: str = None,
    article_id: str = None
) -> List[EntreeTimeline]

# Export
exporter_csv(fichier: str, jours: int = None)
exporter_json(fichier: str)

# Statistiques
obtenir_stats_periode(date_debut: str, date_fin: str) -> Dict
```

---

### 2.6 Module `scenarios.py` (Simulations What-If)

Module de **prospective et aide à la décision**.

#### Fonctionnalités

##### 1. Scénarios Configurables

```python
@dataclass
class Scenario:
    nom: str
    description: str
    parametres: Dict[str, Any]
    # Exemples de paramètres :
    # - croissance_ventes: +20%
    # - nouveau_fournisseur: délai 5j au lieu de 7j
    # - remise_prix_achat: -10%
    # - augmentation_prix_vente: +15%
    # - nouveau_seuil_min: 50 au lieu de 32
```

##### 2. Simulation sur 90 Jours

**Étapes de simulation :**
1. Duplication état actuel inventaire
2. Application des paramètres du scénario
3. Simulation jour par jour (90 itérations)
   - Génération ventes journalières (avec croissance)
   - Déclenchement réappros automatiques
   - Calcul coûts stockage
   - Détection ruptures
4. Agrégation des métriques
5. Calcul du score global

##### 3. Scoring Automatique (0-100)

**Formule pondérée :**

```python
Score = (Score_marge × 0.4) + (Score_ruptures × 0.4) + (Score_efficacité × 0.2)

Score_marge = min(40, (taux_marge / 50) × 40)
Score_ruptures = max(0, 40 - (jours_rupture / 10))
Score_efficacité = max(0, 20 - (nb_reappros / 5))
```

**Interprétation :**
- 90-100 : Excellent ✅
- 75-89 : Très bon ✅
- 60-74 : Bon 🟢
- 40-59 : Moyen 🟡
- 0-39 : Faible 🔴

##### 4. Comparaison Scénarios

Permet de comparer côte à côte :
- Scénario actuel (baseline)
- Scénario optimiste
- Scénario pessimiste
- Scénarios personnalisés

#### Structures de résultats

```python
@dataclass
class ResultatSimulation:
    scenario: Scenario
    score: float                      # 0-100
    metriques: Dict[str, float]       # KPI détaillés
    evenements: List[str]             # Journal simulation
    recommandations: List[str]        # Suggestions

    # Métriques incluses :
    # - marge_totale
    # - ca_total
    # - cout_stockage
    # - jours_rupture
    # - nombre_reappros
    # - stock_final_moyen
```

#### Méthodes principales

```python
# Simulation
simuler_scenario(scenario: Scenario, duree_jours: int = 90) -> ResultatSimulation
comparer_scenarios(scenarios: List[Scenario]) -> Dict[str, ResultatSimulation]

# Scénarios prédéfinis
creer_scenario_croissance(pourcentage: float) -> Scenario
creer_scenario_optimisation_fournisseur(nouveau_delai: int) -> Scenario
creer_scenario_ajustement_prix(variation_achat: float, variation_vente: float) -> Scenario
```

---

### 2.7 Module `stockflow_gui.py` (Interface Graphique)

Interface **Tkinter moderne** intégrant l'ensemble des fonctionnalités.

#### Architecture GUI (MVC)

```
Vue (Tkinter)
├── Fenêtre principale
│   ├── Barre latérale navigation
│   └── Zone contenu principale
│
Sections (9 vues)
├── 📊 Dashboard
├── 📦 Articles
├── 📋 Mouvements
├── 🔮 Prévisions
├── 📈 Analytics
├── 📥 Réappro
├── 📅 Timeline
├── 🎮 Scénarios
└── ⚙️ Paramètres

Contrôleur
├── Gestionnaire événements
├── Sauvegarde automatique
└── Rafraîchissement données
```

#### Sections détaillées

##### 1. Dashboard 📊

**Widgets :**
- 4 cartes KPI (nb articles, valeur stock, ruptures, marge)
- Liste anomalies critiques avec codes couleur
- Bouton actualisation

**Mise à jour :** Temps réel à chaque changement

##### 2. Articles 📦

**Fonctionnalités :**
- Liste complète articles (Treeview)
- Colonnes : Nom, Réf, Cat, Stock, Seuil, Prix, Statut
- Boutons : Ajouter, Modifier, Supprimer
- Actions rapides : Vendre, Recevoir
- Filtrage par catégorie et statut

**Formulaire article :**
- Tous les champs éditables
- Validation temps réel
- Calcul automatique marges

##### 3. Mouvements 📋

**Affichage :**
- Historique complet (Treeview)
- Filtres : Date, Type, Article
- Export CSV direct

**Actions :**
- Ajout mouvement manuel
- Correction historique
- Annulation (si autorisé)

##### 4. Prévisions 🔮

**3 sous-sections :**

**Anomalies :**
- Liste détaillée avec sévérité
- Codes couleur (🔴🟠🟡🟢🔵)
- Suggestions actions correctives

**Seuils automatiques :**
- Tableau comparatif (manuel vs auto)
- Bouton "Appliquer seuils auto"
- Visualisation formule

**Prévisions ventes :**
- Sélection article
- Graphique 30 jours futurs
- Détection tendance

##### 5. Analytics 📈

**KPI Globaux :**
- Tableau de bord financier complet
- Graphiques (si matplotlib disponible)

**Top Produits :**
- Top 5 ventes
- Top 5 CA
- Top 5 marge
- Top 5 rotation

**Analyse ABC :**
- Répartition A/B/C
- Tableau détaillé par catégorie

##### 6. Réappro 📥

**Liste recommandations :**
- Triée par urgence (CRITIQUE → FAIBLE)
- Icônes priorité (🔴🟠🟡🔵)
- Quantités optimales (EOQ)

**Actions :**
- Générer bon de commande
- Filtrer par fournisseur
- Export CSV commandes

##### 7. Timeline 📅

**Journal complet :**
- Tous les mouvements chronologiques
- Filtrage période
- Recherche texte

**Export :**
- CSV pour Excel
- JSON pour scripts

##### 8. Scénarios 🎮

**Création scénario :**
- Formulaire paramètres
- Templates prédéfinis

**Simulation :**
- Lancement 90 jours
- Affichage résultats
- Score visuel (jauge 0-100)

**Comparaison :**
- Tableau côte à côte
- Recommandation meilleur scénario

##### 9. Paramètres ⚙️

**Configuration :**
- Choix thème (8 disponibles)
- Paramètres globaux
- Import/Export données
- Réinitialisation

#### Système de Thèmes

**8 thèmes intégrés :**
1. Clair (défaut)
2. Sombre
3. Bleu
4. Vert
5. Violet
6. Orange
7. Rose
8. Professionnel

**Personnalisation :**
- Couleurs primaire/secondaire
- Police et tailles
- Espacements
- Ombres et bordures

#### Sauvegarde Automatique

**Déclencheurs :**
- Ajout/modification/suppression article
- Ajout mouvement
- Application seuils automatiques
- Changement paramètres

**Fichier :** `stockflow_inventaire.json`

**Format :**
```json
{
  "articles": [...],
  "mouvements": [...],
  "version": "1.0",
  "derniere_sauvegarde": "2025-01-20T15:30:00"
}
```

---

## 3. Structures de données

### 3.1 Hiérarchie des Classes

```
Inventaire (classe principale)
├── articles: Dict[str, Article]
├── mouvements: List[Mouvement]
└── fichier_sauvegarde: str

Article (dataclass)
├── Identifiants (id, nom, référence)
├── Classification (catégorie)
├── Stock (quantité, seuils, optimal)
├── Prix (achat, vente)
├── Fournisseur (nom, délai)
└── Métriques calculées (ventes/j, rotation)

Mouvement (dataclass)
├── Identifiants (id, article_id)
├── Type (entrée/sortie)
├── Quantité et prix
├── Horodatage
└── Motif

Anomalie (dataclass)
├── Type et sévérité
├── Article concerné
├── Message descriptif
└── Valeurs (actuelle, attendue)

KPIArticle (dataclass)
├── Valeur stock
├── Marges
├── Rotation
└── Ventes/CA

RecommandationReappro (dataclass)
├── Article et quantités
├── Urgence
├── Fournisseur
└── Coûts

Scenario (dataclass)
├── Nom et description
├── Paramètres simulation
└── Résultats
```

### 3.2 Persistance JSON

**Structure fichier stockflow_inventaire.json :**

```json
{
  "version": "1.0",
  "derniere_modification": "2025-01-20T15:30:00",
  "articles": [
    {
      "id": "uuid-123",
      "nom": "Souris Gamer RGB",
      "reference": "MG-001",
      "categorie": "electronique",
      "quantite": 45,
      "seuil_min": 20,
      "seuil_min_auto": 32,
      "stock_optimal": 100,
      "prix_achat": 15.00,
      "prix_vente": 25.00,
      "fournisseur": "TechSupply Co",
      "delai_reappro_jours": 7,
      "ventes_jour": 3.2,
      "rotation_stock": 4.5
    }
  ],
  "mouvements": [
    {
      "id": "uuid-456",
      "article_id": "uuid-123",
      "type": "sortie",
      "quantite": 5,
      "date": "2025-01-20 14:30:00",
      "prix_unitaire": 25.00,
      "motif": "Vente en ligne"
    }
  ],
  "parametres": {
    "theme": "clair",
    "marge_securite_defaut": 1.5,
    "duree_prevision_defaut": 30
  }
}
```

---

## 4. Algorithmes clés

### 4.1 Seuil Automatique

**Complexité :** O(n) où n = mouvements de l'article

```
ALGORITHME calculer_seuil_automatique(article_id, marge_securite)

    # Étape 1 : Collecter ventes sur 30 jours
    mouvements ← filtrer_mouvements(article_id, type="sortie", jours=30)

    # Étape 2 : Calculer moyenne
    total_ventes ← somme(mouvement.quantite pour mouvement dans mouvements)
    ventes_jour ← total_ventes / 30

    # Étape 3 : Récupérer délai fournisseur
    article ← obtenir_article(article_id)
    delai ← article.delai_reappro_jours

    # Étape 4 : Appliquer formule
    seuil ← arrondi((ventes_jour × délai) × marge_securite)

    # Étape 5 : Borner valeur
    seuil ← max(1, min(seuil, article.stock_optimal))

    RETOURNER seuil
```

### 4.2 Détection Anomalies

**Complexité :** O(n × m) où n = articles, m = mouvements moyens/article

```
ALGORITHME detecter_anomalies()

    anomalies ← liste_vide

    POUR CHAQUE article DANS inventaire FAIRE

        # Anomalie 1 : Stock négatif
        SI article.quantite < 0 ALORS
            ajouter_anomalie(STOCK_NEGATIF, CRITIQUE, article)

        # Anomalie 2 : Rupture
        SINON SI article.quantite = 0 ALORS
            ajouter_anomalie(RUPTURE, ELEVEE, article)

        # Anomalie 3 : Stock critique
        SINON SI article.quantite < article.seuil_min ALORS
            ajouter_anomalie(STOCK_CRITIQUE, MOYENNE, article)

        # Anomalie 4 : Surstock
        SI article.quantite > article.stock_optimal × 2 ALORS
            ajouter_anomalie(SURSTOCK, FAIBLE, article)

        # Anomalie 5 : Stock dormant
        ventes_90j ← compter_ventes(article.id, jours=90)
        SI ventes_90j = 0 ET article.quantite > 0 ALORS
            ajouter_anomalie(STOCK_DORMANT, MOYENNE, article)

        # Anomalie 6 : Variation anormale
        variation ← analyser_variation_stock(article.id)
        SI abs(variation) > 200% ALORS
            ajouter_anomalie(VARIATION_ANORMALE, MOYENNE, article)

    FIN POUR

    # Tri par sévérité
    trier(anomalies, clé=lambda a: a.severite.value)

    RETOURNER anomalies
```

### 4.3 Analyse ABC (Pareto)

**Complexité :** O(n log n) (tri)

```
ALGORITHME calculer_abc_analysis()

    # Étape 1 : Calculer valeur stock par article
    articles_valeur ← liste_vide
    POUR CHAQUE article DANS inventaire FAIRE
        valeur ← article.quantite × article.prix_achat
        ajouter(articles_valeur, {article, valeur})
    FIN POUR

    # Étape 2 : Tri décroissant
    trier(articles_valeur, clé=valeur, ordre=DÉCROISSANT)

    # Étape 3 : Calcul valeur totale
    valeur_totale ← somme(av.valeur pour av dans articles_valeur)

    # Étape 4 : Classification
    valeur_cumulee ← 0
    resultat ← {A: [], B: [], C: []}

    POUR CHAQUE article_valeur DANS articles_valeur FAIRE
        valeur_cumulee ← valeur_cumulee + article_valeur.valeur
        pourcentage_cumul ← (valeur_cumulee / valeur_totale) × 100

        SI pourcentage_cumul ≤ 80 ALORS
            categorie ← 'A'
        SINON SI pourcentage_cumul ≤ 95 ALORS
            categorie ← 'B'
        SINON
            categorie ← 'C'
        FIN SI

        ajouter(resultat[categorie], article_valeur)
    FIN POUR

    RETOURNER resultat
```

### 4.4 EOQ (Quantité Économique de Commande)

**Complexité :** O(n) (calcul demande annuelle)

```
ALGORITHME calculer_eoq(article_id, cout_commande)

    # Étape 1 : Demande annuelle
    ventes_jour ← calculer_ventes_moyennes_jour(article_id, jours=30)
    demande_annuelle ← ventes_jour × 365

    # Étape 2 : Coût de stockage (20% du prix achat)
    article ← obtenir_article(article_id)
    cout_stockage ← article.prix_achat × 0.20

    # Étape 3 : Formule de Wilson
    SI cout_stockage > 0 ALORS
        numerateur ← 2 × demande_annuelle × cout_commande
        eoq ← racine_carree(numerateur / cout_stockage)
        RETOURNER arrondi(eoq)
    SINON
        RETOURNER article.stock_optimal
    FIN SI
```

### 4.5 Simulation Scénario

**Complexité :** O(k × n) où k = jours simulation, n = articles

```
ALGORITHME simuler_scenario(scenario, duree_jours)

    # Initialisation
    inventaire_simule ← copie_profonde(inventaire_actuel)
    metriques ← {marge_totale: 0, ca_total: 0, jours_rupture: 0, ...}
    evenements ← []

    # Simulation jour par jour
    POUR jour ← 1 À duree_jours FAIRE

        POUR CHAQUE article DANS inventaire_simule FAIRE

            # Génération vente quotidienne
            vente_base ← article.ventes_jour
            vente_ajustee ← vente_base × (1 + scenario.croissance_ventes)
            quantite_vendue ← arrondi_aleatoire(vente_ajustee)

            # Tentative vente
            SI article.quantite ≥ quantite_vendue ALORS
                article.quantite ← article.quantite - quantite_vendue
                ca ← quantite_vendue × article.prix_vente
                marge ← quantite_vendue × (article.prix_vente - article.prix_achat)
                metriques.ca_total ← metriques.ca_total + ca
                metriques.marge_totale ← metriques.marge_totale + marge
            SINON
                # Rupture de stock
                metriques.jours_rupture ← metriques.jours_rupture + 1
                evenements.ajouter(f"Rupture {article.nom} jour {jour}")
            FIN SI

            # Déclenchement réappro automatique
            SI article.quantite < article.seuil_min ALORS
                qte_reappro ← calculer_quantite_optimale(article.id, scenario.methode)
                article.quantite ← article.quantite + qte_reappro
                metriques.nombre_reappros ← metriques.nombre_reappros + 1
                evenements.ajouter(f"Réappro {article.nom}: +{qte_reappro}")
            FIN SI

            # Calcul coût stockage journalier
            cout ← (article.quantite × article.prix_achat × 0.20) / 365
            metriques.cout_stockage ← metriques.cout_stockage + cout

        FIN POUR

    FIN POUR

    # Calcul score final
    score ← calculer_score(metriques)

    RETOURNER ResultatSimulation(scenario, score, metriques, evenements)
```

---

## 5. Fonctionnement général (workflow)

### 5.1 Workflow Utilisateur

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. LANCEMENT APPLICATION                     │
│         python3 stockflow_gui.py                                │
│         Chargement stockflow_inventaire.json                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              2. INITIALISATION INVENTAIRE                       │
│   • Si fichier existe → chargement données                      │
│   • Si fichier absent → création + données exemple              │
│   • Calcul seuils automatiques                                  │
│   • Détection anomalies initiale                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   3. AFFICHAGE DASHBOARD                        │
│   • KPI temps réel                                              │
│   • Anomalies critiques                                         │
│   • Navigation sections                                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  4. ACTIONS UTILISATEUR                         │
│                                                                  │
│   Scénario A : Vente produit                                    │
│   ├── Sélection article                                         │
│   ├── Saisie quantité                                           │
│   ├── Validation stock disponible                               │
│   ├── Création mouvement "sortie"                               │
│   ├── Mise à jour quantité article                              │
│   ├── Sauvegarde automatique                                    │
│   └── Rafraîchissement dashboard                                │
│                                                                  │
│   Scénario B : Réapprovisionnement                              │
│   ├── Consultation recommandations                              │
│   ├── Sélection articles à commander                            │
│   ├── Vérification quantités optimales (EOQ)                    │
│   ├── Génération bon de commande                                │
│   ├── Création mouvements "entrée"                              │
│   ├── Sauvegarde                                                │
│   └── Export CSV bon de commande                                │
│                                                                  │
│   Scénario C : Analyse performance                              │
│   ├── Consultation KPI Analytics                                │
│   ├── Analyse ABC (classification produits)                     │
│   ├── Top 5 ventes/CA/marge                                     │
│   └── Export rapports                                           │
│                                                                  │
│   Scénario D : Simulation What-If                               │
│   ├── Création scénario (+20% ventes)                           │
│   ├── Lancement simulation 90 jours                             │
│   ├── Analyse résultats et score                                │
│   ├── Comparaison avec scénario actuel                          │
│   └── Décision stratégique                                      │
│                                                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                5. SAUVEGARDE CONTINUE                           │
│   • Après chaque action                                         │
│   • Format JSON                                                 │
│   • Backup horodaté                                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  6. FERMETURE / REPRISE                         │
│   • État complet sauvegardé                                     │
│   • Reprise exacte session suivante                             │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Flux de Données

```
Interface Utilisateur (GUI)
          │
          ▼
    ┌─────────────────┐
    │  Contrôleur     │ ← Gestion événements
    │  (stockflow_gui)│
    └────────┬────────┘
             │
             ├─────────────┬─────────────┬──────────────┐
             ▼             ▼             ▼              ▼
       ┌─────────┐   ┌──────────┐  ┌──────────┐  ┌──────────┐
       │  stock  │   │predictions│  │analytics │  │restocking│
       │         │   │           │  │          │  │          │
       │(modèle) │   │   (IA)    │  │  (KPI)   │  │ (réappro)│
       └────┬────┘   └─────┬────┘  └────┬─────┘  └────┬─────┘
            │              │            │             │
            └──────────────┴────────────┴─────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  Persistance   │
                  │  (JSON file)   │
                  └────────────────┘
```

---

## 6. Contraintes techniques et choix de conception

### 6.1 Principes directeurs

| Principe | Mise en œuvre |
|----------|---------------|
| **Portabilité** | Python 3.8+ natif, Tkinter inclus |
| **Zéro dépendance externe** | Pas de pip install requis |
| **Simplicité utilisateur** | Interface graphique intuitive |
| **Modularité stricte** | 6 modules indépendants |
| **Performance** | Complexités optimisées, caching |
| **Robustesse** | Validation données, gestion erreurs |

### 6.2 Choix Techniques

#### Pourquoi Python ?
- Syntaxe claire et lisible
- Dataclasses modernes (Python 3.7+)
- Bibliothèque standard riche
- Portabilité multiplateforme

#### Pourquoi Tkinter ?
- Inclus nativement (aucune installation)
- Léger et rapide
- Suffisant pour application métier
- Thèmes personnalisables

#### Pourquoi JSON (pas SQL) ?
- Simplicité (aucun serveur)
- Human-readable (débogage facile)
- Portable (copie simple)
- Suffisant pour PME (<10000 articles)

**Migration SQL possible :**
```python
# Facile à migrer vers SQLite/PostgreSQL
# Structure déjà normalisée (articles, mouvements)
```

#### Pourquoi Dataclasses ?
- Génération automatique `__init__`, `__repr__`, `__eq__`
- Type hints natifs
- Properties calculées élégantes
- Sérialisation facile (asdict, fromdict)

### 6.3 Optimisations Implémentées

| Optimisation | Technique | Gain |
|--------------|-----------|------|
| **Cache seuils** | Stockage 5 min | Évite recalcul constant |
| **Index UUID** | Dictionnaire articles | O(1) au lieu de O(n) |
| **Tri natif Python** | Timsort | O(n log n) optimal |
| **Lazy loading** | Chargement à la demande | Démarrage rapide |
| **Batch updates** | Groupement mises à jour GUI | Fluidité interface |

### 6.4 Gestion Erreurs

**Stratégie défensive :**

```python
# Validation en amont
def ajouter_mouvement(self, mouvement: Mouvement) -> bool:
    try:
        # 1. Vérification existence article
        if not self.obtenir_article(mouvement.article_id):
            logging.error(f"Article {mouvement.article_id} inexistant")
            return False

        # 2. Vérification stock suffisant (sortie)
        if mouvement.type == "sortie":
            article = self.obtenir_article(mouvement.article_id)
            if article.quantite < mouvement.quantite:
                logging.warning(f"Stock insuffisant : {article.nom}")
                return False

        # 3. Validation quantité positive
        if mouvement.quantite <= 0:
            logging.error("Quantité doit être positive")
            return False

        # 4. Ajout effectif
        self.mouvements.append(mouvement)
        self._mettre_a_jour_stock(mouvement)
        self.sauvegarder()
        return True

    except Exception as e:
        logging.exception(f"Erreur ajout mouvement : {e}")
        return False
```

**Logging :**
- Niveau INFO : opérations normales
- Niveau WARNING : situations anormales non bloquantes
- Niveau ERROR : échecs d'opérations
- Niveau CRITICAL : erreurs système

---

## 7. Évolutions possibles

### 7.1 Améliorations Fonctionnelles

| Évolution | Description | Complexité |
|-----------|-------------|------------|
| **Multi-entrepôts** | Gestion stock sur plusieurs sites | Moyenne |
| **Codes-barres** | Scan produits (intégration webcam) | Moyenne |
| **Alertes email** | Notifications ruptures automatiques | Faible |
| **Prévisions ML** | Deep learning (LSTM, Prophet) | Élevée |
| **Multi-devises** | Support international | Faible |
| **Tarifs fournisseurs** | Comparaison automatique prix | Moyenne |
| **Gestion lots** | Traçabilité FIFO/LIFO | Moyenne |
| **Dates expiration** | Alertes péremption (alimentaire) | Faible |
| **API REST** | Intégration e-commerce (Shopify, WooCommerce) | Moyenne |
| **Export comptable** | Format FEC (France) | Moyenne |

### 7.2 Améliorations Techniques

| Évolution | Description | Avantages |
|-----------|-------------|-----------|
| **Migration SQLite** | Base de données relationnelle | Performance, requêtes complexes |
| **Interface Web** | Flask/FastAPI + React | Multi-utilisateurs, cloud |
| **Tests unitaires** | pytest (couverture 80%+) | Fiabilité, maintenance |
| **CI/CD** | GitHub Actions | Déploiement automatisé |
| **Docker** | Conteneurisation | Déploiement facile |
| **Authentification** | Multi-utilisateurs, rôles | Sécurité, audit |
| **Cache Redis** | Accélération calculs | Performance temps réel |
| **GraphQL API** | Alternative REST | Flexibilité requêtes |
| **Graphiques avancés** | Plotly/Chart.js interactifs | Visualisation riche |
| **Mobile app** | React Native/Flutter | Mobilité (inventaire terrain) |

### 7.3 Feuille de Route Suggérée

**Phase 1 (Court terme - 1-2 mois) :**
1. Tests unitaires complets (pytest)
2. Migration SQLite
3. Alertes email ruptures
4. Export comptable FEC

**Phase 2 (Moyen terme - 3-6 mois) :**
1. Interface web (Flask + React)
2. Multi-utilisateurs + authentification
3. API REST complète
4. Intégration e-commerce (WooCommerce)

**Phase 3 (Long terme - 6-12 mois) :**
1. Machine Learning prévisions (Prophet)
2. Multi-entrepôts géographiques
3. Application mobile
4. Tableaux de bord BI avancés (PowerBI/Tableau)

---

## Annexes

### A.1 Diagramme Dépendances Modules

```
                    ┌──────────────────┐
                    │  stockflow_gui   │
                    │  (Interface GUI) │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐         ┌──────────┐       ┌──────────┐
    │ stock   │◄────────│predictions│       │analytics │
    │         │         │          │       │          │
    └────┬────┘         └────┬─────┘       └────┬─────┘
         │                   │                   │
         │                   ▼                   │
         │              ┌──────────┐             │
         └─────────────►│restocking│◄────────────┘
                        └────┬─────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐         ┌──────────┐       ┌──────────┐
    │timeline │         │scenarios │       │ storage  │
    │         │         │          │       │  (JSON)  │
    └─────────┘         └──────────┘       └──────────┘
```

### A.2 Métriques Complexité

| Module | Lignes | Classes | Fonctions | Complexité Cyclomatique Moy. |
|--------|--------|---------|-----------|------------------------------|
| stock.py | 412 | 3 | 25 | 4.2 |
| predictions.py | 367 | 4 | 18 | 5.8 |
| analytics.py | 518 | 3 | 32 | 3.9 |
| restocking.py | 423 | 4 | 21 | 4.7 |
| timeline.py | 354 | 2 | 15 | 3.1 |
| scenarios.py | 401 | 3 | 19 | 6.2 |
| stockflow_gui.py | 1047 | 1 | 42 | 7.3 |

**Total : ~3500 lignes, 20 classes, 172 fonctions**

### A.3 Exemples Requêtes Fréquentes

**1. Obtenir articles en rupture :**
```python
ruptures = [a for a in inventaire.lister_articles() if a.quantite <= 0]
```

**2. Calculer CA mensuel :**
```python
date_debut = datetime.now() - timedelta(days=30)
mouvements_sortie = [m for m in inventaire.mouvements
                     if m.type == "sortie" and m.date >= date_debut]
ca = sum(m.quantite * m.prix_unitaire for m in mouvements_sortie)
```

**3. Top 5 produits rentables :**
```python
articles_tries = sorted(inventaire.lister_articles(),
                       key=lambda a: a.marge_unitaire * a.quantite,
                       reverse=True)
top5 = articles_tries[:5]
```

**4. Détection stock dormant :**
```python
date_limite = datetime.now() - timedelta(days=90)
dormants = []
for article in inventaire.lister_articles():
    mouvements = [m for m in inventaire.obtenir_mouvements(article.id)
                  if m.type == "sortie" and m.date >= date_limite]
    if len(mouvements) == 0 and article.quantite > 0:
        dormants.append(article)
```

---

*Documentation générée pour le projet NSI — StockFlow Pro v1.0*

*Dernière mise à jour : 2025-01-20*
