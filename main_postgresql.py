#!/usr/bin/env python3
"""
Application Flask - Gestion d'Inventaire
Version PostgreSQL pour Render
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import csv
import io
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'inventaire_deploy_2024'

# Configuration PostgreSQL pour Render
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    """Connexion PostgreSQL"""
    try:
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return conn
        else:
            print("❌ DATABASE_URL non configurée")
            return None
    except Exception as e:
        print(f"❌ Erreur connexion PostgreSQL: {e}")
        return None

def init_postgresql_db():
    """Initialise la base PostgreSQL"""
    try:
        conn = get_connection()
        if not conn:
            print("❌ Pas de connexion PostgreSQL")
            return False
            
        cursor = conn.cursor()
        
        # Créer la table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                code_barres VARCHAR(100) NOT NULL UNIQUE,
                prix DECIMAL(10,2) NOT NULL,
                stock INTEGER NOT NULL,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Vérifier si des produits existent
        cursor.execute('SELECT COUNT(*) FROM produits')
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Base PostgreSQL existante avec {count} produits")
            conn.close()
            return True
        
        # Ajouter des produits d'exemple
        print("📦 Base PostgreSQL vide - Ajout des produits d'exemple")
        
        produits_simples = [
            ('Coca-Cola', '123456789', 1.50, 10),
            ('Pain', '987654321', 2.00, 0),
            ('Lait', '555666777', 1.20, 2),
            ('Pommes', '111222333', 3.50, 15),
            ('Yaourt', '444555666', 2.80, 1),
            ('Biscuits', '777888999', 3.20, 0),
            ('Eau', '333444555', 0.80, 4)
        ]
        
        cursor.executemany(
            'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (%s, %s, %s, %s)',
            produits_simples
        )
        
        conn.commit()
        conn.close()
        print(f"✅ {len(produits_simples)} produits d'exemple ajoutés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur initialisation PostgreSQL: {e}")
        return False

# Routes de l'application
@app.route('/')
def index():
    """Page d'accueil avec liste des produits"""
    try:
        conn = get_connection()
        if not conn:
            return "Erreur de connexion base de données", 500
            
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('simple.html', produits=produits)
        
    except Exception as e:
        print(f"❌ Erreur index: {e}")
        return "Erreur serveur", 500

