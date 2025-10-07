"""
Application Flask - Version Déploiement avec SQLite
Optimisée pour hébergement gratuit (Render, Railway, etc.)
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

# Base de données SQLite (plus simple pour déploiement)
DATABASE = 'inventaire.db'

def get_connection():
    """Connexion SQLite simple"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        return conn
    except Exception as e:
        print(f"❌ Erreur connexion SQLite: {e}")
        return None

def initialiser_base_donnees():
    """Initialise la base SQLite avec des produits d'exemple"""
    try:
        conn = get_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Créer la table produits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                code_barres TEXT UNIQUE NOT NULL,
                prix REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0
            )
        ''')
        
        # Vérifier si des produits existent déjà
        cursor.execute('SELECT COUNT(*) FROM produits')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Ajouter des produits d'exemple
            produits_exemple = [
                ("Coca-Cola", "123456789", 1.50, 10),
                ("Pain", "987654321", 0.90, 0),
                ("Lait", "555666777", 1.20, 2),
                ("Yaourt", "444555666", 0.80, 1),
                ("Eau", "111222333", 0.60, 15),
                ("Biscuits", "777888999", 2.30, 8),
                ("Fromage", "333444555", 3.50, 3)
            ]
            
            cursor.executemany(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (?, ?, ?, ?)',
                produits_exemple
            )
            
            print(f"✅ {len(produits_exemple)} produits d'exemple ajoutés")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur initialisation base: {e}")
        return False

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
        elif nouveau_stock <= 2:
            message = f'⚠️ {produit["nom"]}: Stock CRITIQUE ({nouveau_stock} restants)'
        elif nouveau_stock <= 5:
            message = f'📦 {produit["nom"]}: Stock faible ({nouveau_stock} restants)'
        else:
            message = f'✅ {produit["nom"]}: Stock mis à jour ({nouveau_stock} restants)'
        
        return jsonify({
            'success': True,
            'message': message,
            'produit': produit['nom'],
            'nouveau_stock': nouveau_stock
        })
        
    except Exception as e:
        print(f"❌ Erreur scan: {e}")
        return jsonify({'success': False, 'message': 'Erreur lors du scan'})

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

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """Ajouter un produit"""
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '').strip()
            code_barres = request.form.get('code_barres', '').strip()
            prix = float(request.form.get('prix', 0))
            stock = int(request.form.get('stock', 0))
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (?, ?, ?, ?)',
                (nom, code_barres, prix, stock)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
            
        except Exception as e:
            print(f"❌ Erreur ajout: {e}")
            return redirect(url_for('index'))
    
    return render_template('ajouter_simple.html')

@app.route('/modifier/<int:produit_id>', methods=['GET', 'POST'])
def modifier(produit_id):
    """Modifier un produit"""
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '').strip()
            code_barres = request.form.get('code_barres', '').strip()
            prix = float(request.form.get('prix', 0))
            stock = int(request.form.get('stock', 0))
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE produits SET nom=?, code_barres=?, prix=?, stock=? WHERE id=?',
                (nom, code_barres, prix, stock, produit_id)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
            
        except Exception as e:
            print(f"❌ Erreur modification: {e}")
            return redirect(url_for('index'))
    
    # GET - Afficher le formulaire avec les données actuelles
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produits WHERE id = ?', (produit_id,))
        produit = cursor.fetchone()
        conn.close()
        
        if not produit:
            return redirect(url_for('index'))
            
        return render_template('modifier_simple.html', produit=produit)
        
    except Exception as e:
        print(f"❌ Erreur chargement produit: {e}")
        return redirect(url_for('index'))

@app.route('/supprimer/<int:produit_id>')
def supprimer(produit_id):
    """Supprimer un produit"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produits WHERE id = ?', (produit_id,))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
        
    except Exception as e:
        print(f"❌ Erreur suppression: {e}")
        return redirect(url_for('index'))

@app.route('/export/stock-faible')
def export_stock_faible():
    """Exporter les articles en stock faible"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produits WHERE stock <= 5 ORDER BY stock ASC, nom')
        produits = cursor.fetchall()
        conn.close()
        
        # Créer le CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow(['ID', 'Nom', 'Code-barres', 'Prix', 'Stock', 'Statut', 'Action Recommandée'])
        
        # Données
        for p in produits:
            if p['stock'] == 0:
                statut = "RUPTURE"
                action = "RÉAPPROVISIONNER URGENT"
            elif p['stock'] <= 2:
                statut = "CRITIQUE"
                action = "Réapprovisionner rapidement"
            else:
                statut = "FAIBLE"
                action = "Prévoir réapprovisionnement"
                
            writer.writerow([
                p['id'], p['nom'], p['code_barres'], 
                f"{p['prix']:.2f}€", p['stock'], statut, action
            ])
        
        # Préparer la réponse
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=stock_faible.csv'
        
        return response
        
    except Exception as e:
        print(f"❌ Erreur export: {e}")
        return redirect(url_for('index'))

@app.route('/export/rupture')
def export_rupture():
    """Exporter uniquement les articles en rupture"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produits WHERE stock = 0 ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        
        # Créer le CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow(['ID', 'Nom', 'Code-barres', 'Prix', 'Stock', 'Action'])
        
        # Données
        for p in produits:
            writer.writerow([
                p['id'], p['nom'], p['code_barres'], 
                f"{p['prix']:.2f}€", p['stock'], "RÉAPPROVISIONNER URGENT"
            ])
        
        # Préparer la réponse
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=ruptures_stock.csv'
        
        return response
        
    except Exception as e:
        print(f"❌ Erreur export rupture: {e}")
        return redirect(url_for('index'))

# Redirection pour compatibilité
@app.route('/qr-codes')
def qr_codes():
    """Redirection vers codes-barres"""
    return redirect(url_for('codes_barres'))

if __name__ == '__main__':
    print("🚀 APPLICATION DÉPLOIEMENT - GESTION D'INVENTAIRE")
    print("=" * 50)
    
    # Port dynamique pour hébergement
    port = int(os.environ.get('PORT', 5000))
    
    # Initialiser la base
    if initialiser_base_donnees():
        print("✅ Base SQLite initialisée")
        print(f"🌐 Démarrage sur port: {port}")
        
        # Mode production
        debug_mode = os.environ.get('RENDER') is None
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
    else:
        print("❌ Erreur initialisation base")
