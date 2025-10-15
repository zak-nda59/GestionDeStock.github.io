#!/usr/bin/env python3
"""
Script pour vider complètement la base de données
et la préparer pour de nouveaux produits
"""

import mysql.connector
from mysql.connector import Error

# Configuration MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'gestion_inventaire',
    'charset': 'utf8mb4',
    'autocommit': True
}

def reset_database():
    """Vide complètement la base de données"""
    try:
        print("🗑️ REMISE À ZÉRO DE LA BASE DE DONNÉES")
        print("=" * 50)
        
        # Connexion à MySQL
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Connexion MySQL établie")
        
        # Compter les produits actuels
        cursor.execute("SELECT COUNT(*) FROM produits")
        count_before = cursor.fetchone()[0]
        print(f"📦 Produits actuels dans la base: {count_before}")
        
        if count_before > 0:
            # Vider complètement la table
            cursor.execute("DELETE FROM produits")
            
            # Remettre l'auto-increment à 1
            cursor.execute("ALTER TABLE produits AUTO_INCREMENT = 1")
            
            print(f"🗑️ {count_before} produits supprimés")
            print("🔄 Compteur ID remis à zéro")
        else:
            print("✅ La base était déjà vide")
        
        # Vérifier que la table est vide
        cursor.execute("SELECT COUNT(*) FROM produits")
        count_after = cursor.fetchone()[0]
        
        # Vérifier la structure de la table
        cursor.execute("DESCRIBE produits")
        columns = cursor.fetchall()
        
        print("\n📋 Structure de la table 'produits' (vide):")
        for column in columns:
            print(f"   - {column[0]} ({column[1]})")
        
        print(f"\n📦 Produits restants: {count_after}")
        
        conn.close()
        
        if count_after == 0:
            print("\n✅ BASE DE DONNÉES VIDÉE AVEC SUCCÈS")
            print("🚀 Prête à recevoir de nouveaux produits")
            return True
        else:
            print("\n❌ Erreur lors de la suppression")
            return False
        
    except Error as e:
        print(f"❌ Erreur MySQL: {e}")
        return False

if __name__ == '__main__':
    if reset_database():
        print("\n💡 Étapes suivantes:")
        print("   1. Lancez: python app_mobile_auto.py")
        print("   2. Allez sur: http://localhost:5000")
        print("   3. Cliquez 'Ajouter' pour ajouter vos produits")
        print("   4. Chaque produit sera sauvegardé automatiquement")
    else:
        print("\n🔧 Vérifiez que WAMP est démarré et que MySQL fonctionne")
