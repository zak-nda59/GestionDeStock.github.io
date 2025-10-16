#!/usr/bin/env python3
"""
🚀 BOUTIQUE MOBILE - VERSION DÉPLOIEMENT RENDER
Application complète de gestion d'inventaire avec base de données persistante
Compatible PostgreSQL (Render) et SQLite (local)
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import pandas as pd
from datetime import datetime
import tempfile

app = Flask(__name__)

# Configuration base de données
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def get_db_connection():
    """Connexion base de données (PostgreSQL sur Render, SQLite en local)"""
    if DATABASE_URL:
        # PostgreSQL sur Render
        conn = psycopg2.connect(DATABASE_URL)
        return conn, 'postgresql'
    else:
        # SQLite en local
        conn = sqlite3.connect('boutique_mobile.db')
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'

def init_database():
    """Initialise la base de données avec les tables et données de base"""
    conn, db_type = get_db_connection()
    
    if db_type == 'postgresql':
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Table catégories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(100) NOT NULL UNIQUE,
                emoji VARCHAR(10) DEFAULT '📦',
                description TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table produits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                code_barres VARCHAR(50) UNIQUE NOT NULL,
                prix DECIMAL(10,2) NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                categorie VARCHAR(100) DEFAULT 'Autre',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
    else:
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
            if db_type == 'postgresql':
                cursor.execute(
                    'INSERT INTO categories (emoji, nom, description) VALUES (%s, %s, %s) ON CONFLICT (nom) DO NOTHING',
                    (emoji, nom, desc)
                )
            else:
                cursor.execute(
                    'INSERT OR IGNORE INTO categories (emoji, nom, description) VALUES (?, ?, ?)',
                    (emoji, nom, desc)
                )
        except:
            pass
    
    # Produits d'exemple (seulement si aucun produit existe)
    cursor.execute('SELECT COUNT(*) as count FROM produits')
    result = cursor.fetchone()
    count = result['count'] if db_type == 'postgresql' else result[0]
    
    if count == 0:
        produits_exemple = [
            ('Écran iPhone 12', '1234567890123', 45.99, 15, 'Écran'),
            ('Batterie Samsung S21', '2345678901234', 29.99, 8, 'Batterie'),
            ('Coque iPhone 13 Pro', '3456789012345', 12.99, 25, 'Coque'),
            ('Câble USB-C 2m', '4567890123456', 8.99, 30, 'Câble')
        ]
        
        for nom, code, prix, stock, cat in produits_exemple:
            try:
                if db_type == 'postgresql':
                    cursor.execute(
                        'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (%s, %s, %s, %s, %s)',
                        (nom, code, prix, stock, cat)
                    )
                else:
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
    conn, db_type = get_db_connection()
    
    if db_type == 'postgresql':
        cursor = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM categories ORDER BY nom')
    categories = cursor.fetchall()
    conn.close()
    
    return [dict(cat) for cat in categories]

@app.route('/')
def index():
    """Page d'accueil avec recherche et aperçu produits"""
    try:
        conn, db_type = get_db_connection()
        
        if db_type == 'postgresql':
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            placeholder = '%s'
        else:
            cursor = conn.cursor()
            placeholder = '?'
        
        # Paramètres de recherche
        recherche = request.args.get('q', '').strip()
        categorie = request.args.get('cat', '').strip()
        
        # Construction de la requête
        query = 'SELECT * FROM produits WHERE 1=1'
        params = []
        
        if recherche:
            query += f' AND (nom ILIKE {placeholder} OR code_barres LIKE {placeholder})'
            params.extend([f'%{recherche}%', f'%{recherche}%'])
        
        if categorie:
            query += f' AND categorie = {placeholder}'
            params.append(categorie)
        
        query += ' ORDER BY nom LIMIT 12'
        
        cursor.execute(query, params)
        produits = cursor.fetchall()
        
        # Stats rapides
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total = cursor.fetchone()['total'] if db_type == 'postgresql' else cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as ruptures FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()['ruptures'] if db_type == 'postgresql' else cursor.fetchone()[0]
        
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

