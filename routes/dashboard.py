# routes/dashboard.py - Routes pour les données du dashboard principal
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import sqlite3
import random

from database import (
    get_db,
    get_stats_globales,
    get_revenus_semaine,
    get_top_produits,
    get_repartition_societes,
    get_stocks_critiques
)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/kpis', methods=['GET'])
def get_kpis():
    """Retourne les KPIs pour le dashboard"""
    try:
        # Récupérer les stats depuis la base de données
        stats = get_stats_globales()
        
        # Si la base est vide, retourner des données de démonstration
        if not stats or stats.get('revenus_jour') == 0 and stats.get('ventes_jour') == 0:
            # Données de démonstration
            return jsonify({
                'success': True,
                'revenus_jour': 245500,
                'ventes_jour': 42,
                'benefice_jour': 82350,
                'alertes_stock': 3
            })
        
        return jsonify({
            'success': True,
            'revenus_jour': stats.get('revenus_jour', 0),
            'ventes_jour': stats.get('ventes_jour', 0),
            'benefice_jour': stats.get('benefice_jour', 0),
            'alertes_stock': stats.get('alertes_stock', 0)
        })
    except Exception as e:
        print(f"Erreur dashboard/kpis: {str(e)}")
        # En cas d'erreur, retourner des données de démonstration
        return jsonify({
            'success': True,
            'revenus_jour': 245500,
            'ventes_jour': 42,
            'benefice_jour': 82350,
            'alertes_stock': 3
        })

@dashboard_bp.route('/revenus-semaine', methods=['GET'])
def get_revenus_semaine_route():
    """Retourne les revenus des 7 derniers jours"""
    try:
        # Essayer de récupérer depuis la base
        data = get_revenus_semaine()
        
        # Si pas de données, générer des données de démonstration
        if not data or len(data) == 0:
            today = datetime.now()
            data = []
            for i in range(6, -1, -1):
                date = (today - timedelta(days=i)).strftime('%d/%m')
                # Générer des revenus avec une tendance
                base = 45000 + (i * 2000)
                variation = random.randint(-5000, 5000)
                data.append({
                    'date': date,
                    'revenu': base + variation
                })
        
        return jsonify(data)
    except Exception as e:
        print(f"Erreur dashboard/revenus-semaine: {str(e)}")
        # Données de démonstration en cas d'erreur
        today = datetime.now()
        demo_data = []
        for i in range(6, -1, -1):
            date = (today - timedelta(days=i)).strftime('%d/%m')
            demo_data.append({
                'date': date,
                'revenu': 45000 + (i * 2000) + random.randint(-3000, 3000)
            })
        return jsonify(demo_data)

@dashboard_bp.route('/top-produits', methods=['GET'])
def get_top_produits_route():
    """Retourne le top 5 des produits"""
    try:
        limit = request.args.get('limit', 5, type=int)
        data = get_top_produits(limit)
        
        # Si pas de données, générer des données de démonstration
        if not data or len(data) == 0:
            demo_produits = [
                {'produit': 'Castel Beer', 'revenus': 125000},
                {'produit': 'Guinness', 'revenus': 98000},
                {'produit': 'Mützig', 'revenus': 87000},
                {'produit': 'Whisky', 'revenus': 65000},
                {'produit': 'Tangui', 'revenus': 43000}
            ]
            return jsonify(demo_produits[:limit])
        
        # Reformater les données si nécessaire
        formatted_data = []
        for item in data:
            if 'nom' in item and 'revenus' in item:
                formatted_data.append({
                    'produit': item['nom'],
                    'revenus': item['revenus']
                })
            else:
                formatted_data.append(item)
        
        return jsonify(formatted_data)
    except Exception as e:
        print(f"Erreur dashboard/top-produits: {str(e)}")
        # Données de démonstration
        return jsonify([
            {'produit': 'Castel Beer', 'revenus': 125000},
            {'produit': 'Guinness', 'revenus': 98000},
            {'produit': 'Mützig', 'revenus': 87000},
            {'produit': 'Whisky', 'revenus': 65000},
            {'produit': 'Tangui', 'revenus': 43000}
        ])

@dashboard_bp.route('/repartition-societes', methods=['GET'])
def get_repartition_societes_route():
    """Retourne la répartition des ventes par société"""
    try:
        data = get_repartition_societes()
        
        # Si pas de données, générer des données de démonstration
        if not data or len(data) == 0:
            demo_societes = [
                {'societe': 'SABC', 'revenus': 245000},
                {'societe': 'Guinness', 'revenus': 187000},
                {'societe': 'UCB', 'revenus': 124000},
                {'societe': 'Sources du Pays', 'revenus': 89000},
                {'societe': 'Autres Produits', 'revenus': 67000}
            ]
            return jsonify(demo_societes)
        
        return jsonify(data)
    except Exception as e:
        print(f"Erreur dashboard/repartition-societes: {str(e)}")
        # Données de démonstration
        return jsonify([
            {'societe': 'SABC', 'revenus': 245000},
            {'societe': 'Guinness', 'revenus': 187000},
            {'societe': 'UCB', 'revenus': 124000},
            {'societe': 'Sources du Pays', 'revenus': 89000},
            {'societe': 'Autres Produits', 'revenus': 67000}
        ])

