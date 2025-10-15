#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script automatique pour corriger les IDs SQLite
"""

import sqlite3
import os

def corriger_ids_sqlite():
    """Corrige automatiquement les IDs dans la base SQLite"""
    
    db_path = 'database.db'
    
    if not os.path.exists(db_path):
        print("❌ Base de données non trouvée!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 État AVANT correction:")
        cursor.execute("SELECT id, nom, code_barres FROM produits ORDER BY id")
        produits = cursor.fetchall()
        
        for produit in produits:
            print(f"  ID {produit[0]}: {produit[1]} ({produit[2]})")
        
        print("\n🔧 Correction des IDs en cours...")
        
        # Sauvegarder les données dans l'ordre
        cursor.execute('''
            CREATE TABLE produits_backup AS 
            SELECT nom, code_barres, prix, stock, date_creation 
            FROM produits 
            ORDER BY id
        ''')
        
        # Supprimer l'ancienne table
        cursor.execute('DROP TABLE produits')
        
        # Recréer la table
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
        
        # Réinsérer les données (IDs automatiques: 1, 2, 3...)
        cursor.execute('''
            INSERT INTO produits (nom, code_barres, prix, stock, date_creation)
            SELECT nom, code_barres, prix, stock, date_creation 
            FROM produits_backup
        ''')
        
        # Nettoyer
        cursor.execute('DROP TABLE produits_backup')
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="produits"')
        
        conn.commit()
        
        print("✅ IDs corrigés avec succès!")
        print("\n📋 État APRÈS correction:")
        cursor.execute("SELECT id, nom, code_barres FROM produits ORDER BY id")
        produits = cursor.fetchall()
        
        for produit in produits:
            print(f"  ID {produit[0]}: {produit[1]} ({produit[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Correction automatique des IDs SQLite")
    print("=" * 45)
    
    if corriger_ids_sqlite():
        print("\n🎉 Les IDs sont maintenant consécutifs: 1, 2, 3...")
        print("Redémarrez votre application pour voir les changements.")
    else:
        print("\n❌ Échec de la correction.")
    
    print("=" * 45)
