# StockFlow Pro 📦

> **Système intelligent de gestion de stock** avec prévisions automatiques, détection d'anomalies et interface graphique moderne

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-Educational-orange.svg)](LICENSE)

**Projet NSI** transformé en solution professionnelle de gestion d'inventaire avec intelligence artificielle intégrée.

---

## 🚀 Démarrage Rapide

### Installation

```bash
# Cloner le projet
git clone https://github.com/synnheal/projet-nsi.git
cd projet-nsi

# Aucune dépendance externe requise !
# Python 3.8+ avec tkinter (inclus par défaut)
```

### Lancement

```bash
# Interface graphique moderne (RECOMMANDÉ)
python3 stockflow_gui.py

# Démonstration console
python3 stockflow_demo.py
```

**C'est tout !** 🎉 L'application démarre avec des données d'exemple.

---

## 📸 Aperçu

### Dashboard Principal
```
┌─────────────────────────────────────────────────────────────┐
│  📊 Dashboard                              🔄 Actualiser    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Articles │  │  Valeur  │  │ Ruptures │  │  Marge   │   │
│  │    25    │  │ 145,680€ │  │    2 🔴  │  │  36.2%   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ⚠️  5 Anomalie(s) Détectées                                │
│  🔴 Samsung Galaxy S24 - Rupture de stock                   │
│  🟠 AirPods Pro 2 - Stock critique (2 unités)               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Interface Complète
- **9 sections** accessibles via sidebar
- **Design moderne** avec cartes et ombres
- **Thèmes personnalisables** (8 disponibles)
- **Sauvegarde automatique** après chaque action

---

## ✨ Fonctionnalités Principales

### 🎯 Gestion Intelligente du Stock

#### 1. Seuils Automatiques
Le système calcule automatiquement les seuils d'alerte pour chaque article :

**Formule** : `Seuil = Ventes/jour × Délai réappro × Marge sécurité (1.5)`

**Exemple** :
```
Article : MacBook Pro 16"
Ventes moyennes : 0.8/jour
Délai fournisseur : 7 jours
→ Seuil calculé : 8 unités

Stock actuel : 5 unités
→ ⚠️ "Rupture prévue dans 6 jours"
```

#### 2. Prévisions de Ventes
Analyse automatique basée sur l'historique :
- **Moyenne glissante** sur 30 jours
- **Détection de tendance** (hausse/baisse/stable)
- **Niveau de confiance** calculé
- **Estimation mensuelle**

**Exemple** :
```
📈 iPhone 15 Pro
   Ventes/jour : 2.5
   Prévision mois : 75 unités
   Tendance : Hausse (+15.3%)
   Confiance : 85%
```

#### 3. Détection d'Anomalies
6 types d'anomalies détectées automatiquement :

| Type | Sévérité | Description |
|------|----------|-------------|
| Stock négatif | 🔴 Critique | Erreur de saisie détectée |
| Rupture de stock | 🔴 Critique | Article en rupture |
| Stock critique | 🟠 Élevée | Sous le seuil minimum |
| Surstock | 🟡 Moyenne | Immobilisation de capital |
| Article mort | 🔵 Faible | Aucune vente enregistrée |
| Variation brutale | 🟡 Moyenne | Pic de ventes inhabituel |

### 💰 Analyses Financières

#### 4. Tableaux de Bord Complets
KPIs calculés en temps réel :
- 💵 **Valeur stock totale** (prix d'achat)
- 💰 **Valeur vente potentielle**
- 📊 **Marge potentielle** et taux moyen
- 🔄 **Rotation des stocks** (turnover)
- 💎 **Coût de stockage** (25% annuel)

#### 5. Analyse ABC (Pareto)
Classification automatique selon la loi des 80/20 :
- **Catégorie A** : 20% des articles = 80% de la valeur → Priorité maximale
- **Catégorie B** : 30% des articles = 15% de la valeur → Priorité moyenne
- **Catégorie C** : 50% des articles = 5% de la valeur → Priorité faible

#### 6. Statistiques par Catégorie
10 catégories prédéfinies :
- 💻 Électronique
- 👕 Vêtements
- 🍽️ Alimentaire
- 💄 Cosmétique
- 📝 Papeterie
- ⚽ Sport
- 🏠 Maison
- 🧸 Jouets
- 📚 Livres
- 📦 Autres

### 📦 Réapprovisionnement Intelligent

#### 7. Recommandations Automatiques
Le système génère des recommandations prioritaires :

**Niveaux d'urgence** :
- 🔴 **CRITIQUE** : Rupture immédiate (stock = 0)
- 🟠 **ÉLEVÉE** : Sous seuil critique
- 🟡 **MOYENNE** : Approche du seuil
- 🔵 **FAIBLE** : Réapprovisionnement préventif

**Calcul des quantités** :
```
Quantité recommandée = Stock optimal - Stock actuel

