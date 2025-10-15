#!/usr/bin/env python3
"""
🚀 BOUTIQUE MOBILE - APPLICATION ORIGINALE
Application de gestion d'inventaire - Flask + SQLite
"""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, make_response
from datetime import datetime
import io
import csv

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
    """Récupérer toutes les catégories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories ORDER BY nom')
        categories = cursor.fetchall()
        conn.close()
        return [dict(cat) for cat in categories]
    except Exception as e:
        return []

@app.route('/')
def index():
    """Page d'accueil avec recherche et aperçu produits"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Paramètres de recherche
        recherche = request.args.get('q', '').strip()
        categorie = request.args.get('cat', '').strip()
        
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
        
        cursor.execute(query, params)
        produits = cursor.fetchall()
        
        # Stats rapides
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as ruptures FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()[0]
        
        conn.close()
        
        return render_template('index.html', 
                             produits=[dict(p) for p in produits],
                             categories=get_categories(),
                             recherche=recherche,
                             categorie_filtre=categorie,
                             total=total,
                             ruptures=ruptures)
        
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/scanner')
def scanner():
    """Page scanner parfait - simple et fonctionnel"""
    return render_template('scanner_parfait.html')

@app.route('/scan', methods=['POST'])
def scan():
    """API de scan - avec choix d'action et quantité"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        action = data.get('action', '').strip()  # 'retirer', 'ajouter', ou vide pour demander
        quantite = data.get('quantite', 1)
        
        if not code:
            return jsonify({'success': False, 'message': 'Code vide'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produits WHERE code_barres = ?', (code,))
        produit = cursor.fetchone()
        
        if not produit:
            conn.close()
            return jsonify({'success': False, 'message': f'Produit non trouvé: {code}'})
        
        produit_dict = dict(produit)
        
        # Si aucune action spécifiée, retourner les infos du produit pour demander l'action
        if not action:
            conn.close()
            return jsonify({
                'success': True,
                'ask_action': True,
                'produit': {
                    'id': produit_dict['id'],
                    'nom': produit_dict['nom'],
                    'code_barres': produit_dict['code_barres'],
                    'prix': produit_dict['prix'],
                    'stock': produit_dict['stock'],
                    'categorie': produit_dict['categorie']
                },
                'message': f'Produit trouvé: {produit_dict["nom"]}'
            })
        
        # Traitement de l'action
        stock_actuel = produit_dict['stock']
        
        if action == 'retirer':
            if stock_actuel < quantite:
                conn.close()
                return jsonify({
                    'success': False, 
                    'message': f'❌ Stock insuffisant ! Stock actuel: {stock_actuel}, demandé: {quantite}'
                })
            nouveau_stock = stock_actuel - quantite
            action_text = f'retiré {quantite}'
        
        elif action == 'ajouter':
            nouveau_stock = stock_actuel + quantite
            action_text = f'ajouté {quantite}'
        
        else:
            conn.close()
            return jsonify({'success': False, 'message': 'Action non valide'})
        
        # Mise à jour du stock
        cursor.execute('UPDATE produits SET stock = ? WHERE id = ?', (nouveau_stock, produit_dict['id']))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'✅ {produit_dict["nom"]}: {action_text} unité(s)',
            'produit': produit_dict['nom'],
            'action': action,
            'quantite': quantite,
            'stock_precedent': stock_actuel,
            'nouveau_stock': nouveau_stock
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/api/produits')
def api_produits():
    """API JSON des produits"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(produits),
            'produits': [dict(p) for p in produits]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health():
    """Health check pour Render"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM produits')
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'app': 'Boutique Mobile',
            'version': '2.0',
            'message': 'Application fonctionnelle',
            'database': 'ok',
            'produits_count': count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur: {str(e)}'
        })

@app.route('/favicon.ico')
def favicon():
    """Favicon simple"""
    return '', 204

if __name__ == '__main__':
    print("🚀 BOUTIQUE MOBILE - APPLICATION ORIGINALE")
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
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Application prête sur le port {port}")
    print("📱 Accès local: http://localhost:5000")
    print("🔧 Fonctionnalités:")
    print("   ✅ Scanner codes-barres")
    print("   ✅ Gestion stock")
    print("   ✅ Base SQLite")
    print("   ✅ API JSON")
    
    # Lancement
    app.run(host='0.0.0.0', port=port, debug=False)
