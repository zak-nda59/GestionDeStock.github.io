#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier le contenu de la base de données SQLite
"""

import sqlite3
import os

def verifier_base_donnees():
    """Vérifie et affiche le contenu de la base de données"""
    
    db_path = 'database.db'
    
    # Vérifier si le fichier existe
    if not os.path.exists(db_path):
        print("❌ Le fichier database.db n'existe pas!")
        print(f"📁 Répertoire actuel: {os.getcwd()}")
        print(f"📋 Fichiers présents: {os.listdir('.')}")
        return
    
    print(f"✅ Base de données trouvée: {db_path}")
    print(f"📊 Taille du fichier: {os.path.getsize(db_path)} bytes")
    print("-" * 50)
    
    try:
        # Connexion à la base
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lister les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Tables trouvées: {[table[0] for table in tables]}")
        print("-" * 50)
        
        # Vérifier la table produits
        if ('produits',) in tables:
            cursor.execute("SELECT COUNT(*) FROM produits")
            count = cursor.fetchone()[0]
            print(f"📦 Nombre de produits: {count}")
            
            if count > 0:
                print("\n🏷️  Liste des produits:")
                cursor.execute("SELECT id, nom, code_barres, prix, stock FROM produits ORDER BY nom")
                produits = cursor.fetchall()
                
                print(f"{'ID':<3} | {'Nom':<20} | {'Code-barres':<15} | {'Prix':<8} | {'Stock':<5}")
                print("-" * 60)
                
                for produit in produits:
                    id_prod, nom, code_barres, prix, stock = produit
                    print(f"{id_prod:<3} | {nom:<20} | {code_barres:<15} | {prix:<8.2f} | {stock:<5}")
            else:
                print("⚠️  Aucun produit trouvé dans la base!")
        else:
            print("❌ Table 'produits' non trouvée!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture de la base: {e}")

if __name__ == "__main__":
    print("🔍 Vérification de la base de données SQLite")
    print("=" * 50)
    verifier_base_donnees()
    print("=" * 50)
    print("✅ Vérification terminée!")
