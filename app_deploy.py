#!/usr/bin/env python3
"""
🚀 BOUTIQUE MOBILE - VERSION DÉPLOIEMENT RENDER
Application ultra-simple garantie de fonctionner sur Render
"""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    """Connexion SQLite"""
    conn = sqlite3.connect('boutique.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialise la base de données"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            code_barres TEXT UNIQUE NOT NULL,
            prix REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            categorie TEXT DEFAULT 'Autre'
        )
    ''')
    
    # Vérifier s'il y a des produits
    cursor.execute('SELECT COUNT(*) FROM produits')
    count = cursor.fetchone()[0]
    
    if count == 0:
        produits = [
            ('Écran iPhone 12', '1234567890123', 45.99, 15, 'Écran'),
            ('Batterie Samsung S21', '2345678901234', 29.99, 8, 'Batterie'),
            ('Coque iPhone 13 Pro', '3456789012345', 12.99, 25, 'Coque'),
            ('Câble USB-C 2m', '4567890123456', 8.99, 30, 'Câble'),
            ('Écouteurs Bluetooth', '5678901234567', 19.99, 12, 'Audio'),
            ('Tournevis Kit', '6789012345678', 15.99, 5, 'Outil'),
            ('Chargeur Rapide', '7890123456789', 24.99, 18, 'Accessoire')
        ]
        
        for nom, code, prix, stock, cat in produits:
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (?, ?, ?, ?, ?)',
                (nom, code, prix, stock, cat)
            )
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Page d'accueil"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('index.html', produits=produits)
    except Exception as e:
        return f"<h1>Boutique Mobile</h1><p>Application en cours de démarrage...</p><p>Erreur: {str(e)}</p>"

@app.route('/scanner')
def scanner():
    """Page scanner"""
    return render_template('scanner.html')

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """Ajouter un produit"""
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '').strip()
            prix = float(request.form.get('prix', 0))
            stock = int(request.form.get('stock', 0))
            categorie = request.form.get('categorie', 'Autre')
            
            if not nom or prix <= 0:
                return render_template('ajouter.html', error="Nom et prix requis")
            
            # Code-barres automatique
            import random
            code_barres = ''.join([str(random.randint(0, 9)) for _ in range(13)])
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (?, ?, ?, ?, ?)',
                (nom, code_barres, prix, stock, categorie)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
            
        except Exception as e:
            return render_template('ajouter.html', error=f"Erreur: {str(e)}")
    
    return render_template('ajouter.html')

@app.route('/statistiques')
def statistiques():
    """Page statistiques"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM produits')
        total = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(prix * stock) FROM produits')
        valeur = cursor.fetchone()[0] or 0
        
        conn.close()
        
        stats = {
            'total': total,
            'ruptures': ruptures,
            'valeur': round(valeur, 2)
        }
        
        return render_template('statistiques.html', stats=stats)
        
    except Exception as e:
        return f"<h1>Statistiques</h1><p>Erreur: {str(e)}</p>"

@app.route('/scan', methods=['POST'])
def scan():
    """API de scan"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        action = data.get('action', '').strip()
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
        
        if not action:
            conn.close()
            return jsonify({
                'success': True,
                'ask_action': True,
                'produit': produit_dict,
                'message': f'Produit trouvé: {produit_dict["nom"]}'
            })
        
        stock_actuel = produit_dict['stock']
        
        if action == 'retirer':
            if stock_actuel < quantite:
                conn.close()
                return jsonify({'success': False, 'message': f'Stock insuffisant ! Stock: {stock_actuel}'})
            nouveau_stock = stock_actuel - quantite
        elif action == 'ajouter':
            nouveau_stock = stock_actuel + quantite
        else:
            conn.close()
            return jsonify({'success': False, 'message': 'Action invalide'})
        
        cursor.execute('UPDATE produits SET stock = ? WHERE id = ?', (nouveau_stock, produit_dict['id']))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'✅ {produit_dict["nom"]}: {stock_actuel} → {nouveau_stock}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/api/produits')
def api_produits():
    """API JSON"""
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
    """Health check"""
    return jsonify({
        'status': 'ok', 
        'app': 'Boutique Mobile',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    return f"<h1>Erreur 500</h1><p>Erreur interne: {str(e)}</p><a href='/'>Retour à l'accueil</a>"

if __name__ == '__main__':
    print("🚀 BOUTIQUE MOBILE - DÉPLOIEMENT RENDER")
    print("=" * 50)
    
    try:
        init_database()
        print("✅ Base de données initialisée")
    except Exception as e:
        print(f"❌ Erreur DB: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Application sur le port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