@app.route('/produits')
def voir_produits():
    """Page complète des produits avec filtres avancés"""
    try:
        conn, db_type = get_db_connection()
        
        if db_type == 'postgresql':
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            placeholder = '%s'
        else:
            cursor = conn.cursor()
            placeholder = '?'
        
        # Paramètres de filtrage
        recherche = request.args.get('q', '').strip()
        categorie = request.args.get('cat', '').strip()
        stock_filter = request.args.get('stock', '').strip()
        prix_min = request.args.get('prix_min', '').strip()
        prix_max = request.args.get('prix_max', '').strip()
        tri = request.args.get('sort', 'nom').strip()
        ordre = request.args.get('order', 'asc').strip()
        
        # Construction de la requête
        query = 'SELECT * FROM produits WHERE 1=1'
        params = []
        
        if recherche:
            query += f' AND (nom ILIKE {placeholder} OR code_barres LIKE {placeholder})'
            params.extend([f'%{recherche}%', f'%{recherche}%'])
        
        if categorie:
            query += f' AND categorie = {placeholder}'
            params.append(categorie)
        
        if stock_filter == 'out':
            query += ' AND stock = 0'
        elif stock_filter == 'low':
            query += ' AND stock > 0 AND stock <= 5'
        elif stock_filter == 'ok':
            query += ' AND stock > 5'
        
        if prix_min:
            query += f' AND prix >= {placeholder}'
            params.append(float(prix_min))
        
        if prix_max:
            query += f' AND prix <= {placeholder}'
            params.append(float(prix_max))
        
        # Tri
        colonnes_tri = {
            'nom': 'nom',
            'prix': 'prix',
            'stock': 'stock',
            'categorie': 'categorie',
            'date': 'date_creation'
        }
        
        colonne_tri = colonnes_tri.get(tri, 'nom')
        ordre_sql = 'DESC' if ordre == 'desc' else 'ASC'
        query += f' ORDER BY {colonne_tri} {ordre_sql}'
        
        cursor.execute(query, params)
        produits = cursor.fetchall()
        
        # Statistiques
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total = cursor.fetchone()['total'] if db_type == 'postgresql' else cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as ruptures FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()['ruptures'] if db_type == 'postgresql' else cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as stock_faible FROM produits WHERE stock > 0 AND stock <= 5')
        stock_faible = cursor.fetchone()['stock_faible'] if db_type == 'postgresql' else cursor.fetchone()[0]
        
        conn.close()
        
        stats = {
            'total': total,
            'ruptures': ruptures,
            'stock_faible': stock_faible,
            'resultats': len(produits)
        }
        
        return render_template('produits.html', 
                             produits=[dict(p) for p in produits],
                             categories=get_categories(),
                             stats=stats,
                             filtres={
                                 'recherche': recherche,
                                 'categorie': categorie,
                                 'stock_filter': stock_filter,
                                 'prix_min': prix_min,
                                 'prix_max': prix_max,
                                 'tri': tri,
                                 'ordre': ordre
                             })
        
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter_produit():
    """Ajouter un nouveau produit"""
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '').strip()
            prix = float(request.form.get('prix', 0))
            stock = int(request.form.get('stock', 0))
            categorie = request.form.get('categorie', 'Autre').strip()
            code_barres = request.form.get('code_barres', '').strip()
            
            if not nom or not code_barres:
                return render_template('ajouter.html', 
                                     categories=get_categories(),
                                     error="Nom et code-barres obligatoires")
            
            # Génération automatique du code-barres si vide
            if not code_barres:
                code_barres = str(int(datetime.now().timestamp() * 1000))[-13:]
            
            conn, db_type = get_db_connection()
            
            if db_type == 'postgresql':
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (%s, %s, %s, %s, %s)',
                    (nom, code_barres, prix, stock, categorie)
                )
            else:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (?, ?, ?, ?, ?)',
                    (nom, code_barres, prix, stock, categorie)
                )
            
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
            
        except Exception as e:
            return render_template('ajouter.html', 
                                 categories=get_categories(),
                                 error=f"Erreur: {str(e)}")
    
    return render_template('ajouter.html', categories=get_categories())

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_produit(id):
    """Modifier un produit existant"""
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '').strip()
            prix = float(request.form.get('prix', 0))
            stock = int(request.form.get('stock', 0))
            categorie = request.form.get('categorie', 'Autre').strip()
            code_barres = request.form.get('code_barres', '').strip()
            
            conn, db_type = get_db_connection()
            
            if db_type == 'postgresql':
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE produits SET nom=%s, code_barres=%s, prix=%s, stock=%s, categorie=%s WHERE id=%s',
                    (nom, code_barres, prix, stock, categorie, id)
                )
            else:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE produits SET nom=?, code_barres=?, prix=?, stock=?, categorie=? WHERE id=?',
                    (nom, code_barres, prix, stock, categorie, id)
                )
            
            conn.commit()
            conn.close()
            
            return redirect(url_for('voir_produits'))
            
        except Exception as e:
            return render_template('error.html', error=str(e))
    
    # GET - Afficher le formulaire
    try:
        conn, db_type = get_db_connection()
        
        if db_type == 'postgresql':
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM produits WHERE id = %s', (id,))
        else:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM produits WHERE id = ?', (id,))
        
        produit = cursor.fetchone()
        conn.close()
        
        if not produit:
            return render_template('error.html', error="Produit non trouvé")
        
        return render_template('modifier.html', 
                             produit=dict(produit),
                             categories=get_categories())
        
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/supprimer/<int:id>')
def supprimer_produit(id):
    """Supprimer un produit"""
    try:
        conn, db_type = get_db_connection()
        
        if db_type == 'postgresql':
            cursor = conn.cursor()
            cursor.execute('DELETE FROM produits WHERE id = %s', (id,))
        else:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM produits WHERE id = ?', (id,))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        pass
    
    return redirect(url_for('voir_produits'))

