#!/usr/bin/env python3
"""
Application Flask - Gestion d'Inventaire
Version déploiement ultra-compatible
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'inventaire_deploy_2024'

# Base de données SQLite
DATABASE = 'inventaire.db'

def get_connection():
    """Connexion SQLite simple"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ Erreur connexion SQLite: {e}")
        return None

def init_simple_db():
    """Initialise la base avec des produits simples SEULEMENT si elle est vide"""
    try:
        conn = get_connection()
        if not conn:
            print("❌ Pas de connexion SQLite")
            return False
            
        cursor = conn.cursor()
        
        # Table simple
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                code_barres TEXT NOT NULL,
                prix REAL NOT NULL,
                stock INTEGER NOT NULL
            )
        ''')
        
        # VÉRIFIER SI DES PRODUITS EXISTENT DÉJÀ
        cursor.execute('SELECT COUNT(*) FROM produits')
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ Base de données existante avec {count} produits - CONSERVATION des données")
            conn.close()
            return True
        
        # SEULEMENT si la base est vide, ajouter des produits d'exemple
        print("📦 Base de données vide - Ajout des produits d'exemple")
        
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
            'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (?, ?, ?, ?)',
            produits_simples
        )
        
        conn.commit()
        conn.close()
        print(f"✅ {len(produits_simples)} produits d'exemple ajoutés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
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
        cursor.execute('SELECT id, nom, stock FROM produits WHERE code_barres = ?', (code_barres,))
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
        
        cursor.execute('UPDATE produits SET stock = ? WHERE id = ?', (nouveau_stock, produit['id']))
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
            cursor.execute('SELECT COUNT(*) FROM produits WHERE code_barres = ?', (code_barres,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return render_template('ajouter_simple.html', 
                                     error=f'⚠️ Le code-barres "{code_barres}" existe déjà')
            
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (?, ?, ?, ?)',
                (nom, code_barres, prix, stock)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
            
        except Exception as e:
            return render_template('ajouter_simple.html', 
                                 error=f'❌ Erreur lors de l\'ajout: {str(e)}')
    
    return render_template('ajouter_simple.html')

@app.route('/ajouter-lot', methods=['GET', 'POST'])
def ajouter_lot():
    """Ajouter plusieurs produits en une fois"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            produits = data.get('produits', [])
            
            if not produits:
                return jsonify({'success': False, 'message': 'Aucun produit à ajouter'})
            
            conn = get_connection()
            if not conn:
                return jsonify({'success': False, 'message': 'Erreur de connexion'})
            
            cursor = conn.cursor()
            produits_ajoutes = 0
            erreurs = []
            
            for i, produit in enumerate(produits):
                try:
                    nom = produit.get('nom', '').strip()
                    code_barres = produit.get('code_barres', '').strip()
                    prix = float(produit.get('prix', 0))
                    stock = int(produit.get('stock', 0))
                    
                    if not nom or not code_barres:
                        erreurs.append(f"Ligne {i+1}: Nom et code-barres obligatoires")
                        continue
                    
                    cursor.execute('SELECT COUNT(*) FROM produits WHERE code_barres = ?', (code_barres,))
                    if cursor.fetchone()[0] > 0:
                        erreurs.append(f"Ligne {i+1}: Code-barres '{code_barres}' déjà existant")
                        continue
                    
                    cursor.execute(
                        'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (?, ?, ?, ?)',
                        (nom, code_barres, prix, stock)
                    )
                    produits_ajoutes += 1
                    
                except Exception as e:
                    erreurs.append(f"Ligne {i+1}: {str(e)}")
            
            conn.commit()
            conn.close()
            
            message = f"✅ {produits_ajoutes} produits ajoutés"
            if erreurs:
                message += f" | ⚠️ {len(erreurs)} erreurs"
            
            return jsonify({
                'success': True,
                'message': message,
                'ajoutes': produits_ajoutes,
                'erreurs': erreurs
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})
    
    return render_template('ajouter_lot.html')

if __name__ == '__main__':
    print("🚀 APPLICATION DÉPLOIEMENT - GESTION D'INVENTAIRE")
    print("=" * 50)
    
    # Port pour hébergement
    port = int(os.environ.get('PORT', 5000))
    
    # Initialiser
    if init_simple_db():
        print("✅ Base SQLite prête")
        print(f"🌐 Port: {port}")
        
        # Lancer l'app
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("❌ Erreur initialisation")
