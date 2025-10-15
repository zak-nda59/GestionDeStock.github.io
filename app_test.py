#!/usr/bin/env python3
"""
🚀 BOUTIQUE MOBILE - VERSION TEST
Test simple pour identifier le problème
"""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    """Connexion SQLite locale"""
    conn = sqlite3.connect('boutique_mobile.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialise la base de données SQLite"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table catégories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            emoji TEXT DEFAULT '📦',
            description TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table produits
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            code_barres TEXT UNIQUE NOT NULL,
            prix REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            categorie TEXT DEFAULT 'Autre',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Catégories par défaut
    categories_defaut = [
        ('📱', 'Écran', 'Écrans et dalles tactiles'),
        ('🔋', 'Batterie', 'Batteries et accumulateurs'),
        ('🛡️', 'Coque', 'Coques et étuis de protection'),
        ('📎', 'Accessoire', 'Accessoires divers'),
        ('🔌', 'Câble', 'Câbles et chargeurs'),
        ('🔧', 'Outil', 'Outils de réparation'),
        ('💾', 'Composant', 'Composants électroniques'),
        ('🎧', 'Audio', 'Écouteurs et haut-parleurs'),
        ('📦', 'Autre', 'Autres produits')
    ]
    
    for emoji, nom, desc in categories_defaut:
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO categories (emoji, nom, description) VALUES (?, ?, ?)',
                (emoji, nom, desc)
            )
        except:
            pass
    
    # Produits d'exemple (seulement si aucun produit existe)
    cursor.execute('SELECT COUNT(*) as count FROM produits')
    result = cursor.fetchone()
    count = result[0]
    
    if count == 0:
        produits_exemple = [
            ('Écran iPhone 12', '1234567890123', 45.99, 15, 'Écran'),
            ('Batterie Samsung S21', '2345678901234', 29.99, 8, 'Batterie'),
            ('Coque iPhone 13 Pro', '3456789012345', 12.99, 25, 'Coque'),
            ('Câble USB-C 2m', '4567890123456', 8.99, 30, 'Câble'),
            ('Écouteurs Bluetooth', '5678901234567', 19.99, 12, 'Audio'),
            ('Tournevis Kit', '6789012345678', 15.99, 5, 'Outil'),
            ('Chargeur Rapide', '7890123456789', 24.99, 18, 'Câble')
        ]
        
        for nom, code, prix, stock, cat in produits_exemple:
            try:
                cursor.execute(
                    'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (?, ?, ?, ?, ?)',
                    (nom, code, prix, stock, cat)
                )
            except:
                pass
    
    conn.commit()
    conn.close()

def get_categories():
    """Récupère toutes les catégories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories ORDER BY nom')
        categories = cursor.fetchall()
        conn.close()
        return [dict(cat) for cat in categories]
    except Exception as e:
        print(f"Erreur get_categories: {e}")
        return []

@app.route('/')
def index():
    """Page d'accueil simple pour test"""
    try:
        print("=== DÉBUT INDEX ===")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Connexion DB OK")
        
        # Paramètres de recherche
        recherche = request.args.get('q', '').strip()
        categorie = request.args.get('cat', '').strip()
        
        print(f"Recherche: {recherche}, Catégorie: {categorie}")
        
        # Construction de la requête
        query = 'SELECT * FROM produits WHERE 1=1'
        params = []
        
        if recherche:
            query += ' AND (nom LIKE ? OR code_barres LIKE ?)'
            params.extend([f'%{recherche}%', f'%{recherche}%'])
        
        if categorie:
            query += ' AND categorie = ?'
            params.append(categorie)
        
        query += ' ORDER BY nom LIMIT 12'
        
        print(f"Query: {query}")
        print(f"Params: {params}")
        
        cursor.execute(query, params)
        produits = cursor.fetchall()
        
        print(f"Produits trouvés: {len(produits)}")
        
        # Stats rapides
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as ruptures FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"Stats: total={total}, ruptures={ruptures}")
        
        # Récupérer les catégories
        categories = get_categories()
        print(f"Catégories: {len(categories)}")
        
        print("=== RENDU TEMPLATE ===")
        
        return render_template('index_simple.html', 
                             produits=[dict(p) for p in produits],
                             categories=categories,
                             recherche=recherche,
                             categorie_filtre=categorie,
                             total=total,
                             ruptures=ruptures)
        
    except Exception as e:
        print(f"ERREUR INDEX: {e}")
        import traceback
        traceback.print_exc()
        return f"Erreur: {str(e)}", 500

@app.route('/test')
def test():
    """Page de test simple"""
    return "<h1>✅ Test OK</h1><p>L'application Flask fonctionne !</p>"

@app.route('/favicon.ico')
def favicon():
    """Favicon simple"""
    return '', 204

if __name__ == '__main__':
    print("🚀 BOUTIQUE MOBILE - VERSION TEST")
    print("=" * 50)
    
    # Initialisation de la base de données
    try:
        init_database()
        print("✅ Base de données SQLite initialisée")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM produits')
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"📦 {count} produits en base")
        
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
    
    print("🌐 Application test prête")
    print("📱 Test simple: http://localhost:5000/test")
    print("📱 Page complète: http://localhost:5000")
    
    # Lancement avec debug pour voir les erreurs
    app.run(host='0.0.0.0', port=5000, debug=True)
