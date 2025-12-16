# 🚀 StockFlow Pro - Lancement Rapide

## Démarrage immédiat

### Option 1 : Interface Graphique (RECOMMANDÉ)
```bash
python3 stockflow_gui.py
```

### Option 2 : Démonstration Console
```bash
python3 stockflow_demo.py
```

---

## 📦 Interface Graphique - Guide Rapide

L'interface est divisée en **9 sections principales** :

### 1. 📊 **Dashboard**
- Vue d'ensemble de votre inventaire
- KPIs en temps réel (Articles, Valeur, Ruptures, Marge)
- Anomalies détectées automatiquement
- Articles récents

### 2. 📦 **Articles**
- Liste complète de tous vos articles
- **Ajouter** : Bouton "➕ Nouvel Article"
- **Vendre** : Bouton "📤 Vente" sur chaque article
- **Réapprovisionner** : Bouton "📥 Entrée" sur chaque article
- Informations détaillées (stock, seuil, prix, marge, valeur)

### 3. 📝 **Mouvements**
- Journal de tous les mouvements (entrées/sorties)
- Statistiques sur 30 jours
- Historique complet avec dates et quantités

### 4. 🔮 **Prévisions**
- **Anomalies détectées** automatiquement :
  - 🔴 Critique : Ruptures, stocks négatifs
  - 🟠 Élevée : Stocks sous seuil
  - 🟡 Moyenne : Surstocks, variations
  - 🔵 Faible : Articles inactifs
- **Prévisions de ventes** :
  - Tendance (📈 hausse, 📉 baisse, ➡️ stable)
  - Estimation mensuelle
  - Niveau de confiance

### 5. 💰 **Analyses**
- **KPIs financiers** :
  - Valeur stock totale
  - Valeur de vente potentielle
  - Marge potentielle
  - Taux de marge moyen
- **Top 5 articles** par valeur
- Classement avec médailles 🥇🥈🥉

### 6. 🚚 **Réapprovisionnement**
- **Recommandations automatiques** :
  - 🔴 **CRITIQUE** : Commande urgente
  - 🟠 **ÉLEVÉE** : À commander rapidement
  - 🟡 **MOYENNE** : Planifier
  - 🔵 **FAIBLE** : Préventif
- Quantités calculées automatiquement
- Coût estimé par commande
- Fournisseur et délai

### 7. 📅 **Timeline**
- Historique chronologique complet
- Filtres et recherche
- Export CSV disponible

### 8. 🎯 **Scénarios**
- **Simulations What-If** :
  - Ventes +20% / -20%
  - Prix +10%
  - Coûts +15%
  - Délais +5 jours
- Comparaison automatique
- Score global sur 100
- Impact sur CA, marge, ruptures

### 9. ⚙️ **Réglages**
- Sauvegarde manuelle
- Export CSV de la timeline
- Actualisation des statistiques

---

## 🎯 Actions Rapides

### Ajouter un article
1. Cliquer sur "📦 Articles" (sidebar)
2. Cliquer sur "➕ Nouvel Article" (en haut à droite)
3. Remplir le formulaire
4. Cliquer sur "✅ Créer"

### Vendre un article
1. Aller dans "📦 Articles"
2. Trouver votre article
3. Cliquer sur "📤 Vente"
4. Entrer la quantité
5. OK !

### Réapprovisionner
1. Aller dans "📦 Articles"
2. Trouver votre article
3. Cliquer sur "📥 Entrée"
4. Entrer la quantité reçue
5. OK !

### Voir les anomalies
1. Cliquer sur "🔮 Prévisions" (sidebar)
2. Liste complète des anomalies détectées
3. Gravité indiquée par couleur 🔴🟠🟡🔵

### Obtenir des recommandations
1. Cliquer sur "🚚 Réappro" (sidebar)
2. Voir toutes les recommandations
3. Articles triés par urgence

### Simuler des scénarios
1. Cliquer sur "🎯 Scénarios" (sidebar)
2. Cliquer sur "▶️  Lancer la Simulation"
3. Attendre quelques secondes
4. Comparer les résultats avec scores

---

## 🎨 Personnalisation

### Thèmes disponibles (Section Réglages)
- 🌙 Dark (par défaut)
- ☀️ Light
- 🌌 Midnight
- 🌊 Ocean
- 🌅 Sunset
- 🌲 Forest
- ❄️ Nord
- 🌸 Rose

---

## 💾 Sauvegarde Automatique

L'inventaire est **sauvegardé automatiquement** après chaque action :
- Ajout d'article
- Vente
- Entrée de stock
- Modification

**Fichier** : `stockflow_inventaire.json`

---

## 📊 Données d'Exemple

Au premier lancement, 3 articles d'exemple sont créés :
- MacBook Pro 16" (stock: 8)
- iPhone 15 Pro (stock: 25)
- AirPods Pro 2 (stock: 2, **CRITIQUE** ⚠️)

Vous pouvez :
- Les modifier
- Les supprimer
- Ajouter vos propres articles

---

## 🐛 Résolution de Problèmes

### L'interface ne s'affiche pas
```bash
# Vérifier tkinter
python3 -c "import tkinter; print('Tkinter OK')"
```

### Erreur au lancement
```bash
# Vérifier les dépendances
python3 -c "from projectflow import stock, predictions, analytics; print('Modules OK')"
```

### Reset complet
```bash
# Supprimer l'inventaire et recommencer
rm stockflow_inventaire.json
python3 stockflow_gui.py
```

---

## 📝 Notes Importantes

1. **Statuts des articles** (couleurs automatiques) :
   - 🔴 **Rupture** : Stock = 0
   - 🟠 **Critique** : Stock ≤ Seuil
   - 🟡 **Faible** : Stock ≤ Seuil × 2
   - 🟢 **Bon** : Stock OK
   - 🔵 **Surstock** : Stock > Optimal × 1.2

2. **Seuils automatiques** calculés par :
   - Formule : `Ventes/jour × Délai réappro × Marge sécurité`
   - Mise à jour automatique

3. **Prévisions** basées sur :
   - 30 derniers jours
   - Moyenne glissante
   - Détection de tendance

4. **Scénarios** simulent :
   - 90 jours
   - Impact financier complet
   - Score de 0 à 100

---

## 🚀 Pour Aller Plus Loin

### Export des données
```bash
# Dans Réglages → Export CSV
# Ou via code :
from projectflow.timeline import TimelineManager
timeline = TimelineManager(inventaire)
timeline.exporter_csv("export.csv", jours=90)
```

### Rapports HTML
```python
# À venir : Export HTML professionnel avec graphiques
```

### API Python
```python
from projectflow.stock import Inventaire, Article
from projectflow.predictions import PredictionEngine

# Charger
inv = Inventaire.from_dict(json.load(open("stockflow_inventaire.json")))

# Analyser
pred = PredictionEngine(inv)
anomalies = pred.detecter_anomalies()

# Afficher
for anom in anomalies:
    print(f"{anom.article_nom}: {anom.message}")
```

---

**StockFlow Pro** - Gestion de stock intelligente 🚀