Avec ajustement selon :
- Délai de livraison
- Ventes prévues
- Saisonnalité
```

#### 8. Bons de Commande
Génération automatique :
- **Groupement** par fournisseur
- **Calcul du coût** total
- **Priorisation** par urgence
- **Export** texte/CSV

**Exemple** :
```
===============================================================
BON DE COMMANDE N° BC-20250116-143022
===============================================================

Fournisseur: Apple France
Date:        16/01/2025 14:30
Urgence:     ELEVEE 🟠

---------------------------------------------------------------
Réf.            Article                      Qté    P.U.    Total
---------------------------------------------------------------
APPLE-APP2      AirPods Pro 2                 48   210.00€  10,080€
APPLE-MBP-16    MacBook Pro 16"                7  2200.00€  15,400€
---------------------------------------------------------------
TOTAL                                         55            25,480€
===============================================================
```

### 📊 Visualisation et Rapports

#### 9. Timeline Chronologique
Journal complet des mouvements :
- 📥 **Entrées** (réapprovisionnements, retours)
- 📤 **Sorties** (ventes, pertes, casse)
- ✏️ **Corrections** d'inventaire
- 📋 **Inventaires** physiques

**Fonctionnalités** :
- Recherche par mot-clé
- Filtres par période/type/article
- Export CSV
- Statistiques hebdomadaires/mensuelles

#### 10. Export HTML Professionnel
Rapports avec :
- 📊 Graphiques intégrés (courbes, camemberts, barres)
- 🎨 Signalements visuels par couleur
- 📋 Tableaux détaillés
- 💾 Export PDF (via navigateur)

### 🔮 Simulations de Scénarios

#### 11. What-If Analysis
Simulez l'impact de différents scénarios sur 90 jours :

**Scénarios prédéfinis** :
- 📈 Ventes +20% (campagne marketing)
- 📉 Ventes -20% (période creuse)
- 💰 Prix +10% (inflation)
- 📦 Coûts +15% (hausse fournisseurs)
- ⏱️ Délais +5 jours (problèmes logistiques)
- 🎯 Optimiste (ventes +15%, marge +5%)
- ⚠️ Pessimiste (ventes -15%, coûts +10%)

**Métriques comparées** :
- Chiffre d'affaires projeté
- Marge potentielle
- Nombre de ruptures
- CA perdu (ventes manquées)
- Coût de stockage
- **Score global** 0-100

**Exemple de résultat** :
```
🥇 Optimiste (Score: 87/100)
   CA: 198,450€ | Marge: 52,770€ (36.2%)
   Ruptures: 2 | CA perdu: 3,200€

🥈 Actuel (Score: 76/100)
   CA: 175,320€ | Marge: 45,890€ (34.8%)
   Ruptures: 5 | CA perdu: 8,100€

🥉 Ventes +20% (Score: 71/100)
   CA: 210,384€ | Marge: 55,024€ (35.1%)
   Ruptures: 12 | CA perdu: 15,600€ ⚠️
