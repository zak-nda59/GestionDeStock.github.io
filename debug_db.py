#!/usr/bin/env python3
"""
Script de diagnostic de la base de données
"""

import mysql.connector

def debug_database():
    try:
        # Connexion à la base
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='gestion_inventaire'
        )
        
        cursor = conn.cursor()
        
        print("🔍 DIAGNOSTIC BASE DE DONNÉES")
        print("=" * 50)
        
        # Compter les produits
        cursor.execute('SELECT COUNT(*) FROM produits')
        count = cursor.fetchone()[0]
        print(f"📊 Nombre total de produits: {count}")
        
        # Lister tous les produits
        cursor.execute('SELECT id, nom, code_barres, prix, stock FROM produits ORDER BY id')
        produits = cursor.fetchall()
        
        print("\n📋 LISTE COMPLÈTE DES PRODUITS:")
        print("-" * 50)
        for p in produits:
            print(f"ID: {p[0]} | Nom: {p[1]} | Code: {p[2]} | Prix: {p[3]}€ | Stock: {p[4]}")
        
        # Vérifier les produits avec stock > 0
        cursor.execute('SELECT COUNT(*) FROM produits WHERE stock > 0')
        stock_positif = cursor.fetchone()[0]
        print(f"\n✅ Produits avec stock > 0: {stock_positif}")
        
        # Vérifier les produits en rupture
        cursor.execute('SELECT COUNT(*) FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()[0]
        print(f"🚨 Produits en rupture: {ruptures}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    debug_database()
