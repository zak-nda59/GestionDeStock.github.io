#!/usr/bin/env python3
"""
Application Flask - Boutique Réparation Mobile
Avec filtres, hiérarchie et catégories spécialisées
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from mysql.connector import Error
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mobile_shop_2024'

# Configuration MySQL Local (WAMP)
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'gestion_inventaire',
    'charset': 'utf8mb4',
    'autocommit': True
}

# Catégories spécialisées boutique mobile
CATEGORIES = [
    'Écran',
    'Batterie', 
    'Coque',
    'Housse',
    'Verre Trempé',
    'Câble',
    'Outil',
    'Accessoire',
    'Autre'
]

def get_mysql_connection():
    """Connexion MySQL locale"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if conn.is_connected():
            return conn
        else:
            print("❌ Connexion MySQL échouée")
            return None
    except Error as e:
        print(f"❌ Erreur MySQL: {e}")
        return None

@app.route('/')
def index():
    """Page d'accueil avec filtres et tri"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return "❌ Erreur de connexion MySQL", 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les paramètres de filtre
        tri = request.args.get('tri', 'nom_asc')
        categorie_filtre = request.args.get('categorie', 'toutes')
        recherche = request.args.get('recherche', '')
        
        # Construction de la requête SQL
        sql = "SELECT * FROM produits WHERE 1=1"
        params = []
        
        # Filtre par catégorie
        if categorie_filtre and categorie_filtre != 'toutes':
            sql += " AND categorie = %s"
            params.append(categorie_filtre)
        
        # Filtre par recherche
        if recherche:
            sql += " AND (nom LIKE %s OR code_barres LIKE %s)"
            params.extend([f'%{recherche}%', f'%{recherche}%'])
        
        # Tri
        if tri == 'nom_asc':
            sql += " ORDER BY nom ASC"
        elif tri == 'nom_desc':
            sql += " ORDER BY nom DESC"
        elif tri == 'prix_asc':
            sql += " ORDER BY prix ASC"
        elif tri == 'prix_desc':
            sql += " ORDER BY prix DESC"
        elif tri == 'stock_asc':
            sql += " ORDER BY stock ASC"
        elif tri == 'stock_desc':
            sql += " ORDER BY stock DESC"
        elif tri == 'categorie_asc':
            sql += " ORDER BY categorie ASC, nom ASC"
        else:
            sql += " ORDER BY nom ASC"
        
        cursor.execute(sql, params)
        produits = cursor.fetchall()
        
        # Statistiques par catégorie
        cursor.execute("""
            SELECT categorie, 
                   COUNT(*) as total,
                   SUM(stock) as stock_total,
                   COUNT(CASE WHEN stock = 0 THEN 1 END) as ruptures,
                   COUNT(CASE WHEN stock <= 5 AND stock > 0 THEN 1 END) as stock_faible
            FROM produits 
            GROUP BY categorie 
            ORDER BY total DESC
        """)
        stats_categories = cursor.fetchall()
        
        conn.close()
        
        return render_template('mobile_shop.html', 
                             produits=produits,
                             categories=CATEGORIES,
                             stats_categories=stats_categories,
                             tri_actuel=tri,
                             categorie_actuelle=categorie_filtre,
                             recherche_actuelle=recherche)
        
    except Error as e:
        print(f"❌ Erreur index: {e}")
        return f"Erreur serveur: {e}", 500

@app.route('/scanner')
def scanner():
    """Page de scan simple"""
    return render_template('scanner_mobile.html')

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Scanner automatique avec info catégorie"""
    try:
        data = request.get_json()
        code_barres = data.get('code_barres', '').strip()
        
        if not code_barres:
            return jsonify({'success': False, 'message': 'Code-barres vide'})
        
        conn = get_mysql_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erreur connexion MySQL'})
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produits WHERE code_barres = %s', (code_barres,))
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
                'message': f'🚨 {produit["nom"]} ({produit["categorie"]}) déjà en rupture de stock'
            })
        
        # DÉCRÉMENTER AUTOMATIQUEMENT LE STOCK (-1)
        nouveau_stock = stock_actuel - 1
        
        cursor.execute('UPDATE produits SET stock = %s WHERE id = %s', (nouveau_stock, produit['id']))
        conn.commit()
        conn.close()
        
        # Messages avec catégorie et émojis
        categorie_emoji = {
            'Écran': '📱',
            'Batterie': '🔋',
            'Coque': '🛡️',
            'Housse': '👜',
            'Verre Trempé': '🔍',
            'Câble': '🔌',
            'Outil': '🔧',
            'Accessoire': '📎',
            'Autre': '📦'
        }
        
        emoji = categorie_emoji.get(produit['categorie'], '📦')
        
        if nouveau_stock == 0:
            message = f'🚨 {emoji} {produit["nom"]} ({produit["categorie"]}): RUPTURE DE STOCK !'
            statut = 'rupture'
        elif nouveau_stock <= 2:
            message = f'⚠️ {emoji} {produit["nom"]} ({produit["categorie"]}): Stock CRITIQUE ({nouveau_stock})'
            statut = 'critique'
        elif nouveau_stock <= 5:
            message = f'📦 {emoji} {produit["nom"]} ({produit["categorie"]}): Stock faible ({nouveau_stock})'
            statut = 'faible'
        else:
            message = f'✅ {emoji} {produit["nom"]} ({produit["categorie"]}): Stock mis à jour ({nouveau_stock})'
            statut = 'ok'
        
        return jsonify({
            'success': True,
            'message': message,
            'produit': produit['nom'],
            'categorie': produit['categorie'],
            'stock_avant': stock_actuel,
            'nouveau_stock': nouveau_stock,
            'statut': statut,
            'prix': float(produit['prix']),
            'decrement': -1
        })
        
    except Error as e:
        print(f"❌ ERREUR SCAN: {e}")
        return jsonify({'success': False, 'message': f'Erreur MySQL: {str(e)}'})

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """Ajouter un produit avec catégorie"""
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '').strip()
            code_barres = request.form.get('code_barres', '').strip()
            prix = request.form.get('prix', '')
            stock = request.form.get('stock', '')
            categorie = request.form.get('categorie', 'Autre')
            
            if not nom or not code_barres or not prix or not stock:
                return render_template('ajouter_mobile.html', 
                                     categories=CATEGORIES,
                                     error='⚠️ Tous les champs sont obligatoires')
            
            try:
                prix = float(prix)
                stock = int(stock)
            except ValueError:
                return render_template('ajouter_mobile.html', 
                                     categories=CATEGORIES,
                                     error='⚠️ Prix et stock doivent être des nombres valides')
            
            if prix < 0 or stock < 0:
                return render_template('ajouter_mobile.html', 
                                     categories=CATEGORIES,
                                     error='⚠️ Prix et stock ne peuvent pas être négatifs')
            
            conn = get_mysql_connection()
            if not conn:
                return render_template('ajouter_mobile.html', 
                                     categories=CATEGORIES,
                                     error='❌ Erreur de connexion MySQL')
            
            cursor = conn.cursor()
            
            # Vérifier l'unicité du code-barres
            cursor.execute('SELECT COUNT(*) FROM produits WHERE code_barres = %s', (code_barres,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return render_template('ajouter_mobile.html', 
                                     categories=CATEGORIES,
                                     error=f'⚠️ Le code-barres "{code_barres}" existe déjà')
            
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (%s, %s, %s, %s, %s)',
                (nom, code_barres, prix, stock, categorie)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
            
        except Error as e:
            return render_template('ajouter_mobile.html', 
                                 categories=CATEGORIES,
                                 error=f'❌ Erreur MySQL: {str(e)}')
    
    return render_template('ajouter_mobile.html', categories=CATEGORIES)

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    """Modifier un produit avec catégorie"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return "Erreur de connexion MySQL", 500
            
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            nom = request.form.get('nom', '').strip()
            code_barres = request.form.get('code_barres', '').strip()
            prix = float(request.form.get('prix', 0))
            stock = int(request.form.get('stock', 0))
            categorie = request.form.get('categorie', 'Autre')
            
            cursor.execute(
                'UPDATE produits SET nom = %s, code_barres = %s, prix = %s, stock = %s, categorie = %s WHERE id = %s',
                (nom, code_barres, prix, stock, categorie, id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        
        cursor.execute('SELECT * FROM produits WHERE id = %s', (id,))
        produit = cursor.fetchone()
        conn.close()
        
        if not produit:
            return "Produit non trouvé", 404
            
        return render_template('modifier_mobile.html', produit=produit, categories=CATEGORIES)
        
    except Error as e:
        return f"Erreur MySQL: {e}", 500

@app.route('/supprimer/<int:id>')
def supprimer(id):
    """Supprimer un produit"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return "Erreur de connexion MySQL", 500
            
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produits WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
        
    except Error as e:
        return f"Erreur MySQL: {e}", 500

@app.route('/api/produits-par-categorie/<categorie>')
def api_produits_par_categorie(categorie):
    """API pour récupérer les produits d'une catégorie"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return jsonify({'error': 'Erreur connexion'}), 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT nom, code_barres FROM produits WHERE categorie = %s ORDER BY nom', (categorie,))
        produits = cursor.fetchall()
        conn.close()
        
        return jsonify(produits)
        
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/statistiques')
def statistiques():
    """Statistiques détaillées par catégorie"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return "Erreur de connexion MySQL", 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Stats générales
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total_produits = cursor.fetchone()['total']
        
        cursor.execute('SELECT SUM(stock) as total FROM produits')
        result = cursor.fetchone()
        stock_total = result['total'] if result['total'] else 0
        
        cursor.execute('SELECT COUNT(*) as total FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM produits WHERE stock <= 5 AND stock > 0')
        stock_faible = cursor.fetchone()['total']
        
        cursor.execute('SELECT AVG(prix) as moyenne FROM produits')
        result = cursor.fetchone()
        prix_moyen = float(result['moyenne']) if result['moyenne'] else 0
        
        # Stats par catégorie
        cursor.execute("""
            SELECT categorie,
                   COUNT(*) as total_produits,
                   SUM(stock) as stock_total,
                   COUNT(CASE WHEN stock = 0 THEN 1 END) as ruptures,
                   COUNT(CASE WHEN stock <= 5 AND stock > 0 THEN 1 END) as stock_faible,
                   AVG(prix) as prix_moyen,
                   MIN(prix) as prix_min,
                   MAX(prix) as prix_max
            FROM produits 
            GROUP BY categorie 
            ORDER BY total_produits DESC
        """)
        stats_categories = cursor.fetchall()
        
        # Top produits par catégorie
        cursor.execute("""
            SELECT * FROM produits 
            WHERE stock <= 5 
            ORDER BY categorie, stock ASC 
            LIMIT 20
        """)
        produits_attention = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_produits': total_produits,
            'stock_total': stock_total,
            'ruptures': ruptures,
            'stock_faible': stock_faible,
            'prix_moyen': round(prix_moyen, 2),
            'stats_categories': stats_categories,
            'produits_attention': produits_attention
        }
        
        return render_template('statistiques_mobile.html', stats=stats)
        
    except Error as e:
        return f"Erreur MySQL: {e}", 500

if __name__ == '__main__':
    print("📱 BOUTIQUE RÉPARATION MOBILE - GESTION D'INVENTAIRE")
    print("=" * 60)
    print("🔧 Configuration WAMP:")
    print(f"   Host: {MYSQL_CONFIG['host']}")
    print(f"   Port: {MYSQL_CONFIG['port']}")
    print(f"   Database: {MYSQL_CONFIG['database']}")
    print("📱 Catégories disponibles:")
    for cat in CATEGORIES:
        print(f"   - {cat}")
    
    # Lancer l'app
    app.run(host='127.0.0.1', port=5000, debug=True)
