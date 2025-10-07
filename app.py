#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Flask de gestion d'inventaire avec scanner de code-barres
Auteur: Assistant IA
Version: 1.0
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import sqlite3
import pandas as pd
import os
from datetime import datetime
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'

# Configuration de la base de données
DATABASE = 'database.db'

def init_db():
    """Initialise la base de données avec la table produits"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            code_barres TEXT UNIQUE NOT NULL,
            prix REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Ajouter quelques produits d'exemple si la table est vide
    cursor.execute('SELECT COUNT(*) FROM produits')
    if cursor.fetchone()[0] == 0:
        produits_exemple = [
            ('Coca-Cola 33cl', '5449000000996', 1.50, 25),
            ('Pain de mie', '3274080005003', 2.30, 12),
            ('Lait 1L', '3033710074617', 1.20, 8),
            ('Yaourt nature x4', '3033490001001', 3.45, 15),
            ('Pommes Golden 1kg', '2000000000001', 2.80, 20)
        ]
        
        cursor.executemany(
            'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (?, ?, ?, ?)',
            produits_exemple
        )
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Retourne une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Page d'accueil - Liste des produits"""
    conn = get_db_connection()
    produits = conn.execute(
        'SELECT * FROM produits ORDER BY nom'
    ).fetchall()
    conn.close()
    
    return render_template('index.html', produits=produits)

@app.route('/scanner')
def scanner():
    """Page de scan des codes-barres"""
    return render_template('scanner.html')

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """Page d'ajout de produit"""
    if request.method == 'POST':
        nom = request.form['nom']
        code_barres = request.form['code_barres']
        prix = float(request.form['prix'])
        stock = int(request.form['stock'])
        
        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (?, ?, ?, ?)',
                (nom, code_barres, prix, stock)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('ajouter.html', 
                                 error='Ce code-barres existe déjà!')
    
    return render_template('ajouter.html')

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    """Modifier un produit existant"""
    conn = get_db_connection()
    
    if request.method == 'POST':
        nom = request.form['nom']
        code_barres = request.form['code_barres']
        prix = float(request.form['prix'])
        stock = int(request.form['stock'])
        
        try:
            conn.execute(
                'UPDATE produits SET nom=?, code_barres=?, prix=?, stock=? WHERE id=?',
                (nom, code_barres, prix, stock, id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            produit = conn.execute('SELECT * FROM produits WHERE id = ?', (id,)).fetchone()
            conn.close()
            return render_template('modifier.html', produit=produit,
                                 error='Ce code-barres existe déjà!')
    
    produit = conn.execute('SELECT * FROM produits WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if produit is None:
        return redirect(url_for('index'))
    
    return render_template('modifier.html', produit=produit)

@app.route('/supprimer/<int:id>')
def supprimer(id):
    """Supprimer un produit"""
    conn = get_db_connection()
    conn.execute('DELETE FROM produits WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/statistiques')
def statistiques():
    """Page des statistiques avec graphiques"""
    conn = get_db_connection()
    produits = conn.execute(
        'SELECT nom, stock FROM produits ORDER BY stock DESC'
    ).fetchall()
    
    # Statistiques générales
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total_produits,
            SUM(stock) as total_stock,
            AVG(prix) as prix_moyen,
            SUM(CASE WHEN stock = 0 THEN 1 ELSE 0 END) as rupture_stock,
            SUM(CASE WHEN stock < 2 THEN 1 ELSE 0 END) as stock_faible
        FROM produits
    ''').fetchone()
    
    conn.close()
    
    return render_template('statistiques.html', produits=produits, stats=stats)

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API pour traiter le scan d'un code-barres"""
    data = request.get_json()
    code_barres = data.get('code_barres', '').strip()
    
    if not code_barres:
        return jsonify({'success': False, 'message': 'Code-barres manquant'})
    
    conn = get_db_connection()
    produit = conn.execute(
        'SELECT * FROM produits WHERE code_barres = ?', (code_barres,)
    ).fetchone()
    
    if not produit:
        conn.close()
        return jsonify({
            'success': False, 
            'message': f'Produit non trouvé pour le code-barres: {code_barres}'
        })
    
    nouveau_stock = produit['stock'] - 1
    
    if nouveau_stock < 0:
        conn.close()
        return jsonify({
            'success': False,
            'message': f'Stock insuffisant pour {produit["nom"]} (stock actuel: {produit["stock"]})'
        })
    
    # Mettre à jour le stock
    conn.execute(
        'UPDATE produits SET stock = ? WHERE id = ?',
        (nouveau_stock, produit['id'])
    )
    conn.commit()
    conn.close()
    
    # Déterminer le message selon le niveau de stock
    if nouveau_stock == 0:
        message = f'⚠️ RUPTURE DE STOCK - {produit["nom"]} (stock: 0)'
        alert_type = 'danger'
    elif nouveau_stock < 2:
        message = f'🔴 STOCK FAIBLE - {produit["nom"]} (stock: {nouveau_stock})'
        alert_type = 'warning'
    else:
        message = f'✅ Stock mis à jour - {produit["nom"]} (stock: {nouveau_stock})'
        alert_type = 'success'
    
    return jsonify({
        'success': True,
        'message': message,
        'alert_type': alert_type,
        'produit': {
            'nom': produit['nom'],
            'stock_avant': produit['stock'],
            'stock_apres': nouveau_stock,
            'prix': produit['prix']
        }
    })

@app.route('/api/produits')
def api_produits():
    """API pour récupérer la liste des produits (pour les graphiques)"""
    conn = get_db_connection()
    produits = conn.execute(
        'SELECT nom, stock, prix FROM produits ORDER BY nom'
    ).fetchall()
    conn.close()
    
    return jsonify([dict(produit) for produit in produits])

@app.route('/export/csv')
def export_csv():
    """Exporter la liste des produits au format CSV"""
    conn = get_db_connection()
    produits = conn.execute(
        'SELECT nom, code_barres, prix, stock FROM produits ORDER BY nom'
    ).fetchall()
    conn.close()
    
    # Créer un DataFrame pandas
    df = pd.DataFrame(produits, columns=['Nom', 'Code-barres', 'Prix', 'Stock'])
    
    # Créer un buffer en mémoire
    output = io.StringIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    # Créer un fichier temporaire
    filename = f'inventaire_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@app.route('/export/excel')
def export_excel():
    """Exporter la liste des produits au format Excel"""
    conn = get_db_connection()
    produits = conn.execute(
        'SELECT nom, code_barres, prix, stock FROM produits ORDER BY nom'
    ).fetchall()
    conn.close()
    
    # Créer un DataFrame pandas
    df = pd.DataFrame(produits, columns=['Nom', 'Code-barres', 'Prix', 'Stock'])
    
    # Créer un buffer en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Inventaire', index=False)
    
    output.seek(0)
    filename = f'inventaire_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    # Initialiser la base de données au démarrage
    init_db()
    
    # Lancer l'application Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
