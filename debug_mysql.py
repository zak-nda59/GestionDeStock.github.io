#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic et correction pour l'application MySQL
"""

import mysql.connector
from mysql.connector import Error

# Configuration MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'gestion_inventaire',
    'charset': 'utf8mb4'
}

def diagnostic_complet():
    """Effectue un diagnostic complet de la base MySQL"""
    
    print("🔍 DIAGNOSTIC MYSQL - GESTION D'INVENTAIRE")
    print("=" * 50)
    
    try:
        # Test de connexion
        print("1. Test de connexion...")
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        print("   ✅ Connexion MySQL réussie")
        
        cursor = conn.cursor(dictionary=True)
        
        # Vérifier la base de données
        print("\n2. Vérification de la base de données...")
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()
        print(f"   ✅ Base active: {db_name['DATABASE()']}")
        
        # Lister les tables
        print("\n3. Tables disponibles...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            for table in tables:
                table_name = list(table.values())[0]
                print(f"   ✅ Table trouvée: {table_name}")
        else:
            print("   ❌ Aucune table trouvée!")
            return False
        
        # Vérifier la structure de la table produits
        print("\n4. Structure de la table produits...")
        try:
            cursor.execute("DESCRIBE produits")
            columns = cursor.fetchall()
            
            print("   Colonnes:")
            for col in columns:
                print(f"     - {col['Field']} ({col['Type']})")
        except Error as e:
            print(f"   ❌ Erreur structure: {e}")
            return False
        
        # Compter les produits
        print("\n5. Données dans la table produits...")
        cursor.execute("SELECT COUNT(*) as total FROM produits")
        count = cursor.fetchone()
        print(f"   📦 Nombre de produits: {count['total']}")
        
        # Afficher les produits
        if count['total'] > 0:
            cursor.execute("SELECT * FROM produits ORDER BY id")
            produits = cursor.fetchall()
            
            print("\n   Liste des produits:")
            for produit in produits:
                print(f"     ID {produit['id']}: {produit['nom']} - {produit['code_barres']} - {produit['prix']}€ - Stock: {produit['stock']}")
        else:
            print("   ⚠️ Aucun produit trouvé!")
        
        conn.close()
        return True
        
    except Error as e:
        print(f"❌ Erreur MySQL: {e}")
        return False

def corriger_donnees():
    """Corrige les données manquantes"""
    
    print("\n🔧 CORRECTION DES DONNÉES")
    print("=" * 30)
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("SHOW TABLES LIKE 'produits'")
        if not cursor.fetchone():
            print("Création de la table produits...")
            cursor.execute('''
                CREATE TABLE produits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    code_barres VARCHAR(50) UNIQUE NOT NULL,
                    prix DECIMAL(10,2) NOT NULL,
                    stock INT NOT NULL DEFAULT 0,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            print("   ✅ Table créée")
        
        # Vérifier s'il y a des données
        cursor.execute("SELECT COUNT(*) FROM produits")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("Ajout de produits d'exemple...")
            produits_exemple = [
                ('Coca-Cola 33cl', '5449000000996', 1.50, 25),
                ('Pain de mie', '3274080005003', 2.30, 12),
                ('Lait 1L', '3033710074617', 1.20, 8),
                ('Yaourt nature x4', '3033490001001', 3.45, 15),
                ('Pommes Golden 1kg', '2000000000001', 2.80, 20),
                ('Smartphone iPhone', '1234567890123', 599.99, 5),
                ('Ordinateur portable', '9876543210987', 899.00, 3)
            ]
            
            cursor.executemany(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (%s, %s, %s, %s)',
                produits_exemple
            )
            
            print(f"   ✅ {len(produits_exemple)} produits ajoutés")
        else:
            print(f"   ℹ️ {count} produits déjà présents")
        
        conn.commit()
        conn.close()
        
        print("✅ Correction terminée!")
        return True
        
    except Error as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def tester_requetes():
    """Teste les requêtes utilisées par l'application"""
    
    print("\n🧪 TEST DES REQUÊTES")
    print("=" * 25)
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Test requête index
        print("1. Test requête page d'accueil...")
        cursor.execute('SELECT * FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        print(f"   ✅ {len(produits)} produits récupérés")
        
        # Test requête statistiques
        print("2. Test requête statistiques...")
        cursor.execute('''
            SELECT 
                COUNT(*) as total_produits,
                SUM(stock) as total_stock,
                AVG(prix) as prix_moyen,
                SUM(CASE WHEN stock = 0 THEN 1 ELSE 0 END) as rupture_stock,
                SUM(CASE WHEN stock < 2 THEN 1 ELSE 0 END) as stock_faible
            FROM produits
        ''')
        stats = cursor.fetchone()
        print(f"   ✅ Stats: {stats['total_produits']} produits, {stats['total_stock']} stock total")
        
        # Test requête API
        print("3. Test requête API produits...")
        cursor.execute('SELECT nom, stock, prix FROM produits ORDER BY nom')
        api_produits = cursor.fetchall()
        print(f"   ✅ {len(api_produits)} produits pour API")
        
        conn.close()
        return True
        
    except Error as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC ET CORRECTION MYSQL")
    print("=" * 60)
    
    # Diagnostic
    if diagnostic_complet():
        print("\n✅ Diagnostic réussi!")
    else:
        print("\n❌ Problèmes détectés, correction en cours...")
        corriger_donnees()
    
    # Test des requêtes
    tester_requetes()
    
    print("\n" + "=" * 60)
    print("🎉 Diagnostic terminé! Redémarrez l'application.")