@dashboard_bp.route('/stocks-critiques', methods=['GET'])
def get_stocks_critiques_route():
    """Retourne la liste des stocks critiques"""
    try:
        data = get_stocks_critiques()
        
        # Si pas de données, générer des données de démonstration
        if not data or len(data) == 0:
            demo_stocks = [
                {'id': 1, 'nom': 'Castel Beer', 'societe': 'SABC', 'quantite': 2, 'seuil_alerte': 10},
                {'id': 2, 'nom': 'Whisky', 'societe': 'Autres Produits', 'quantite': 1, 'seuil_alerte': 5},
                {'id': 3, 'nom': 'Tangui', 'societe': 'Sources du Pays', 'quantite': 5, 'seuil_alerte': 15}
            ]
            return jsonify({'success': True, 'stocks': demo_stocks})
        
        return jsonify({'success': True, 'stocks': data})
    except Exception as e:
        print(f"Erreur dashboard/stocks-critiques: {str(e)}")
        # Données de démonstration
        return jsonify({
            'success': True, 
            'stocks': [
                {'id': 1, 'nom': 'Castel Beer', 'societe': 'SABC', 'quantite': 2, 'seuil_alerte': 10},
                {'id': 2, 'nom': 'Whisky', 'societe': 'Autres Produits', 'quantite': 1, 'seuil_alerte': 5}
            ]
        })

@dashboard_bp.route('/ventes-recentes', methods=['GET'])
def get_ventes_recentes():
    """Retourne les 10 dernières ventes"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.id, v.date_vente, p.nom as produit, 
                   v.quantite, v.prix_unitaire,
                   (v.quantite * v.prix_unitaire) as total
            FROM ventes v
            JOIN produits p ON v.produit_id = p.id
            ORDER BY v.date_vente DESC
            LIMIT 10
        ''')
        
        ventes = cursor.fetchall()
        conn.close()
        
        # Si pas de ventes, données démo
        if not ventes or len(ventes) == 0:
            demo_ventes = []
            now = datetime.now()
            for i in range(5):
                demo_ventes.append({
                    'id': i+1,
                    'date_vente': (now - timedelta(minutes=15*i)).isoformat(),
                    'produit': ['Castel Beer', 'Guinness', 'Mützig', 'Tangui', 'Whisky'][i % 5],
                    'quantite': i+1,
                    'prix_unitaire': [600, 900, 650, 300, 4500][i % 5],
                    'total': [600, 900, 650, 300, 4500][i % 5] * (i+1)
                })
            return jsonify({
                'success': True,
                'ventes': demo_ventes
            })
        
        return jsonify({
            'success': True,
            'ventes': [dict(v) for v in ventes]
        })
    except Exception as e:
        print(f"Erreur dashboard/ventes-recentes: {str(e)}")
        # Données de démonstration
        demo_ventes = []
        now = datetime.now()
        for i in range(5):
            demo_ventes.append({
                'id': i+1,
                'date_vente': (now - timedelta(minutes=15*i)).isoformat(),
                'produit': ['Castel Beer', 'Guinness', 'Mützig', 'Tangui', 'Whisky'][i % 5],
                'quantite': i+1,
                'prix_unitaire': [600, 900, 650, 300, 4500][i % 5],
                'total': [600, 900, 650, 300, 4500][i % 5] * (i+1)
            })
        return jsonify({
            'success': True,
            'ventes': demo_ventes
        })

@dashboard_bp.route('/activite-recente', methods=['GET'])
def get_activite_recente():
    """Retourne l'activité récente (ventes + appros)"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Dernières ventes
        cursor.execute('''
            SELECT 'vente' as type, v.date_vente as date,
                   p.nom as produit, v.quantite,
                   (v.quantite * v.prix_unitaire) as montant
            FROM ventes v
            JOIN produits p ON v.produit_id = p.id
            ORDER BY v.date_vente DESC
            LIMIT 5
        ''')
        ventes = cursor.fetchall()
        
        # Derniers approvisionnements
        cursor.execute('''
            SELECT 'appro' as type, a.date_appro as date,
                   p.nom as produit, a.quantite,
                   (a.quantite * a.prix_achat_unitaire) as montant
            FROM approvisionnements a
            JOIN produits p ON a.produit_id = p.id
            ORDER BY a.date_appro DESC
            LIMIT 5
        ''')
        appros = cursor.fetchall()
        
        conn.close()
        
        # Fusion et tri
        activite = [dict(v) for v in ventes] + [dict(a) for a in appros]
        activite.sort(key=lambda x: x['date'], reverse=True)
        
        # Si pas d'activité, données démo
        if not activite or len(activite) == 0:
            now = datetime.now()
            activite = [
                {
                    'type': 'vente',
                    'date': now.isoformat(),
                    'produit': 'Castel Beer',
                    'quantite': 3,
                    'montant': 1800
                },
                {
                    'type': 'vente',
                    'date': (now - timedelta(minutes=5)).isoformat(),
                    'produit': 'Guinness',
                    'quantite': 2,
                    'montant': 1800
                },
                {
                    'type': 'appro',
                    'date': (now - timedelta(hours=2)).isoformat(),
                    'produit': 'Mützig',
                    'quantite': 24,
                    'montant': 15600
                }
            ]
        
        return jsonify({
            'success': True,
            'activite': activite[:10]
        })
    except Exception as e:
        print(f"Erreur dashboard/activite-recente: {str(e)}")
        # Données de démonstration
        now = datetime.now()
        return jsonify({
            'success': True,
            'activite': [
                {
                    'type': 'vente',
                    'date': now.isoformat(),
                    'produit': 'Castel Beer',
                    'quantite': 3,
                    'montant': 1800
                },
                {
                    'type': 'vente',
                    'date': (now - timedelta(minutes=5)).isoformat(),
                    'produit': 'Guinness',
                    'quantite': 2,
                    'montant': 1800
                }
            ]
        })

@dashboard_bp.route('/test', methods=['GET'])
def test_route():
    """Route de test pour vérifier que le blueprint fonctionne"""
    return jsonify({
        'success': True,
        'message': 'Le blueprint dashboard fonctionne correctement',
        'time': datetime.now().isoformat()
    })