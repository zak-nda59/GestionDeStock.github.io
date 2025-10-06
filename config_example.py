# Configuration MySQL - EXEMPLE
# Copiez ce fichier vers config.py et modifiez les valeurs

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'votre_mot_de_passe_mysql',
    'database': 'gestion_inventaire',
    'charset': 'utf8mb4'
}

# Configuration Flask
SECRET_KEY = 'votre_cle_secrete_ici'
DEBUG = True
PORT = 5004

# Configuration Application
APP_NAME = "Gestion d'Inventaire"
VERSION = "1.0.0"