```

---

## 🖥️ Interface Graphique

### 9 Sections Complètes

| Section | Icône | Description |
|---------|-------|-------------|
| **Dashboard** | 📊 | Vue d'ensemble, KPIs, anomalies |
| **Articles** | 📦 | CRUD complet, vente, réappro |
| **Mouvements** | 📝 | Journal, statistiques |
| **Prévisions** | 🔮 | Anomalies, tendances |
| **Analyses** | 💰 | KPIs financiers, Top 5 |
| **Réappro** | 🚚 | Recommandations, bons de commande |
| **Timeline** | 📅 | Historique chronologique |
| **Scénarios** | 🎯 | Simulations What-If |
| **Réglages** | ⚙️ | Sauvegarde, exports, thèmes |

### Actions Rapides

#### Ajouter un article
1. Cliquer sur **📦 Articles**
2. Cliquer sur **➕ Nouvel Article**
3. Remplir le formulaire (nom, référence, quantité, prix...)
4. Cliquer sur **✅ Créer**

#### Enregistrer une vente
1. Dans **📦 Articles**, trouver l'article
2. Cliquer sur **📤 Vente**
3. Entrer la quantité vendue
4. Valider

#### Réapprovisionner
1. Dans **📦 Articles**, trouver l'article
2. Cliquer sur **📥 Entrée**
3. Entrer la quantité reçue
4. Valider

#### Voir les anomalies
1. Cliquer sur **🔮 Prévisions**
2. Liste complète avec sévérité et recommandations

#### Simuler des scénarios
1. Cliquer sur **🎯 Scénarios**
2. Cliquer sur **▶️ Lancer la Simulation**
3. Comparer les résultats avec scores

---

## 📚 Architecture

### Modules Python

| Module | Lignes | Description |
|--------|--------|-------------|
| `stock.py` | ~400 | Gestion inventaire, articles, mouvements |
| `predictions.py` | ~350 | Seuils auto, prévisions, anomalies |
| `analytics.py` | ~500 | KPIs, ABC, rotation, marges |
| `restocking.py` | ~400 | Recommandations, EOQ, bons commande |
| `timeline.py` | ~350 | Journal, recherche, export CSV |
| `scenarios.py` | ~400 | Simulations What-If, comparaisons |
| `themes.py` | ~200 | 8 thèmes personnalisables |
| `charts.py` | ~300 | Graphiques (ligne, pie, barres) |
| `export_html.py` | ~150 | Rapports HTML |

**Total** : ~3700 lignes de code Python

### Structure des Données

#### Article
```python
{
    "id": "uuid",
    "nom": "MacBook Pro 16\"",
    "reference": "APPLE-MBP-16",
    "categorie": "electronique",
    "quantite": 8,
    "seuil_min": 3,
    "seuil_min_auto": 8,  # Calculé automatiquement
    "stock_optimal": 15,
    "prix_achat": 2200.0,
    "prix_vente": 2899.0,
    "fournisseur": "Apple France",
    "delai_reappro_jours": 7,
    "ventes_jour": 0.8,  # Calculé
    "rotation_stock": 10.5  # Calculé
}
```

#### Mouvement
```python
{
    "id": "uuid",
    "article_id": "uuid",
    "type": "sortie",  # "entree", "sortie", "correction", "inventaire"
    "quantite": 2,
    "date": "2025-01-16T14:30:00",
    "prix_unitaire": 2899.0,
    "motif": "vente",  # "reappro", "retour", "perte", etc.
    "commentaire": "Vente client VIP"
}
```

---

## 📈 Indicateurs Clés (KPI)

Le système calcule automatiquement :

| KPI | Formule | Description |
|-----|---------|-------------|
| **Taux de marge** | (Marge / CA) × 100 | Rentabilité moyenne |
| **Rotation stock** | Ventes annuelles / Stock moyen | Vitesse d'écoulement |
| **Taux de service** | (1 - Ruptures/Demandes) × 100 | Disponibilité |
| **Couverture stock** | Stock / Ventes jour | Autonomie en jours |
| **Stock mort** | Articles sans vente > 90j | Immobilisation |
| **Coût stockage** | Valeur stock × 25% | Coût annuel estimé |

---

## 🎯 Cas d'Usage

### E-commerce
- Gestion multi-références
- Alertes de rupture en temps réel
- Optimisation des commandes fournisseurs
- Prévisions saisonnières

### Boutique Physique
- Inventaire en temps réel
- Réapprovisionnement intelligent
- Réduction du surstock
- Analyse des ventes

### Distribution / Grossiste
- Analyse ABC pour prioriser
- Rotation optimale du stock
- Réduction des coûts de stockage
- Simulations What-If

### Startup / PME
- Dashboard financier complet
- Décisions basées sur les données
- Simulations avant investissement
- Export pour comptabilité

---

## 🔧 Configuration Avancée

### Catégories Personnalisées

```python
from projectflow.stock import CATEGORIES_ARTICLES

# Ajouter une catégorie
CATEGORIES_ARTICLES["bio"] = {
    "nom": "Produits Bio",
    "icone": "🌱",
    "couleur": "#22c55e"
}
```

### Seuils Personnalisés

```python
from projectflow.predictions import PredictionEngine

predictions = PredictionEngine(inventaire)

# Marge de sécurité par défaut : 1.5
# Plus prudent : 2.0
seuil = predictions.calculer_seuil_automatique(
    article_id="...",
    marge_securite=2.0
)
```

### Méthodes de Réapprovisionnement

```python
from projectflow.restocking import RestockingEngine

restocking = RestockingEngine(inventaire, predictions)

# Méthode 1 : Stock optimal (par défaut)
qte = restocking.calculer_quantite_optimale(
    article_id="...",
    methode="stock_optimal"
)

