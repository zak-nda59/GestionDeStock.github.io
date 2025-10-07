"""
Application Flask - Version Déploiement avec SQLite
Version corrigée avec scanner précis et base persistante
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, make_response
import sqlite3
import os
import csv
import io
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
import base64

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

def generer_code_barre(code_barres):
    """Génère un code-barres traditionnel en base64"""
    try:
        code128 = barcode.get_barcode_class('code128')
        code_barre_obj = code128(code_barres, writer=ImageWriter())
        
        buffer = io.BytesIO()
        code_barre_obj.write(buffer)
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"❌ Erreur génération code-barres: {e}")
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

def sauvegarder_base():
    """Crée une sauvegarde de la base de données"""
    try:
        conn = get_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produits ORDER BY id')
        produits = cursor.fetchall()
        conn.close()
        
        # Créer le fichier de sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f'backup_produits_{timestamp}.sql'
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write("-- Sauvegarde automatique de la base de données\n")
            f.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("DELETE FROM produits;\n\n")
            
            for p in produits:
                f.write(f"INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('{p['nom']}', '{p['code_barres']}', {p['prix']}, {p['stock']});\n")
        
        print(f"💾 Sauvegarde créée: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
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
        print("🔍 API SCAN APPELÉE")
        
        data = request.get_json()
        print(f"📥 Données reçues: {data}")
        
        code_barres = data.get('code_barres', '').strip()
        print(f"🔢 Code-barres extrait: '{code_barres}'")
        
        if not code_barres:
            print("❌ Code-barres vide")
            return jsonify({'success': False, 'message': 'Code-barres vide'})
        
        conn = get_connection()
        if not conn:
            print("❌ Erreur connexion SQLite")
            return jsonify({'success': False, 'message': 'Erreur connexion base de données'})
            
        cursor = conn.cursor()
        print(f"🔍 Recherche produit avec code: {code_barres}")
        
        cursor.execute('SELECT id, nom, stock FROM produits WHERE code_barres = ?', (code_barres,))
        produit = cursor.fetchone()
        print(f"📦 Produit trouvé: {dict(produit) if produit else None}")
        
        if not produit:
            conn.close()
            print(f"❌ Aucun produit trouvé pour le code: {code_barres}")
            return jsonify({
                'success': False, 
                'message': f'❌ Produit non trouvé (Code: {code_barres})'
            })
        
        stock_actuel = produit['stock']
        print(f"📊 Stock actuel: {stock_actuel}")
        
        if stock_actuel <= 0:
            conn.close()
            print(f"🚨 Stock déjà à zéro pour {produit['nom']}")
            return jsonify({
                'success': False, 
                'message': f'🚨 {produit["nom"]} déjà en rupture de stock'
            })
        
        # DÉCRÉMENTER AUTOMATIQUEMENT LE STOCK (-1)
        nouveau_stock = stock_actuel - 1
        print(f"⬇️ DÉCRÉMENT: {stock_actuel} → {nouveau_stock}")
        
        cursor.execute('UPDATE produits SET stock = ? WHERE id = ?', (nouveau_stock, produit['id']))
        rows_affected = cursor.rowcount
        print(f"💾 Lignes mises à jour: {rows_affected}")
        
        conn.commit()
        print("✅ Commit effectué")
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
        
        print(f"📊 SCAN AUTOMATIQUE RÉUSSI: {code_barres} → {produit['nom']} | Stock: {stock_actuel} → {nouveau_stock} (-1)")
        
        response_data = {
            'success': True,
            'message': message,
            'produit': produit['nom'],
            'stock_avant': stock_actuel,
            'nouveau_stock': nouveau_stock,
            'statut': statut,
            'decrement': -1
        }
        print(f"📤 Réponse envoyée: {response_data}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ ERREUR SCAN AUTOMATIQUE: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Erreur lors du scan: {str(e)}'})

@app.route('/codes-barres')
def codes_barres():
    """Page d'affichage des codes-barres générés"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produits ORDER BY nom')
        produits_raw = cursor.fetchall()
        conn.close()
        
        # Générer les codes-barres
        produits_avec_codes = []
        for p in produits_raw:
            code_barre_img = generer_code_barre(p['code_barres'])
            produits_avec_codes.append({
                'id': p['id'],
                'nom': p['nom'],
                'code_barres': p['code_barres'],
                'prix': float(p['prix']),
                'stock': p['stock'],
                'code_barre_img': code_barre_img
            })
        
        return render_template('codes_barres.html', produits=produits_avec_codes)
        
    except Exception as e:
        print(f"❌ Erreur codes-barres: {e}")
        return redirect(url_for('index'))

@app.route('/sauvegarde')
def creer_sauvegarde():
    """Créer une sauvegarde manuelle de la base de données"""
    try:
        if sauvegarder_base():
            return jsonify({
                'success': True, 
                'message': '💾 Sauvegarde créée avec succès!'
            })
        else:
            return jsonify({
                'success': False, 
                'message': '❌ Erreur lors de la sauvegarde'
            })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'❌ Erreur: {str(e)}'
        })

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