@app.route('/scanner')
def scanner():
    """Page scanner"""
    return render_template('scanner.html')

@app.route('/scan', methods=['POST'])
def scan():
    """API de scan - décrément automatique du stock"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({'success': False, 'message': 'Code vide'})
        
        conn, db_type = get_db_connection()
        
        if db_type == 'postgresql':
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM produits WHERE code_barres = %s', (code,))
        else:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM produits WHERE code_barres = ?', (code,))
        
        produit = cursor.fetchone()
        
        if not produit:
            conn.close()
            return jsonify({'success': False, 'message': f'Produit non trouvé: {code}'})
        
        produit_dict = dict(produit)
        
        if produit_dict['stock'] <= 0:
            conn.close()
            return jsonify({
                'success': False, 
                'message': f'Rupture de stock: {produit_dict["nom"]}',
                'produit': produit_dict['nom']
            })
        
        # Décrémenter le stock
        nouveau_stock = produit_dict['stock'] - 1
        
        if db_type == 'postgresql':
            cursor.execute('UPDATE produits SET stock = %s WHERE id = %s', (nouveau_stock, produit_dict['id']))
        else:
            cursor.execute('UPDATE produits SET stock = ? WHERE id = ?', (nouveau_stock, produit_dict['id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'✅ {produit_dict["nom"]} scanné avec succès !',
            'produit': produit_dict['nom'],
            'nouveau_stock': nouveau_stock
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/codes-barres')
def codes_barres():
    """Générateur de codes-barres"""
    return render_template('codes_barres.html', produits=get_all_produits())

@app.route('/generer-code/<int:produit_id>')
def generer_code_barres(produit_id):
    """Génère et retourne l'image du code-barres"""
    try:
        conn, db_type = get_db_connection()
        
        if db_type == 'postgresql':
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('SELECT * FROM produits WHERE id = %s', (produit_id,))
        else:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM produits WHERE id = ?', (produit_id,))
        
        produit = cursor.fetchone()
        conn.close()
        
        if not produit:
            return "Produit non trouvé", 404
        
        produit_dict = dict(produit)
        
        # Génération du code-barres
        code128 = barcode.get_barcode_class('code128')
        code_barres = code128(produit_dict['code_barres'], writer=ImageWriter())
        
        buffer = BytesIO()
        code_barres.write(buffer)
        buffer.seek(0)
        
        return send_file(buffer, mimetype='image/png')
        
    except Exception as e:
        return f"Erreur: {str(e)}", 500

