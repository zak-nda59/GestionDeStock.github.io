#!/usr/bin/env python3
"""
Script de correction automatique de la base de données
Ajoute la colonne 'categorie' si elle n'existe pas
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

def fix_database():
    """Corrige la structure de la base de données"""
    try:
        print("🔧 CORRECTION AUTOMATIQUE DE LA BASE DE DONNÉES")
        print("=" * 50)
        
        # Connexion à MySQL
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Connexion MySQL établie")
        
        # Vérifier si la colonne 'categorie' existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'gestion_inventaire' 
            AND TABLE_NAME = 'produits' 
            AND COLUMN_NAME = 'categorie'
        """)
        
        column_exists = cursor.fetchone()[0] > 0
        
        if column_exists:
            print("✅ La colonne 'categorie' existe déjà")
        else:
            print("⚠️ La colonne 'categorie' n'existe pas - Ajout en cours...")
            
            # Ajouter la colonne categorie
            cursor.execute("ALTER TABLE produits ADD COLUMN categorie VARCHAR(50) DEFAULT 'Autre'")
            print("✅ Colonne 'categorie' ajoutée avec succès")
            
            # Mettre à jour les produits existants avec des catégories par défaut
            cursor.execute("UPDATE produits SET categorie = 'Autre' WHERE categorie IS NULL")
            print("✅ Produits existants mis à jour")
        
        # Vérifier la structure finale
        cursor.execute("DESCRIBE produits")
        columns = cursor.fetchall()
        
        print("\n📋 Structure de la table 'produits':")
        for column in columns:
            print(f"   - {column[0]} ({column[1]})")
        
        # Compter les produits
        cursor.execute("SELECT COUNT(*) FROM produits")
        count = cursor.fetchone()[0]
        print(f"\n📦 Nombre de produits: {count}")
        
        if count > 0:
            cursor.execute("SELECT nom, categorie FROM produits LIMIT 5")
            produits = cursor.fetchall()
            print("\n📝 Exemples de produits:")
            for produit in produits:
                print(f"   - {produit[0]} ({produit[1]})")
        
        conn.close()
        print("\n✅ CORRECTION TERMINÉE AVEC SUCCÈS")
        print("🚀 Vous pouvez maintenant lancer l'application")
        return True
        
    except Error as e:
        print(f"❌ Erreur MySQL: {e}")
        return False

if __name__ == '__main__':
    if fix_database():
        print("\n💡 Commande pour lancer l'application:")
        print("   python app_mobile_auto.py")
    else:
        print("\n🔧 Vérifiez que WAMP est démarré et que MySQL fonctionne")
