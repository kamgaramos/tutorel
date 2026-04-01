# app.py (version corrigée)
from flask import Flask, render_template, jsonify, request, send_file
import json
import os
from datetime import datetime, timedelta

# Import des modules de configuration
from config import NOM_BAR, DEVISE

# Import des routes (blueprints)
from routes.produits import produits_bp
from routes.ventes import ventes_bp
from routes.stocks import stocks_bp
from routes.appro import appro_bp
from routes.ml import ml_bp
from routes.dashboard import dashboard_bp
from routes.rapports import rapports_bp

# Création de l'application Flask
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

app.config['SECRET_KEY'] = 'bar-camerounais-secret-key-2024'
app.config['NOM_BAR'] = NOM_BAR
app.config['DEVISE'] = DEVISE

# Enregistrement des blueprints (avec ou sans préfixe)
app.register_blueprint(produits_bp, url_prefix='/api/produits')
app.register_blueprint(ventes_bp, url_prefix='/api/ventes')
app.register_blueprint(stocks_bp, url_prefix='/api/stocks')
app.register_blueprint(appro_bp, url_prefix='/api/appro')
app.register_blueprint(ml_bp, url_prefix='/api/ml')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(rapports_bp, url_prefix='/api/rapports')

# ========== ROUTES PAGES ==========

@app.route('/')
def index():
    """Page d'accueil / Dashboard principal"""
    return render_template('index.html', 
                         nom_bar=NOM_BAR,
                         devise=DEVISE,
                         annee=datetime.now().year)

@app.route('/produits')
def produits_page():
    """Page de gestion des produits"""
    return render_template('produits.html',
                         nom_bar=NOM_BAR,
                         devise=DEVISE)

@app.route('/caisse')
def caisse_page():
    """Page de caisse / enregistrement des ventes"""
    return render_template('caisse.html',
                         nom_bar=NOM_BAR,
                         devise=DEVISE)

@app.route('/stocks')
def stocks_page():
    """Page de gestion des stocks"""
    return render_template('stocks.html',
                         nom_bar=NOM_BAR,
                         devise=DEVISE)

@app.route('/appro')
def appro_page():
    """Page d'approvisionnement"""
    return render_template('appro.html',
                         nom_bar=NOM_BAR,
                         devise=DEVISE)

@app.route('/tendances')
def tendances_page():
    """Page des tendances et ML"""
    return render_template('tendances.html',
                         nom_bar=NOM_BAR,
                         devise=DEVISE)

@app.route('/bilan')
def bilan_page():
    """Page de bilan financier"""
    return render_template('bilan.html',
                         nom_bar=NOM_BAR,
                         devise=DEVISE)

@app.route('/rapport')
def rapport_page():
    """Page de rapport journalier"""
    return render_template('rapport.html',
                         nom_bar=NOM_BAR,
                         devise=DEVISE)

# ========== ROUTE DE TEST API ==========

@app.route('/api/test')
def test_api():
    """Route simple pour tester que l'API fonctionne"""
    return jsonify({
        'success': True,
        'message': 'API fonctionne correctement',
        'time': datetime.now().isoformat()
    })

# ========== MIDDLEWARE ==========

@app.after_request
def add_header(response):
    """Ajoute des headers pour éviter le cache en développement"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# ========== GESTION DES ERREURS ==========

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'success': False, 'message': 'Page non trouvée'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'success': False, 'message': 'Erreur interne du serveur'}), 500

# ========== LANCEMENT ==========

if __name__ == '__main__':
    print(f"""
     {NOM_BAR} - Dashboard de Gestion
    ===================================
    Interface: http://localhost:5000
    Test API:  http://localhost:5000/api/test
    Base: data/bar.sqlite
    ===================================
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)