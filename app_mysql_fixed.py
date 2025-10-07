#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Flask CORRIGÉE de gestion d'inventaire avec MySQL
Version corrigée avec tous les templates professionnels
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
from datetime import datetime
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre_cle_secrete_ici'

# Configuration MySQL - MODIFIEZ SELON VOS PARAMÈTRES
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Votre utilisateur MySQL
    'password': '',  # Votre mot de passe MySQL (laissez vide si pas de mot de passe)
    'database': 'gestion_inventaire',  # LE NOM DE VOTRE BASE CRÉÉE DANS PHPMYADMIN
    'charset': 'utf8mb4'
}

def get_db_connection():
    """Retourne une connexion à la base de données MySQL"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Error as e:
        print(f"Erreur de connexion MySQL: {e}")
        return None

def init_db():
    """Initialise la base de données MySQL avec des données de test"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Créer la table si elle n'existe pas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                code_barres VARCHAR(50) UNIQUE NOT NULL,
                prix DECIMAL(10,2) NOT NULL,
                stock INT NOT NULL DEFAULT 0,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Vérifier s'il y a des données
        cursor.execute('SELECT COUNT(*) FROM produits')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Ajouter des produits d'exemple avec plus de variété
            produits_exemple = [
                ('Coca-Cola 33cl', '5449000000996', 1.50, 25),
                ('Pain de mie', '3274080005003', 2.30, 12),
                ('Lait 1L', '3033710074617', 1.20, 8),
                ('Yaourt nature x4', '3033490001001', 3.45, 15),
                ('Pommes Golden 1kg', '2000000000001', 2.80, 20),
                ('Smartphone iPhone 15', '1234567890123', 999.99, 3),
                ('Ordinateur portable HP', '9876543210987', 699.00, 5),
                ('Casque Bluetooth', '1111222233334', 89.99, 12),
                ('Clavier mécanique', '4444555566667', 129.50, 8),
                ('Souris gaming', '7777888899990', 45.99, 15)
            ]
            
            cursor.executemany(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (%s, %s, %s, %s)',
                produits_exemple
            )
            print(f"✅ {len(produits_exemple)} produits d'exemple ajoutés")
        
        conn.commit()
        conn.close()
        return True
        
    except Error as e:
        print(f"Erreur d'initialisation: {e}")
        return False

@app.route('/')
def index():
    """Page d'accueil - Liste des produits avec template professionnel"""
    try:
        conn = get_db_connection()
        if not conn:
            return "Erreur de connexion à la base de données", 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        
        # Convertir les Decimal en float pour l'affichage
        for produit in produits:
            produit['prix'] = float(produit['prix'])
        
        conn.close()
        
        print(f"📦 {len(produits)} produits récupérés pour l'affichage")
        return render_template('index_pro.html', produits=produits)
        
    except Error as e:
        print(f"Erreur dans index(): {e}")
        return f"Erreur: {e}", 500

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
        
        try:
            conn = get_db_connection()
            if not conn:
                return render_template('ajouter.html', error='Erreur de connexion à la base')
                
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (%s, %s, %s, %s)',
                (nom, code_barres, prix, stock)
            )
            conn.commit()
            conn.close()
            print(f"✅ Produit ajouté: {nom}")
            return redirect(url_for('index'))
            
        except mysql.connector.IntegrityError:
            return render_template('ajouter.html', error='Ce code-barres existe déjà!')
        except Error as e:
            return render_template('ajouter.html', error=f'Erreur: {e}')
    
    return render_template('ajouter.html')

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    """Modifier un produit existant"""
    try:
        conn = get_db_connection()
        if not conn:
            return redirect(url_for('index'))
            
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            nom = request.form['nom']
            code_barres = request.form['code_barres']
            prix = float(request.form['prix'])
            stock = int(request.form['stock'])
            
            try:
                cursor.execute(
                    'UPDATE produits SET nom=%s, code_barres=%s, prix=%s, stock=%s WHERE id=%s',
                    (nom, code_barres, prix, stock, id)
                )
                conn.commit()
                conn.close()
                return redirect(url_for('index'))
            except mysql.connector.IntegrityError:
                cursor.execute('SELECT * FROM produits WHERE id = %s', (id,))
                produit = cursor.fetchone()
                if produit:
                    produit['prix'] = float(produit['prix'])
                conn.close()
                return render_template('modifier.html', produit=produit, error='Ce code-barres existe déjà!')
        
        cursor.execute('SELECT * FROM produits WHERE id = %s', (id,))
        produit = cursor.fetchone()
        
        if produit:
            produit['prix'] = float(produit['prix'])
        
        conn.close()
        
        if produit is None:
            return redirect(url_for('index'))
        
        return render_template('modifier.html', produit=produit)
        
    except Error as e:
        return f"Erreur: {e}", 500

