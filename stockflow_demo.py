"""
StockFlow Pro - Démonstration des fonctionnalités

Ce script démontre toutes les capacités de StockFlow :
1. Gestion d'inventaire
2. Prévisions automatiques
3. Détection d'anomalies
4. Analyses financières
5. Réapprovisionnement intelligent
6. Timeline des mouvements
7. Simulations de scénarios
"""

from projectflow.stock import Inventaire, Article, Mouvement, CATEGORIES_ARTICLES
from projectflow.predictions import PredictionEngine
from projectflow.analytics import AnalyticsEngine
from projectflow.restocking import RestockingEngine
from projectflow.timeline import TimelineManager
from projectflow.scenarios import ScenarioEngine, Scenario
from datetime import datetime, timedelta


def demo_complete():
    """Démonstration complète de StockFlow."""

    print("\n" + "=" * 80)
    print("                  🚀 STOCKFLOW PRO - DÉMONSTRATION")
    print("=" * 80 + "\n")

    # ===== 1. CRÉATION DE L'INVENTAIRE =====
    print("📦 1. CRÉATION DE L'INVENTAIRE\n")
    print("-" * 80)

    inventaire = Inventaire(nom="Boutique High-Tech")

    # Créer des articles d'exemple
    articles_demo = [
        Article(
            nom="MacBook Pro 16\"",
            reference="APPLE-MBP-16",
            categorie="electronique",
            quantite=8,
            seuil_min=3,
            stock_optimal=15,
            prix_achat=2200,
            prix_vente=2899,
            fournisseur="Apple France",
            delai_reappro_jours=7,
            ventes_jour=0.8
        ),
        Article(
            nom="iPhone 15 Pro",
            reference="APPLE-IP15PRO",
            categorie="electronique",
            quantite=25,
            seuil_min=10,
            stock_optimal=40,
            prix_achat=950,
            prix_vente=1329,
            fournisseur="Apple France",
            delai_reappro_jours=5,
            ventes_jour=2.5
        ),
        Article(
            nom="AirPods Pro 2",
            reference="APPLE-APP2",
            categorie="electronique",
            quantite=2,  # Stock critique !
            seuil_min=15,
            stock_optimal=50,
            prix_achat=210,
            prix_vente=279,
            fournisseur="Apple France",
            delai_reappro_jours=3,
            ventes_jour=3.2
        ),
        Article(
            nom="Samsung Galaxy S24",
            reference="SAMSUNG-S24",
            categorie="electronique",
            quantite=0,  # Rupture !
            seuil_min=8,
            stock_optimal=25,
            prix_achat=750,
            prix_vente=999,
            fournisseur="Samsung Distribution",
            delai_reappro_jours=4,
            ventes_jour=1.5
        ),
        Article(
            nom="Logitech MX Master 3",
            reference="LOGI-MX3",
            categorie="electronique",
            quantite=45,
            seuil_min=10,
            stock_optimal=30,
            prix_achat=75,
            prix_vente=119,
            fournisseur="Logitech",
            delai_reappro_jours=2,
            ventes_jour=0.5
        ),
    ]

    for article in articles_demo:
        inventaire.ajouter_article(article)

    print(f"✅ Inventaire créé : {len(inventaire.articles)} articles")
    for article in inventaire.articles:
        statut_icone = {
            "rupture": "🔴",
            "critique": "🟠",
            "faible": "🟡",
            "bon": "🟢",
            "surstock": "🔵"
        }
        print(f"   {statut_icone.get(article.statut_stock, '⚪')} {article.nom} : {article.quantite} unités ({article.statut_stock})")

    # Simuler quelques mouvements
    print("\n📊 Simulation de mouvements...")
    for i in range(10):
        # Ventes aléatoires
        import random
        article = random.choice(inventaire.articles)
        if article.quantite > 0:
            qte = min(article.quantite, random.randint(1, 3))
            try:
                inventaire.retirer_stock(
                    article.id,
                    qte,
                    prix_unitaire=article.prix_vente,
                    motif="vente"
                )
            except:
                pass

    print(f"✅ {len(inventaire.mouvements)} mouvements enregistrés\n")


    # ===== 2. PRÉVISIONS ET ANOMALIES =====
    print("\n🔮 2. PRÉVISIONS ET DÉTECTION D'ANOMALIES\n")
    print("-" * 80)

    prediction_engine = PredictionEngine(inventaire)

    # Mettre à jour les statistiques
    prediction_engine.mettre_a_jour_tous_les_articles()

    # Détecter les anomalies
    anomalies = prediction_engine.detecter_anomalies()
    print(f"⚠️  {len(anomalies)} anomalie(s) détectée(s):\n")

    for anom in anomalies[:5]:
        icones_sev = {
            "critique": "🔴",
            "elevee": "🟠",
            "moyenne": "🟡",
            "faible": "🔵"
        }
        print(f"{icones_sev.get(anom.severite, '⚪')} {anom.article_nom}")
        print(f"   {anom.message}")
        print(f"   Type: {anom.type}\n")

    # Prévisions
    print("\n📈 Prévisions pour quelques articles:\n")
    for article in inventaire.articles[:3]:
        prev = prediction_engine.prevoir_ventes(article.id)
        if prev:
            fleche = "📈" if prev.tendance == "hausse" else "📉" if prev.tendance == "baisse" else "➡️"
            print(f"{fleche} {article.nom}")
            print(f"   Ventes/jour: {prev.ventes_jour_moyenne:.2f}")
            print(f"   Prévision mois: {prev.ventes_mois_prevue:.0f} unités")
            print(f"   Tendance: {prev.tendance} ({prev.tendance_pourcentage:+.1f}%)")
            print(f"   Confiance: {prev.confiance:.0f}%\n")


    # ===== 3. ANALYSES FINANCIÈRES =====
    print("\n💰 3. ANALYSES FINANCIÈRES\n")
    print("-" * 80)

    analytics_engine = AnalyticsEngine(inventaire)

    # Rapport financier
    rapport = analytics_engine.generer_rapport_financier()

    print(f"Valeur stock:           {rapport.valeur_stock_total:>12,.2f} €")
    print(f"Valeur vente:           {rapport.valeur_vente_potentielle:>12,.2f} €")
    print(f"Marge potentielle:      {rapport.marge_potentielle:>12,.2f} € ({rapport.taux_marge_moyen:.1f}%)\n")

    print(f"Articles:               {rapport.nombre_articles}")
    print(f"En rupture:             {rapport.articles_en_rupture} 🔴")
    print(f"Critiques:              {rapport.articles_critiques} 🟠\n")

    print(f"Rotation moyenne:       {rapport.rotation_moyenne:.2f} fois/an")
    print(f"Rotation rapide (>12):  {rapport.articles_rotation_rapide}")
    print(f"Rotation lente (<4):    {rapport.articles_rotation_lente}\n")

    # Top 3
    print("🏆 TOP 3 - Valeur stock:")
    for i, art in enumerate(rapport.top_articles_valeur[:3], 1):
        print(f"   {i}. {art['nom'][:40]:40} {art['valeur']:>10,.2f} €")

    print("\n💎 TOP 3 - Marge potentielle:")
    for i, art in enumerate(rapport.top_articles_marge[:3], 1):
        print(f"   {i}. {art['nom'][:40]:40} {art['marge_totale']:>10,.2f} €")


    # ===== 4. RÉAPPROVISIONNEMENT =====
    print("\n\n📦 4. RÉAPPROVISIONNEMENT INTELLIGENT\n")
    print("-" * 80)

    restocking_engine = RestockingEngine(inventaire, prediction_engine)

    # Recommandations
    recommandations = restocking_engine.generer_recommandations(inclure_preventif=False)

    print(f"📋 {len(recommandations)} recommandation(s) de réapprovisionnement:\n")

    icones_urgence = {
        "CRITIQUE": "🔴",
        "ELEVEE": "🟠",
        "MOYENNE": "🟡",
        "FAIBLE": "🔵"
    }

    for reco in recommandations[:5]:
        print(f"{icones_urgence.get(reco.urgence.name, '⚪')} {reco.article_nom}")
        print(f"   Stock: {reco.quantite_actuelle} (seuil: {reco.seuil_critique})")
        print(f"   À commander: {reco.quantite_recommandee} unités")
        print(f"   Coût: {reco.cout_estime:,.2f} €")
        print(f"   Fournisseur: {reco.fournisseur}")
        if reco.jours_avant_rupture:
            print(f"   ⚠️  Rupture dans {reco.jours_avant_rupture} jours")
        print()

    # Bons de commande
    print("\n📝 Génération des bons de commande (groupés par fournisseur):\n")
    bons = restocking_engine.generer_bons_commande(recommandations)

    for bon in bons:
        print(f"BC N° {bon.numero}")
        print(f"Fournisseur: {bon.fournisseur}")
        print(f"Articles: {len(bon.articles)}")
        print(f"Quantité totale: {bon.total_quantite}")
        print(f"Coût total: {bon.total_cout:,.2f} €")
        print(f"Urgence: {icones_urgence.get(bon.urgence_max.name, '⚪')} {bon.urgence_max.name}\n")


    # ===== 5. TIMELINE =====
    print("\n📅 5. TIMELINE DES MOUVEMENTS\n")
    print("-" * 80)

    timeline_manager = TimelineManager(inventaire)

    # Statistiques
    stats = timeline_manager.calculer_statistiques_mouvements(jours=30)
    print(f"Mouvements (30 derniers jours): {stats['total_mouvements']}")
    print(f"Moyenne/jour: {stats['mouvements_par_jour']:.1f}")
    print(f"Entrées: {stats['par_type']['entree']} ({stats['total_entrees_quantite']} unités)")
    print(f"Sorties: {stats['par_type']['sortie']} ({stats['total_sorties_quantite']} unités)")
    print(f"Solde: {stats['solde_quantite']:+} unités\n")

    # Derniers mouvements
    print("🕒 5 derniers mouvements:\n")
    entrees = timeline_manager.obtenir_timeline(limite=5)
    for entree in entrees:
        print(f"{entree.icone} {entree.article_nom}")
        print(f"   Qté: {'+' if entree.type == 'entree' else '-'}{entree.quantite}")
        print(f"   Motif: {entree.motif}")
        print(f"   Date: {entree.date_complete}\n")


    # ===== 6. SIMULATIONS DE SCÉNARIOS =====
    print("\n🔮 6. SIMULATIONS DE SCÉNARIOS\n")
    print("-" * 80)

    scenario_engine = ScenarioEngine(inventaire, prediction_engine)

    # Scénarios prédéfinis
    scenarios = scenario_engine.generer_scenarios_predéfinis()

    print(f"📊 Simulation de {len(scenarios)} scénarios sur 90 jours...\n")

    # Comparer les 3 premiers scénarios
    resultats = scenario_engine.comparer_scenarios(scenarios[:3], duree_jours=90)

    print(f"🏆 RÉSULTATS (triés par score):\n")
    for i, resultat in enumerate(resultats, 1):
        medaille = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        print(f"{medaille} {resultat.scenario.nom}")
        print(f"   Score: {resultat.score_global:.1f}/100")
        print(f"   CA: {resultat.chiffre_affaires_total:,.2f} €")
        print(f"   Marge: {resultat.marge_totale:,.2f} € ({resultat.taux_marge_moyen:.1f}%)")
        print(f"   Ruptures: {resultat.ruptures_count} fois ({resultat.jours_rupture_total} jours)")
        print(f"   Ventes perdues: {resultat.ventes_perdues:,.2f} €\n")


    # ===== 7. ANALYSE ABC =====
    print("\n📊 7. ANALYSE ABC (PARETO)\n")
    print("-" * 80)

    abc = analytics_engine.calculer_abc_analysis()

    print(f"Catégorie A (80% valeur): {len(abc['A'])} articles")
    print(f"Catégorie B (15% valeur): {len(abc['B'])} articles")
    print(f"Catégorie C (5% valeur):  {len(abc['C'])} articles\n")

    if abc['A']:
        print("🔴 Articles catégorie A (prioritaires):")
        for art in abc['A'][:3]:
            print(f"   • {art['nom']}: {art['valeur_stock']:,.2f} €")


    # ===== RÉSUMÉ FINAL =====
    print("\n\n" + "=" * 80)
    print("                         ✅ DÉMONSTRATION TERMINÉE")
    print("=" * 80)
    print("\n🎯 FONCTIONNALITÉS DÉMONTRÉES:\n")
    print("  1. ✅ Gestion d'inventaire multi-articles")
    print("  2. ✅ Seuils automatiques intelligents")
    print("  3. ✅ Prévisions de ventes (moyenne glissante, tendance)")
    print("  4. ✅ Détection d'anomalies (ruptures, surstocks, variations)")
    print("  5. ✅ Analyses financières (valeur, marge, rotation)")
    print("  6. ✅ Réapprovisionnement semi-automatique")
    print("  7. ✅ Catégories intelligentes avec statistiques")
    print("  8. ✅ Timeline chronologique des mouvements")
    print("  9. ✅ Simulations de scénarios What-If")
    print(" 10. ✅ Analyse ABC (Pareto)")
    print("\n" + "=" * 80 + "\n")

    return inventaire


if __name__ == "__main__":
    inventaire = demo_complete()

    print("\n💡 POUR ALLER PLUS LOIN:")
    print("\n1. Interface graphique (GUI):")
    print("   python stockflow_gui.py")
    print("\n2. Export HTML:")
    print("   Utilisez les fonctions d'export pour générer des rapports HTML")
    print("\n3. Sauvegarde:")
    print("   inventaire.to_dict() pour sauvegarder en JSON")
    print("\n" + "=" * 80 + "\n")