@app.route('/scanner')
def scanner():
    """Page de scan simple"""
    return render_template('scanner_simple.html')

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Scanner automatique - Décrément immédiat du stock"""
    try:
        data = request.get_json()
        code_barres = data.get('code_barres', '').strip()
        
        if not code_barres:
            return jsonify({'success': False, 'message': 'Code-barres vide'})
        
        conn = get_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erreur connexion base de données'})
            
        cursor = conn.cursor()
        cursor.execute('SELECT id, nom, stock FROM produits WHERE code_barres = %s', (code_barres,))
        produit = cursor.fetchone()
        
        if not produit:
            conn.close()
            return jsonify({
                'success': False, 
                'message': f'❌ Produit non trouvé (Code: {code_barres})'
            })
        
        stock_actuel = produit['stock']
        
        if stock_actuel <= 0:
            conn.close()
            return jsonify({
                'success': False, 
                'message': f'🚨 {produit["nom"]} déjà en rupture de stock'
            })
        
        # DÉCRÉMENTER AUTOMATIQUEMENT LE STOCK (-1)
        nouveau_stock = stock_actuel - 1
        
        cursor.execute('UPDATE produits SET stock = %s WHERE id = %s', (nouveau_stock, produit['id']))
        conn.commit()
        conn.close()
        
        # Messages avec émojis
        if nouveau_stock == 0:
            message = f'🚨 {produit["nom"]}: RUPTURE DE STOCK ! (0 restant)'
            statut = 'rupture'
        elif nouveau_stock <= 2:
            message = f'⚠️ {produit["nom"]}: Stock CRITIQUE ({nouveau_stock} restants)'
            statut = 'critique'
        elif nouveau_stock <= 5:
            message = f'📦 {produit["nom"]}: Stock faible ({nouveau_stock} restants)'
            statut = 'faible'
        else:
            message = f'✅ {produit["nom"]}: Stock mis à jour ({nouveau_stock} restants)'
            statut = 'ok'
        
        return jsonify({
            'success': True,
            'message': message,
            'produit': produit['nom'],
            'stock_avant': stock_actuel,
            'nouveau_stock': nouveau_stock,
            'statut': statut,
            'decrement': -1
        })
        
    except Exception as e:
        print(f"❌ ERREUR SCAN: {e}")
        return jsonify({'success': False, 'message': f'Erreur lors du scan: {str(e)}'})

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """Ajouter un produit"""
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '').strip()
            code_barres = request.form.get('code_barres', '').strip()
            prix = request.form.get('prix', '')
            stock = request.form.get('stock', '')
            
            if not nom or not code_barres or not prix or not stock:
                return render_template('ajouter_simple.html', 
                                     error='⚠️ Tous les champs sont obligatoires')
            
            try:
                prix = float(prix)
                stock = int(stock)
            except ValueError:
                return render_template('ajouter_simple.html', 
                                     error='⚠️ Prix et stock doivent être des nombres valides')
            
            if prix < 0 or stock < 0:
                return render_template('ajouter_simple.html', 
                                     error='⚠️ Prix et stock ne peuvent pas être négatifs')
            
            conn = get_connection()
            if not conn:
                return render_template('ajouter_simple.html', 
                                     error='❌ Erreur de connexion à la base de données')
            
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM produits WHERE code_barres = %s', (code_barres,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return render_template('ajouter_simple.html', 
                                     error=f'⚠️ Le code-barres "{code_barres}" existe déjà')
            
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (%s, %s, %s, %s)',
                (nom, code_barres, prix, stock)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
            
        except Exception as e:
            return render_template('ajouter_simple.html', 
                                 error=f'❌ Erreur lors de l\'ajout: {str(e)}')
    
    return render_template('ajouter_simple.html')

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    """Modifier un produit"""
    try:
        conn = get_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        cursor = conn.cursor()
        
        if request.method == 'POST':
            nom = request.form.get('nom', '').strip()
            code_barres = request.form.get('code_barres', '').strip()
            prix = float(request.form.get('prix', 0))
            stock = int(request.form.get('stock', 0))
            
            cursor.execute(
                'UPDATE produits SET nom = %s, code_barres = %s, prix = %s, stock = %s WHERE id = %s',
                (nom, code_barres, prix, stock, id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        
        cursor.execute('SELECT * FROM produits WHERE id = %s', (id,))
        produit = cursor.fetchone()
        conn.close()
        
        if not produit:
            return "Produit non trouvé", 404
            
        return render_template('modifier_simple.html', produit=produit)
        
    except Exception as e:
        return f"Erreur: {e}", 500

@app.route('/supprimer/<int:id>')
def supprimer(id):
    """Supprimer un produit"""
    try:
        conn = get_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produits WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
        
    except Exception as e:
        return f"Erreur: {e}", 500

@app.route('/codes-barres')
def codes_barres():
    """Page de génération de codes-barres"""
    try:
        conn = get_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('codes_barres.html', produits=produits)
        
    except Exception as e:
        return f"Erreur: {e}", 500

@app.route('/statistiques')
def statistiques():
    """Page de statistiques"""
    try:
        conn = get_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM produits')
        total_produits = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(stock) FROM produits')
        stock_total = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM produits WHERE stock <= 5 AND stock > 0')
        stock_faible = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(prix) FROM produits')
        prix_moyen = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT * FROM produits ORDER BY stock ASC LIMIT 10')
        produits_faibles = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_produits': total_produits,
            'stock_total': stock_total,
            'ruptures': ruptures,
            'stock_faible': stock_faible,
            'prix_moyen': round(float(prix_moyen), 2),
            'produits_faibles': produits_faibles
        }
        
        return render_template('statistiques.html', stats=stats)
        
    except Exception as e:
        return f"Erreur: {e}", 500

if __name__ == '__main__':
    print("🚀 APPLICATION POSTGRESQL - GESTION D'INVENTAIRE")
    print("=" * 50)
    
    # Port pour hébergement
    port = int(os.environ.get('PORT', 5000))
    
    # Initialiser PostgreSQL
    if init_postgresql_db():
        print("✅ Base PostgreSQL prête")
        print(f"🌐 Port: {port}")
        
        # Lancer l'app
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("❌ Erreur initialisation PostgreSQL")