# Méthode 2 : Formule de Wilson (EOQ)
qte = restocking.calculer_quantite_optimale(
    article_id="...",
    methode="eoq"
)
```

---

## 🌟 Fonctionnalités Avancées

### Formule de Wilson (EOQ)
Quantité économique de commande :

```
EOQ = √((2 × Demande annuelle × Coût commande) / Coût stockage)
```

**Exemple** :
```python
from projectflow.restocking import RestockingEngine

restocking = RestockingEngine(inventaire, predictions)
qte_optimale = restocking.calculer_quantite_optimale(
    article_id="...",
    methode="eoq"
)

print(f"Quantité économique : {qte_optimale} unités")
# → "Quantité économique : 45 unités"
```

### Analyse d'Impact de Rupture

```python
from projectflow.scenarios import ScenarioEngine

scenario_engine = ScenarioEngine(inventaire, predictions)
impact = scenario_engine.analyser_impact_rupture(
    article_id="...",
    duree_jours=15
)

print(f"CA perdu : {impact['ca_perdu']:,.2f} €")
print(f"Sévérité : {impact['severite']}")
# → CA perdu : 12,450.00 €
# → Sévérité : Élevée
```

### Export CSV de la Timeline

```python
from projectflow.timeline import TimelineManager

timeline = TimelineManager(inventaire)
timeline.exporter_csv("mouvements_90j.csv", jours=90)
```

---

## 🎨 Thèmes Disponibles

8 thèmes modernes pour l'interface :

| Thème | Description | Couleur principale |
|-------|-------------|-------------------|
| 🌙 **Dark** | Sombre élégant (défaut) | #1a1a2e |
| ☀️ **Light** | Clair et lumineux | #ffffff |
| 🌌 **Midnight** | Noir profond | #0f0f0f |
| 🌊 **Ocean** | Bleu océan | #006994 |
| 🌅 **Sunset** | Violet/rose | #7b2cbf |
| 🌲 **Forest** | Vert nature | #2d6a4f |
| ❄️ **Nord** | Style nordique | #2e3440 |
| 🌸 **Rose** | Rose pastel | #ffc8dd |

**Changement** : Section **⚙️ Réglages** dans l'interface

---

## 💾 Sauvegarde et Données

### Sauvegarde Automatique
L'inventaire est sauvegardé automatiquement après chaque :
- Ajout d'article
- Vente
- Entrée de stock
- Modification
- Correction

**Fichier** : `stockflow_inventaire.json`

### Format JSON
```json
{
  "id": "uuid",
  "nom": "Boutique High-Tech",
  "date_creation": "2025-01-16T10:00:00",
  "articles": [...],
  "mouvements": [...]
}
```

### Sauvegarde Manuelle
```python
from projectflow.stock import Inventaire

# Sauvegarder
with open("backup.json", "w") as f:
    json.dump(inventaire.to_dict(), f, indent=2)

# Charger
with open("backup.json", "r") as f:
    data = json.load(f)
    inventaire = Inventaire.from_dict(data)
```

---

## 🧪 Exemples de Code

### Utilisation de Base

```python
from projectflow.stock import Inventaire, Article
from projectflow.predictions import PredictionEngine
from projectflow.analytics import AnalyticsEngine

# Créer un inventaire
inventaire = Inventaire(nom="Ma Boutique")

# Ajouter un article
article = Article(
    nom="MacBook Pro 16\"",
    reference="APPLE-MBP-16",
    categorie="electronique",
    quantite=10,
    seuil_min=3,
    stock_optimal=20,
    prix_achat=2200,
    prix_vente=2899,
    fournisseur="Apple France",
    delai_reappro_jours=7
)
inventaire.ajouter_article(article)

# Enregistrer une vente
inventaire.retirer_stock(
    article.id,
    quantite=2,
    prix_unitaire=2899,
    motif="vente",
    commentaire="Vente client VIP"
)

# Obtenir des prévisions
predictions = PredictionEngine(inventaire)
prevision = predictions.prevoir_ventes(article.id)

print(f"Ventes prévues : {prevision.ventes_mois_prevue:.0f} unités/mois")
print(f"Tendance : {prevision.tendance} ({prevision.tendance_pourcentage:+.1f}%)")
```

### Détection d'Anomalies

```python
# Détecter toutes les anomalies
anomalies = predictions.detecter_anomalies()

for anom in anomalies:
    print(f"{anom.severite.upper()} - {anom.article_nom}")
    print(f"  {anom.message}")
    print(f"  Type: {anom.type}\n")
