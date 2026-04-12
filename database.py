# database.py - Version corrigée

import sqlite3
import os
from datetime import datetime, timedelta
from config import DB_PATH, SOCIETES, SEUIL_STOCK_DEFAUT

def get_db():
    """Retourne une connexion à la base de données"""
    # Créer le dossier data s'il n'existe pas
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crée toutes les tables si elles n'existent pas"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employe',
            code_pin TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table des paramètres
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametres (
            clef TEXT PRIMARY KEY,
            valeur TEXT
        )
    ''')
    
    # Table des produits - CORRIGÉE : on met la valeur par défaut directement dans SQL
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            societe TEXT NOT NULL,
            prix_achat INTEGER NOT NULL,
            prix_vente INTEGER NOT NULL,
            seuil_alerte INTEGER DEFAULT 10,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des stocks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            produit_id INTEGER PRIMARY KEY,
            quantite INTEGER NOT NULL DEFAULT 0,
            derniere_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produit_id) REFERENCES produits (id) ON DELETE CASCADE
        )
    ''')
    
    # Table des ventes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produit_id INTEGER NOT NULL,
            quantite INTEGER NOT NULL,
            prix_unitaire INTEGER NOT NULL,
            date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produit_id) REFERENCES produits (id)
        )
    ''')
    
    # Table des approvisionnements
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS approvisionnements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produit_id INTEGER NOT NULL,
            quantite INTEGER NOT NULL,
            prix_achat_unitaire INTEGER NOT NULL,
            date_appro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            note TEXT,
            FOREIGN KEY (produit_id) REFERENCES produits (id)
        )
    ''')
    
    # Table des ajustements de stock
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historique_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produit_id INTEGER NOT NULL,
            quantite_avant INTEGER NOT NULL,
            quantite_apres INTEGER NOT NULL,
            type TEXT NOT NULL,
            raison TEXT,
            date_mouvement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produit_id) REFERENCES produits (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    migrate_db()
    
    # Insérer des données de test si la base est vide
    insert_test_data_if_empty()

def migrate_db():
    """Applique les modifications de schéma aux tables existantes"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE ventes ADD COLUMN vendeur_id INTEGER REFERENCES utilisateurs(id)")
        print("Migration: colonne vendeur_id ajoutee a la table ventes.")
    except sqlite3.OperationalError:
        pass  # Colonne déjà existante
    conn.commit()
    conn.close()

def insert_test_data_if_empty():
    """Ajoute des données de test pour le développement"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Vérifier si la table produits est vide
    cursor.execute("SELECT COUNT(*) as count FROM produits")
    count = cursor.fetchone()['count']
    
    if count == 0:
        print("Insertion des donnees de test...")
        
        # Antibiotiques
        produits = [
            ('Amoxicilline 500mg', 'Antibiotiques', 1500, 2500, 20),
            ('Azithromycine 500mg', 'Antibiotiques', 3000, 5000, 10),
            ('Ciprofloxacine 500mg', 'Antibiotiques', 2000, 3500, 15),
            
            # Analgésiques
            ('Paracétamol 500mg', 'Analgésiques', 200, 500, 50),
            ('Ibuprofène 400mg', 'Analgésiques', 500, 1200, 30),
            ('Tramadol 50mg', 'Analgésiques', 800, 1500, 15),
            
            # Vitamines
            ('Vitamine C 1000mg', 'Vitamines', 1500, 2800, 25),
            ('Multivitamines', 'Vitamines', 3500, 6000, 10),
            ('Calcium + D3', 'Vitamines', 2500, 4500, 15),
            
            # Dermatologie
            ('Betamethasone Crème', 'Dermatologie', 1200, 2200, 20),
            ('Sélénium Shampooing', 'Dermatologie', 4500, 7500, 10),
            ('Crème Hydratante', 'Dermatologie', 3000, 5500, 15),
            
            # Matériel Médical
            ('Thermomètre Digital', 'Matériel Médical', 1500, 3500, 10),
            ('Tensiomètre Brassard', 'Matériel Médical', 15000, 25000, 5),
            ('Pansements Autocollants', 'Matériel Médical', 500, 1000, 40)
        ]
        
        for p in produits:
            cursor.execute('''
                INSERT INTO produits (nom, societe, prix_achat, prix_vente, seuil_alerte)
                VALUES (?, ?, ?, ?, ?)
            ''', p)
            
            produit_id = cursor.lastrowid
            
            # Stock initial aléatoire
            import random
            stock_init = random.randint(50, 200)
            cursor.execute('''
                INSERT INTO stocks (produit_id, quantite)
                VALUES (?, ?)
            ''', (produit_id, stock_init))
        
        # Générer des ventes sur les 30 derniers jours
        cursor.execute("SELECT id, prix_vente FROM produits")
        produits_list = cursor.fetchall()
        
        for i in range(150):
            produit = random.choice(produits_list)
            quantite = random.randint(1, 3)
            jours_avant = random.randint(0, 30)
            heures_avant = random.randint(0, 23)
            date_vente = datetime.now() - timedelta(days=jours_avant, hours=heures_avant)
            
            # Verifier le stock avant de vendre
            cursor.execute('SELECT quantite FROM stocks WHERE produit_id = ?', (produit['id'],))
            stock_row = cursor.fetchone()
            if stock_row and stock_row['quantite'] >= quantite:
                cursor.execute('''
                    INSERT INTO ventes (produit_id, quantite, prix_unitaire, date_vente)
                    VALUES (?, ?, ?, ?)
                ''', (produit['id'], quantite, produit['prix_vente'], date_vente.isoformat()))
                
                cursor.execute('''
                    UPDATE stocks SET quantite = quantite - ?
                    WHERE produit_id = ?
                ''', (quantite, produit['id']))
        
        conn.commit()
        print("Donnees de test inserees")
    
    # Verifier si utilisateurs vides
    cursor.execute("SELECT COUNT(*) as count FROM utilisateurs")
    if cursor.fetchone()['count'] == 0:
        cursor.execute("INSERT INTO utilisateurs (nom, role, code_pin) VALUES ('Gérant', 'admin', '1234')")
        admin_id = cursor.lastrowid
        cursor.execute("INSERT INTO utilisateurs (nom, role, code_pin) VALUES ('Alice (Caisse 1)', 'employe', '0000')")
        # Attribuer les anciennes ventes a l'admin
        cursor.execute("UPDATE ventes SET vendeur_id = ? WHERE vendeur_id IS NULL", (admin_id,))
        cursor.execute("INSERT INTO parametres (clef, valeur) VALUES ('NOM_BAR', 'Pharma Moderne')")
        conn.commit()
        print("Utilisateurs par defaut crees.")
    
    conn.close()

# Fonctions utilitaires pour les requêtes courantes

def get_produits_with_stock():
    """Retourne tous les produits avec leur stock actuel"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.*, s.quantite as stock_actuel
        FROM produits p
        LEFT JOIN stocks s ON p.id = s.produit_id
        ORDER BY p.societe, p.nom
    ''')
    
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]

def get_ventes_aujourdhui():
    """Retourne les ventes du jour"""
    conn = get_db()
    cursor = conn.cursor()
    
    today = datetime.now().date()
    cursor.execute('''
        SELECT v.*, p.nom, p.societe
        FROM ventes v
        JOIN produits p ON v.produit_id = p.id
        WHERE DATE(v.date_vente) = ?
        ORDER BY v.date_vente DESC
    ''', (today.isoformat(),))
    
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]

def get_stats_globales():
    """Retourne les statistiques globales pour le dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    today = datetime.now().date()
    
    # Ventes du jour
    cursor.execute('''
        SELECT COALESCE(SUM(v.quantite * v.prix_unitaire), 0) as total
        FROM ventes v
        WHERE DATE(v.date_vente) = ?
    ''', (today.isoformat(),))
    revenus_jour = cursor.fetchone()['total']
    
    # Nombre de ventes du jour
    cursor.execute('''
        SELECT COUNT(*) as count
        FROM ventes v
        WHERE DATE(v.date_vente) = ?
    ''', (today.isoformat(),))
    ventes_jour = cursor.fetchone()['count']
    
    # Bénéfice du jour
    cursor.execute('''
        SELECT COALESCE(SUM(v.quantite * (v.prix_unitaire - p.prix_achat)), 0) as benefice
        FROM ventes v
        JOIN produits p ON v.produit_id = p.id
        WHERE DATE(v.date_vente) = ?
    ''', (today.isoformat(),))
    benefice_jour = cursor.fetchone()['benefice']
    
    # Alertes stock
    cursor.execute('''
        SELECT COUNT(*) as count
        FROM stocks s
        JOIN produits p ON s.produit_id = p.id
        WHERE s.quantite <= p.seuil_alerte
    ''')
    alertes_stock = cursor.fetchone()['count']
    
    conn.close()
    
    return {
        'revenus_jour': revenus_jour,
        'ventes_jour': ventes_jour,
        'benefice_jour': benefice_jour,
        'alertes_stock': alertes_stock
    }

def get_revenus_semaine():
    """Retourne les revenus des 7 derniers jours"""
    conn = get_db()
    cursor = conn.cursor()
    
    dates = []
    revenus = []
    
    for i in range(6, -1, -1):
        date = (datetime.now() - timedelta(days=i)).date()
        dates.append(date.strftime('%d/%m'))
        
        cursor.execute('''
            SELECT COALESCE(SUM(quantite * prix_unitaire), 0) as total
            FROM ventes
            WHERE DATE(date_vente) = ?
        ''', (date.isoformat(),))
        
        revenus.append(cursor.fetchone()['total'])
    
    conn.close()
    return [{'date': d, 'revenu': r} for d, r in zip(dates, revenus)]

def get_top_produits(limit=5):
    """Retourne les produits les plus vendus (par revenus)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.nom, SUM(v.quantite * v.prix_unitaire) as revenus
        FROM ventes v
        JOIN produits p ON v.produit_id = p.id
        GROUP BY p.id
        ORDER BY revenus DESC
        LIMIT ?
    ''', (limit,))
    
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]

def get_repartition_societes():
    """Retourne la répartition des ventes par société"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.societe, SUM(v.quantite * v.prix_unitaire) as revenus
        FROM ventes v
        JOIN produits p ON v.produit_id = p.id
        GROUP BY p.societe
        ORDER BY revenus DESC
    ''')
    
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]

def get_stocks_critiques():
    """Retourne les produits en stock critique"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.id, p.nom, p.societe, s.quantite, p.seuil_alerte
        FROM stocks s
        JOIN produits p ON s.produit_id = p.id
        WHERE s.quantite <= p.seuil_alerte
        ORDER BY (s.quantite * 1.0 / p.seuil_alerte) ASC
    ''')
    
    result = cursor.fetchall()
    conn.close()
    return [dict(row) for row in result]

# Initialisation au chargement du module
init_db()