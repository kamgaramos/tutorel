# config.py - Configuration générale du projet
import os

# Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'bar.sqlite')

# Constantes bar
NOM_BAR = "Le Camer'Bar"
DEVISE = "FCFA"

# Seuils stock par défaut
SEUIL_STOCK_DEFAUT = 10
ALERTE_CRITIQUE_RATIO = 0.5  # En dessous de 50% du seuil → critique

# Catégories de sociétés (5 comme demandé)
SOCIETES = ['SABC', 'UCB', 'Guinness', 'Sources du Pays', 'Autres Produits']

# Couleurs associées (pour les graphiques)
COULEURS_SOCIETES = {
    'SABC': '#E63946',
    'UCB': '#F4A261',
    'Guinness': '#2EC4B6',
    'Sources du Pays': '#4A90D9',
    'Autres Produits': '#9B5DE5'
}

# Configuration ML
ML_PERIODE_DEFAUT = 30  # Jours d'historique pour entraînement
ML_PREVISION_JOURS = 7   # Prévisions sur 7 jours