```

### Recommandations de Réapprovisionnement

```python
from projectflow.restocking import RestockingEngine

restocking = RestockingEngine(inventaire, predictions)
recommandations = restocking.generer_recommandations()

for reco in recommandations:
    print(f"{reco.urgence.name} - {reco.article_nom}")
    print(f"  Commander : {reco.quantite_recommandee} unités")
    print(f"  Coût : {reco.cout_estime:,.2f} €\n")
```

### Simulations de Scénarios

```python
from projectflow.scenarios import ScenarioEngine, Scenario

scenario_engine = ScenarioEngine(inventaire, predictions)

# Scénarios personnalisés
scenarios = [
    Scenario("Ventes +30%", {"variation_ventes": 0.3}),
    Scenario("Prix +15%", {"variation_prix": 0.15}),
]

# Comparer
resultats = scenario_engine.comparer_scenarios(scenarios, duree_jours=90)

for res in resultats:
    print(f"{res.scenario.nom} - Score: {res.score_global:.0f}/100")
    print(f"  CA: {res.chiffre_affaires_total:,.0f} €")
    print(f"  Marge: {res.marge_totale:,.0f} €\n")
```

---

## 🐛 Résolution de Problèmes

### L'interface ne s'affiche pas

```bash
# Vérifier tkinter
python3 -c "import tkinter; print('Tkinter OK')"

# Sur Ubuntu/Debian
sudo apt-get install python3-tk

# Sur macOS (avec Homebrew)
brew install python-tk
```

### Erreur d'import

```bash
# Vérifier les modules
python3 -c "from projectflow import stock, predictions, analytics; print('Modules OK')"
```

### Reset complet

```bash
# Supprimer les données et recommencer
rm stockflow_inventaire.json
python3 stockflow_gui.py
```

### Problème de permissions

```bash
# Rendre exécutable
chmod +x stockflow_gui.py
chmod +x stockflow_demo.py
```

---

## 📝 Documentation Complète

- 📘 **README.md** (ce fichier) : Vue d'ensemble
- 🚀 **LANCEMENT_RAPIDE.md** : Guide de démarrage
- 📖 **docs/architecture.md** : Architecture détaillée
- 💡 **Code source** : Commenté et documenté

---

## 🤝 Contribution

**Projet NSI réalisé par** : [Votre Nom]

### Évolutions Futures

- [ ] Interface web (Flask/Django)
- [ ] Base de données SQLite
- [ ] API REST
- [ ] Application mobile
- [ ] Machine Learning pour prévisions avancées
- [ ] Gestion multi-entrepôts
- [ ] Scanner codes-barres / QR codes
- [ ] Intégration comptable
- [ ] Notifications par email/SMS

---

## 📄 Licence

**Projet éducatif NSI** - Libre d'utilisation à des fins pédagogiques

---

## 🙏 Remerciements

- **Inspiration** : Systèmes ERP professionnels (SAP, Odoo)
- **Framework** : Python + Tkinter
- **Concepts** : Data Science, Analyse de Pareto, Formule de Wilson
- **Design** : Material Design, Modern UI/UX

---

## 📞 Support

Pour toute question ou problème :
1. Consulter **LANCEMENT_RAPIDE.md**
2. Vérifier la section **Résolution de Problèmes**
3. Examiner les exemples de code
4. Créer une issue sur GitHub

---

## 🎓 Contexte Pédagogique

### Compétences NSI Abordées

- ✅ **Programmation** : POO, modules, fonctions
- ✅ **Structures de données** : Listes, dictionnaires, classes
- ✅ **Algorithmique** : Tri, recherche, prévisions
- ✅ **Bases de données** : Persistance JSON
- ✅ **Interface** : Tkinter, événements
- ✅ **Architecture** : MVC, modularité
- ✅ **Data Science** : Statistiques, tendances, simulations

### Concepts Mathématiques

- Moyenne mobile
- Analyse de Pareto (80/20)
- Formule de Wilson (EOQ)
- Calculs statistiques
- Projections linéaires

---

<div align="center">

**StockFlow Pro** - Transformez votre gestion de stock en avantage compétitif ! 🚀

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-green.svg)](https://docs.python.org/3/library/tkinter.html)
[![NSI](https://img.shields.io/badge/Project-NSI-orange.svg)](https://www.education.gouv.fr/)

[Documentation](#-documentation-complète) •
[Exemples](#-exemples-de-code) •
[Support](#-support)

</div>
