#!/usr/bin/env python3
"""
Application Flask - Gestion d'Inventaire
Version MySQL Local avec WAMP
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from mysql.connector import Error
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'inventaire_local_mysql_2024'

# Configuration MySQL Local (WAMP)
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # Mot de passe vide par défaut sur WAMP
    'database': 'gestion_inventaire',
    'charset': 'utf8mb4',
    'autocommit': True
}

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

def test_mysql_connection():
    """Tester la connexion MySQL"""
    try:
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) FROM produits")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"✅ MySQL connecté - Version: {version[0]}")
            print(f"📦 Produits en base: {count}")
            return True
        return False
    except Error as e:
        print(f"❌ Test connexion échoué: {e}")
        return False

# Routes de l'application
@app.route('/')
def index():
    """Page d'accueil avec liste des produits"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return "❌ Erreur de connexion MySQL", 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('simple.html', produits=produits)
        
    except Error as e:
        print(f"❌ Erreur index: {e}")
        return f"Erreur serveur: {e}", 500

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
        
        conn = get_mysql_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erreur connexion MySQL'})
            
        cursor = conn.cursor(dictionary=True)
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
        
    except Error as e:
        print(f"❌ ERREUR SCAN: {e}")
        return jsonify({'success': False, 'message': f'Erreur MySQL: {str(e)}'})

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
            
            conn = get_mysql_connection()
            if not conn:
                return render_template('ajouter_simple.html', 
                                     error='❌ Erreur de connexion MySQL')
            
            cursor = conn.cursor()
            
            # Vérifier l'unicité du code-barres
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
            
        except Error as e:
            return render_template('ajouter_simple.html', 
                                 error=f'❌ Erreur MySQL: {str(e)}')
    
    return render_template('ajouter_simple.html')

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    """Modifier un produit"""
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

@app.route('/codes-barres')
def codes_barres():
    """Page de génération de codes-barres"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return "Erreur de connexion MySQL", 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('codes_barres.html', produits=produits)
        
    except Error as e:
        return f"Erreur MySQL: {e}", 500

@app.route('/statistiques')
def statistiques():
    """Page de statistiques"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return "Erreur de connexion MySQL", 500
            
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM produits')
        total_produits = cursor.fetchone()[0]
        
        cursor.execute('SELECT SUM(stock) FROM produits')
        result = cursor.fetchone()
        stock_total = result[0] if result[0] else 0
        
        cursor.execute('SELECT COUNT(*) FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM produits WHERE stock <= 5 AND stock > 0')
        stock_faible = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(prix) FROM produits')
        result = cursor.fetchone()
        prix_moyen = float(result[0]) if result[0] else 0
        
        cursor.execute('SELECT * FROM produits ORDER BY stock ASC LIMIT 10')
        produits_faibles = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_produits': total_produits,
            'stock_total': stock_total,
            'ruptures': ruptures,
            'stock_faible': stock_faible,
            'prix_moyen': round(prix_moyen, 2),
            'produits_faibles': produits_faibles
        }
        
        return render_template('statistiques.html', stats=stats)
        
    except Error as e:
        return f"Erreur MySQL: {e}", 500

if __name__ == '__main__':
    print("🏠 APPLICATION MYSQL LOCAL - GESTION D'INVENTAIRE")
    print("=" * 60)
    print("🔧 Configuration WAMP:")
    print(f"   Host: {MYSQL_CONFIG['host']}")
    print(f"   Port: {MYSQL_CONFIG['port']}")
    print(f"   Database: {MYSQL_CONFIG['database']}")
    print(f"   User: {MYSQL_CONFIG['user']}")
    
    # Tester la connexion MySQL
    if test_mysql_connection():
        print("✅ MySQL prêt - Démarrage de l'application")
        print("🌐 Application disponible sur: http://localhost:5000")
        
        # Lancer l'app
        app.run(host='127.0.0.1', port=5000, debug=True)
    else:
        print("❌ Erreur connexion MySQL")
        print("🔧 Vérifiez que WAMP est démarré et que la base 'gestion_inventaire' existe")