@app.route('/supprimer/<int:id>')
def supprimer(id):
    """Supprimer un produit"""
    try:
        conn = get_db_connection()
        if not conn:
            return redirect(url_for('index'))
            
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produits WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        print(f"🗑️ Produit ID {id} supprimé")
        return redirect(url_for('index'))
        
    except Error as e:
        return f"Erreur: {e}", 500

@app.route('/statistiques')
def statistiques():
    """Page des statistiques avec graphiques - VERSION CORRIGÉE"""
    try:
        conn = get_db_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les produits avec prix
        cursor.execute('SELECT nom, stock, prix FROM produits ORDER BY stock DESC')
        produits = cursor.fetchall()
        
        # Convertir les Decimal en float pour l'affichage
        for produit in produits:
            produit['prix'] = float(produit['prix'])
        
        # Statistiques générales
        cursor.execute('''
            SELECT 
                COUNT(*) as total_produits,
                SUM(stock) as total_stock,
                AVG(prix) as prix_moyen,
                SUM(CASE WHEN stock = 0 THEN 1 ELSE 0 END) as rupture_stock,
                SUM(CASE WHEN stock < 2 THEN 1 ELSE 0 END) as stock_faible
            FROM produits
        ''')
        stats = cursor.fetchone()
        
        # Convertir les Decimal en float pour les stats
        if stats['prix_moyen']:
            stats['prix_moyen'] = float(stats['prix_moyen'])
        
        conn.close()
        
        print(f"📊 Statistiques: {stats['total_produits']} produits, {len(produits)} avec prix")
        return render_template('statistiques_pro.html', produits=produits, stats=stats)
        
    except Error as e:
        print(f"Erreur dans statistiques(): {e}")
        return f"Erreur: {e}", 500

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """API pour traiter le scan d'un code-barres"""
    data = request.get_json()
    code_barres = data.get('code_barres', '').strip()
    
    if not code_barres:
        return jsonify({'success': False, 'message': 'Code-barres manquant'})
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erreur de connexion à la base'})
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produits WHERE code_barres = %s', (code_barres,))
        produit = cursor.fetchone()
        
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
        cursor.execute('UPDATE produits SET stock = %s WHERE id = %s', (nouveau_stock, produit['id']))
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
                'prix': float(produit['prix'])
            }
        })
        
    except Error as e:
        return jsonify({'success': False, 'message': f'Erreur: {e}'})

@app.route('/api/produits')
def api_produits():
    """API pour récupérer la liste des produits (pour les graphiques)"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify([])
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT nom, stock, prix FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        
        # Convertir Decimal en float pour JSON
        for produit in produits:
            produit['prix'] = float(produit['prix'])
        
        return jsonify(produits)
        
    except Error as e:
        print(f"Erreur API produits: {e}")
        return jsonify([])

@app.route('/export/csv')
def export_csv():
    """Exporter la liste des produits au format CSV"""
    try:
        conn = get_db_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        cursor = conn.cursor()
        cursor.execute('SELECT nom, code_barres, prix, stock FROM produits ORDER BY nom')
        produits = cursor.fetchall()
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
        
    except Error as e:
        return f"Erreur: {e}", 500

@app.route('/export/excel')
def export_excel():
    """Exporter la liste des produits au format Excel"""
    try:
        conn = get_db_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        cursor = conn.cursor()
        cursor.execute('SELECT nom, code_barres, prix, stock FROM produits ORDER BY nom')
        produits = cursor.fetchall()
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
        
    except Error as e:
        return f"Erreur: {e}", 500

if __name__ == '__main__':
    print("🔄 Initialisation de la base MySQL...")
    if init_db():
        print("✅ Base de données MySQL initialisée avec succès")
        print("📍 Application CORRIGÉE disponible sur: http://localhost:5003")
        print("🎨 Interface professionnelle avec animations")
        app.run(debug=True, host='0.0.0.0', port=5003)
    else:
        print("❌ Erreur d'initialisation de la base MySQL")
        print("Vérifiez vos paramètres de connexion dans MYSQL_CONFIG")