@app.route('/statistiques')
def statistiques():
    """Page statistiques"""
    try:
        conn, db_type = get_db_connection()
        
        if db_type == 'postgresql':
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        # Stats générales
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total = cursor.fetchone()['total'] if db_type == 'postgresql' else cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as ruptures FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()['ruptures'] if db_type == 'postgresql' else cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) as stock_faible FROM produits WHERE stock > 0 AND stock <= 5')
        stock_faible = cursor.fetchone()['stock_faible'] if db_type == 'postgresql' else cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(stock * prix) as valeur FROM produits')
        result = cursor.fetchone()
        valeur_stock = result['valeur'] if db_type == 'postgresql' else result[0]
        valeur_stock = valeur_stock or 0
        
        # Top catégories
        cursor.execute('''
            SELECT categorie, COUNT(*) as count, SUM(stock) as stock_total 
            FROM produits 
            GROUP BY categorie 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        top_categories = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_produits': total,
            'ruptures': ruptures,
            'stock_faible': stock_faible,
            'valeur_stock': round(valeur_stock, 2),
            'top_categories': [dict(cat) for cat in top_categories]
        }
        
        return render_template('statistiques.html', stats=stats, categories=get_categories())
        
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/export')
def export_csv():
    """Export CSV des produits"""
    try:
        produits = get_all_produits()
        
        if not produits:
            return render_template('error.html', error="Aucun produit à exporter")
        
        df = pd.DataFrame(produits)
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as f:
            df.to_csv(f.name, index=False, encoding='utf-8')
            temp_path = f.name
        
        return send_file(temp_path, 
                        as_attachment=True, 
                        download_name=f'produits_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                        mimetype='text/csv')
        
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/ruptures')
def ruptures():
    """Produits en rupture"""
    try:
        conn, db_type = get_db_connection()
        
        if db_type == 'postgresql':
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM produits WHERE stock = 0 ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('ruptures.html', 
                             produits=[dict(p) for p in produits],
                             categories=get_categories())
        
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/stock-faible')
def stock_faible():
    """Produits à stock faible"""
    try:
        conn, db_type = get_db_connection()
        
        if db_type == 'postgresql':
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM produits WHERE stock > 0 AND stock <= 5 ORDER BY stock ASC')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('stock_faible.html', 
                             produits=[dict(p) for p in produits],
                             categories=get_categories())
        
    except Exception as e:
        return render_template('error.html', error=str(e))

def get_all_produits():
    """Récupère tous les produits"""
    try:
        conn, db_type = get_db_connection()
        
        if db_type == 'postgresql':
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        
        return [dict(p) for p in produits]
    except:
        return []

if __name__ == '__main__':
    print("🚀 BOUTIQUE MOBILE - DÉPLOIEMENT RENDER")
    print("=" * 50)
    
    # Initialisation de la base de données
    try:
        init_database()
        print("✅ Base de données initialisée")
        
        if DATABASE_URL:
            print("🐘 PostgreSQL connecté (Render)")
        else:
            print("📁 SQLite connecté (Local)")
            
        produits = get_all_produits()
        print(f"📦 {len(produits)} produits en base")
        
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
    
    print("🌐 Application prête pour déploiement")
    print("📱 Toutes les fonctionnalités disponibles")
    
    # Lancement
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
