#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger les IDs dans la base de données
"""

import sqlite3
import os

def corriger_ids_sqlite():
    """Corrige les IDs dans la base SQLite"""
    
    db_path = 'database.db'
    
    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 État actuel de la base:")
        cursor.execute("SELECT id, nom, code_barres FROM produits ORDER BY id")
        produits = cursor.fetchall()
        
        for produit in produits:
            print(f"ID {produit[0]}: {produit[1]} ({produit[2]})")
        
        print("\n🔧 Correction des IDs...")
        
        # Méthode 1: Recréer la table avec des IDs consécutifs
        cursor.execute('''
            CREATE TABLE produits_temp AS 
            SELECT nom, code_barres, prix, stock, date_creation 
            FROM produits 
            ORDER BY id
        ''')
        
        # Supprimer l'ancienne table
        cursor.execute('DROP TABLE produits')
        
        # Recréer la table avec AUTO_INCREMENT
        cursor.execute('''
            CREATE TABLE produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                code_barres TEXT UNIQUE NOT NULL,
                prix REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Réinsérer les données (les IDs seront automatiquement 1, 2, 3...)
        cursor.execute('''
            INSERT INTO produits (nom, code_barres, prix, stock, date_creation)
            SELECT nom, code_barres, prix, stock, date_creation 
            FROM produits_temp
        ''')
        
        # Supprimer la table temporaire
        cursor.execute('DROP TABLE produits_temp')
        
        # Réinitialiser le compteur AUTO_INCREMENT
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="produits"')
        cursor.execute('INSERT INTO sqlite_sequence (name, seq) VALUES ("produits", (SELECT MAX(id) FROM produits))')
        
        conn.commit()
        
        print("✅ IDs corrigés!")
        print("\n📋 Nouvel état:")
        cursor.execute("SELECT id, nom, code_barres FROM produits ORDER BY id")
        produits = cursor.fetchall()
        
        for produit in produits:
            print(f"ID {produit[0]}: {produit[1]} ({produit[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def corriger_ids_mysql():
    """Corrige les IDs dans la base MySQL"""
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # Configuration MySQL
        config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'gestion_inventaire'
        }
        
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("🔍 État actuel de la base MySQL:")
        cursor.execute("SELECT id, nom, code_barres FROM produits ORDER BY id")
        produits = cursor.fetchall()
        
        for produit in produits:
            print(f"ID {produit[0]}: {produit[1]} ({produit[2]})")
        
        print("\n🔧 Correction des IDs MySQL...")
        
        # Créer une table temporaire
        cursor.execute('''
            CREATE TEMPORARY TABLE produits_temp AS 
            SELECT nom, code_barres, prix, stock, date_creation 
            FROM produits 
            ORDER BY id
        ''')
        
        # Vider la table originale
        cursor.execute('DELETE FROM produits')
        
        # Réinitialiser l'AUTO_INCREMENT
        cursor.execute('ALTER TABLE produits AUTO_INCREMENT = 1')
        
        # Réinsérer les données
        cursor.execute('''
            INSERT INTO produits (nom, code_barres, prix, stock, date_creation)
            SELECT nom, code_barres, prix, stock, date_creation 
            FROM produits_temp
        ''')
        
        conn.commit()
        
        print("✅ IDs MySQL corrigés!")
        print("\n📋 Nouvel état:")
        cursor.execute("SELECT id, nom, code_barres FROM produits ORDER BY id")
        produits = cursor.fetchall()
        
        for produit in produits:
            print(f"ID {produit[0]}: {produit[1]} ({produit[2]})")
        
        conn.close()
        
    except ImportError:
        print("❌ Module mysql-connector-python non installé")
    except Error as e:
        print(f"❌ Erreur MySQL: {e}")

if __name__ == "__main__":
    print("🔧 Correction des IDs de la base de données")
    print("=" * 50)
    
    choix = input("Quelle base corriger ?\n1. SQLite (database.db)\n2. MySQL (gestion_inventaire)\n3. Les deux\nVotre choix (1, 2 ou 3): ")
    
    if choix == "1":
        corriger_ids_sqlite()
    elif choix == "2":
        corriger_ids_mysql()
    elif choix == "3":
        corriger_ids_sqlite()
        print("\n" + "="*50)
        corriger_ids_mysql()
    else:
        print("❌ Choix invalide")
    
    print("\n" + "="*50)
    print("✅ Correction terminée!")
