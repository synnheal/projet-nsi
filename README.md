# StockFlow Pro 📦

**Système intelligent de gestion de stock** avec prévisions, analyses financières et réapprovisionnement automatique.

> Projet NSI transformé en solution professionnelle de gestion d'inventaire

---

## ✨ Fonctionnalités principales

### 🎯 Gestion intelligente du stock

#### 1. **Seuils automatiques intelligents**
- Calcul automatique des seuils d'alerte basé sur :
  - Vitesse moyenne des ventes
  - Délai de réapprovisionnement
  - Marge de sécurité configurable
- **Exemple** : *"Attention : rupture prévue dans 12 jours"*

#### 2. **Prévisions de ventes**
- Moyenne glissante sur 30 jours
- Détection de tendances (hausse/baisse/stable)
- Estimation du stock restant
- Niveau de confiance calculé

#### 3. **Détection d'anomalies**
Détecte automatiquement :
- ❌ Stocks négatifs (erreurs de saisie)
- 🔴 Ruptures de stock
- 🟠 Stocks critiques avec estimation de rupture
- 🔵 Surstocks immobilisant du capital
- ⚠️ Articles morts (aucune vente)
- 📈 Variations brutales de ventes

### 💰 Analyses financières avancées

#### 4. **Tableaux de bord complets**
- 💵 Valeur totale du stock (prix d'achat)
- 💰 Valeur de vente potentielle
- 📊 Marge potentielle et taux de marge moyen
- 🔄 Rotation des stocks (turnover)
- 💎 Coût de stockage (immobilisation)

#### 5. **Statistiques par catégorie**
- Répartition par type d'articles
- Catégorie la plus rentable
- Catégorie la plus active
- Performance par fournisseur

#### 6. **Analyse ABC (Pareto)**
- **A** : 20% des articles = 80% de la valeur
- **B** : 30% des articles = 15% de la valeur
- **C** : 50% des articles = 5% de la valeur

### 📦 Réapprovisionnement semi-automatique

#### 7. **Recommandations intelligentes**
- Calcul automatique des quantités à commander
- Priorisation par urgence :
  - 🔴 **Critique** : Rupture imminent
  - 🟠 **Élevée** : Sous seuil critique
  - 🟡 **Moyenne** : Approche du seuil
  - 🔵 **Faible** : Préventif
- Suggestion : *"Il reste 3 unités — recommander 17 pour atteindre le stock optimal"*

#### 8. **Bons de commande automatiques**
- Groupement par fournisseur
- Génération de bons au format texte/PDF
- Estimation des coûts
- Export pour envoi direct

### 📊 Visualisation et rapports

#### 9. **Timeline chronologique**
Journal complet des mouvements :
- 📥 Entrées (réapprovisionnements, retours)
- 📤 Sorties (ventes, pertes, casse)
- ✏️ Corrections d'inventaire
- 📋 Inventaires physiques

Avec statistiques :
- Mouvements par jour
- Solde des quantités
- Recherche dans l'historique

#### 10. **Export HTML professionnel**
Rapports avancés avec :
- 📊 Graphiques intégrés (PNG)
- 🎨 Signalements visuels par couleur :
  - 🔴 Stock faible
  - 🟠 Stock moyen
  - 🟢 Stock bon
- 📋 Tableaux triables
- 💾 Export PDF (via navigateur)

### 🔮 Simulations de scénarios

#### 11. **Scénarios What-If**
Simule l'impact de :
- 📈 Augmentation des ventes (+20%, +50%)
- 📉 Baisse des ventes (-20%, -30%)
- 💰 Variation des prix de vente
- 📦 Modification des délais de livraison
- 🔴 Ruptures prolongées

**Exemple** : *"Que se passe-t-il si les ventes augmentent de 20% ?"*

Comparaison automatique :
- Chiffre d'affaires projeté
- Marge potentielle
- Nombre de ruptures
- Coût de stockage
- **Score global** sur 100

---

## 🚀 Installation et démarrage

### Prérequis
```bash
- Python 3.8+
- tkinter (interface graphique, inclus par défaut)
```

### Lancement rapide

#### 1. **Démonstration complète**
```bash
python stockflow_demo.py
```
Affiche une démonstration de toutes les fonctionnalités avec des données d'exemple.

#### 2. **Interface graphique** (bientôt disponible)
```bash
python stockflow_gui.py
```

#### 3. **Utilisation en code**
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
    motif="vente"
)

# Obtenir des prévisions
predictions = PredictionEngine(inventaire)
prevision = predictions.prevoir_ventes(article.id)
print(f"Ventes prévues : {prevision.ventes_mois_prevue} unités/mois")

# Détecter les anomalies
anomalies = predictions.detecter_anomalies()
for anom in anomalies:
    print(f"⚠️ {anom.article_nom} : {anom.message}")

# Générer des recommandations de réappro
from projectflow.restocking import RestockingEngine
reappro = RestockingEngine(inventaire, predictions)
recommandations = reappro.generer_recommandations()
for reco in recommandations:
    print(f"📦 Commander {reco.quantite_recommandee} × {reco.article_nom}")
```

---

## 📚 Architecture des modules

| Module | Description | Fonctionnalités clés |
|--------|-------------|---------------------|
| `stock.py` | Gestion inventaire | Articles, mouvements, catégories |
| `predictions.py` | Prévisions | Seuils auto, tendances, anomalies |
| `analytics.py` | Analyses financières | Valeur, marge, rotation, ABC |
| `restocking.py` | Réapprovisionnement | Recommandations, bons de commande |
| `timeline.py` | Journal chronologique | Historique, recherche, export |
| `scenarios.py` | Simulations | What-If, comparaisons |
| `themes.py` | Interface | 8 thèmes personnalisables |
| `charts.py` | Graphiques | Courbes, camemberts, barres |
| `export_html.py` | Exports | Rapports HTML professionnels |

---

## 📊 Exemples de rapports

### Rapport financier
```
===============================================================================
                   TABLEAU DE BORD FINANCIER
