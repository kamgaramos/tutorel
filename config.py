# config.py - Configuration générale du projet
import os

# Chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'pharma.sqlite')

# Constantes pharma
NOM_BAR = "Pharma Moderne"
DEVISE = "FCFA"

# Seuils stock par défaut
SEUIL_STOCK_DEFAUT = 10
ALERTE_CRITIQUE_RATIO = 0.5  # En dessous de 50% du seuil → critique

# Admin PIN
ADMIN_PIN = "1234"

# Catégories de sociétés (Pharmacie)
SOCIETES = ['Antibiotiques', 'Analgésiques', 'Vitamines', 'Dermatologie', 'Matériel Médical']

# Couleurs associées (pour les graphiques)
COULEURS_SOCIETES = {
    'Antibiotiques': '#2A9D8F',
    'Analgésiques': '#E76F51',
    'Vitamines': '#F4A261',
    'Dermatologie': '#E9C46A',
    'Matériel Médical': '#264653'
}

# Configuration ML
ML_PERIODE_DEFAUT = 30  # Jours d'historique pour entraînement
ML_PREVISION_JOURS = 7   # Prévisions sur 7 jours