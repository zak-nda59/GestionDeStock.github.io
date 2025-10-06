"""
Application Flask - Version Déploiement Simplifiée
Utilise l'app existante avec SQLite au lieu de MySQL
"""

import os
import sqlite3
import sys

# Remplacer MySQL par SQLite dans l'app principale
def patch_mysql_to_sqlite():
    """Remplace les appels MySQL par SQLite"""
    global mysql
    
    class SQLiteConnector:
        def connect(self, **kwargs):
            conn = sqlite3.connect('inventaire.db')
            conn.row_factory = sqlite3.Row
            return conn
    
    # Simuler mysql.connector
    mysql = type('mysql', (), {})()
    mysql.connector = SQLiteConnector()
    mysql.connector.Error = sqlite3.Error

# Appliquer le patch
patch_mysql_to_sqlite()

# Importer l'app principale après le patch
from app_simple import *

# Modifier la configuration pour SQLite
def get_connection():
    """Connexion SQLite au lieu de MySQL"""
    try:
        conn = sqlite3.connect('inventaire.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Erreur SQLite: {e}")
        return None

def initialiser_base_donnees():
    """Initialise la base SQLite"""
    try:
        conn = get_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Créer la table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                code_barres TEXT UNIQUE NOT NULL,
                prix REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        # Vérifier si des produits existent
        cursor.execute('SELECT COUNT(*) FROM produits')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Produits d'exemple
            produits = [
                ("Coca-Cola", "123456789", 1.50, 10),
                ("Pain", "987654321", 0.90, 0),
                ("Lait", "555666777", 1.20, 2),
                ("Yaourt", "444555666", 0.80, 1),
                ("Eau", "111222333", 0.60, 15),
                ("Biscuits", "777888999", 2.30, 8),
                ("Fromage", "333444555", 3.50, 3)
            ]
            
            cursor.executemany(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (?, ?, ?, ?)',
                produits
            )
            
            print(f"✅ {len(produits)} produits ajoutés")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur init: {e}")
        return False

if __name__ == '__main__':
    print("🚀 APPLICATION DÉPLOIEMENT - GESTION D'INVENTAIRE")
    print("=" * 50)
    
    # Port pour hébergement
    port = int(os.environ.get('PORT', 5000))
    
    # Initialiser
    if initialiser_base_donnees():
        print("✅ Base SQLite prête")
        print(f"🌐 Port: {port}")
        
        # Lancer l'app
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("❌ Erreur initialisation")