===============================================================================

📊 VUE D'ENSEMBLE
----------------------------------------------------------------------
Articles totaux:          25
Articles actifs:          23
Articles en rupture:      2 🔴
Articles critiques:       5 🟠

💰 VALEURS
----------------------------------------------------------------------
Valeur stock (achat):     145,680.00 €
Valeur vente potentielle: 198,450.00 €
Marge potentielle:        52,770.00 € (36.2%)

🔄 ROTATION DES STOCKS
----------------------------------------------------------------------
Rotation moyenne:         8.45 fois/an
Rotation rapide (>12):    3 articles
Rotation lente (<4):      7 articles
```

### Recommandations de réapprovisionnement
```
===============================================================================
              RAPPORT DE RÉAPPROVISIONNEMENT
===============================================================================

🔴 CRITIQUE (2 article(s))
----------------------------------------------------------------------

📦 Samsung Galaxy S24 (SAMSUNG-S24)
   Stock actuel:  0 (seuil: 8)
   À commander:   25 unités
   Coût estimé:   18,750.00 €
   Fournisseur:   Samsung Distribution (délai: 4j)
   ⚠️  Rupture dans: 0 jours
   Raison:        Rupture de stock

🟠 ELEVEE (3 article(s))
----------------------------------------------------------------------
[...]
```

---

## 🎯 Cas d'usage

### E-commerce
- Gestion multi-références
- Alertes de rupture automatiques
- Optimisation des commandes fournisseurs

### Boutique physique
- Inventaire en temps réel
- Prévisions saisonnières
- Réduction du surstock

### Distribution / Grossiste
- Analyse ABC pour prioriser
- Rotation optimale du stock
- Réduction des coûts de stockage

### Startup / PME
- Dashboard financier complet
- Décisions basées sur les données
- Simulations avant investissement

---

## 🔧 Configuration avancée

### Catégories personnalisées
```python
from projectflow.stock import CATEGORIES_ARTICLES

# Ajouter une catégorie
CATEGORIES_ARTICLES["bio"] = {
    "nom": "Produits Bio",
    "icone": "🌱",
    "couleur": "#22c55e"
}
```

### Seuils intelligents
```python
# Marge de sécurité par défaut : 1.5
# (seuil = ventes/jour × délai × 1.5)

predictions = PredictionEngine(inventaire)
seuil = predictions.calculer_seuil_automatique(
    article_id="...",
    marge_securite=2.0  # Plus prudent
)
```

### Export CSV de la timeline
```python
from projectflow.timeline import TimelineManager

timeline = TimelineManager(inventaire)
timeline.exporter_csv("mouvements_30j.csv", jours=30)
```

---

## 📈 Indicateurs clés de performance (KPI)

StockFlow calcule automatiquement :

| KPI | Description | Formule |
|-----|-------------|---------|
| **Taux de marge** | Rentabilité moyenne | (Marge / CA) × 100 |
| **Rotation** | Vitesse d'écoulement | Ventes annuelles / Stock moyen |
| **Taux de service** | Disponibilité | (1 - Ruptures/Demandes) × 100 |
| **Couverture stock** | Autonomie en jours | Stock / Ventes moyennes jour |
| **Stock mort** | Articles immobilisés | Articles sans vente > 90j |

---

## 🌟 Fonctionnalités avancées

### Formule de Wilson (EOQ)
Quantité économique de commande :
```python
qte_optimale = restocking.calculer_quantite_optimale(
    article_id="...",
    methode="eoq"  # Economic Order Quantity
)
```

### Analyse d'impact de rupture
```python
from projectflow.scenarios import ScenarioEngine

scenario_engine = ScenarioEngine(inventaire, predictions)
impact = scenario_engine.analyser_impact_rupture(
    article_id="...",
    duree_jours=15
)

print(f"CA perdu : {impact['ca_perdu']:,.2f} €")
print(f"Sévérité : {impact['severite']}")
```

---

## 📝 Documentation technique

Pour plus de détails, consultez :
- 📘 **[Architecture détaillée](docs/architecture.md)**
- 🔍 **[Guide des modules](docs/modules.md)**
- 💡 **[Exemples avancés](docs/exemples.md)**

---

## 🎨 Thèmes disponibles

8 thèmes modernes pour l'interface :

| Thème | Description |
|-------|-------------|
| 🌙 Dark | Sombre élégant (défaut) |
| ☀️ Light | Clair et lumineux |
| 🌌 Midnight | Noir profond |
| 🌊 Ocean | Bleu océan |
| 🌅 Sunset | Violet/rose |
| 🌲 Forest | Vert nature |
| ❄️ Nord | Style nordique |
| 🌸 Rose | Rose pastel |

---

## 🤝 Contribution

Projet NSI réalisé par : [Votre Nom]

Évolutions futures prévues :
- [ ] Interface graphique complète (Tkinter)
- [ ] Connexion base de données (SQLite)
- [ ] API REST pour intégration
- [ ] Application mobile (Flutter/React Native)
- [ ] ML pour prévisions avancées
- [ ] Gestion multi-entrepôts
- [ ] Codes-barres / QR codes

---

## 📄 Licence

Projet éducatif NSI - Libre d'utilisation

---

## 🙏 Remerciements

- Inspiration : Systèmes ERP professionnels
- Framework : Python + Tkinter
- Concepts : Data Science, Analyse de Pareto, Formule de Wilson

---

**StockFlow Pro** - Transformez votre gestion de stock en avantage compétitif ! 🚀
