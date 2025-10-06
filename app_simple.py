#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application SIMPLE de gestion d'inventaire - Version Ultra-Simplifiée
Garantie de fonctionnement - Affichage direct des produits
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, make_response
import mysql.connector
from mysql.connector import Error
import os
import csv
import io
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'inventaire_simple_2024'

# Configuration MySQL SIMPLE
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'gestion_inventaire',
    'charset': 'utf8mb4'
}

def get_connection():
    """Connexion MySQL simple"""
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except:
        return None

def generer_code_barre(code_barres):
    """Génère un code-barres traditionnel en base64"""
    try:
        # Utiliser le format Code128 qui accepte les chiffres et lettres
        code128 = barcode.get_barcode_class('code128')
        
        # Créer le code-barres avec ImageWriter pour PNG
        code_barre_obj = code128(code_barres, writer=ImageWriter())
        
        # Générer l'image en mémoire
        buffer = io.BytesIO()
        code_barre_obj.write(buffer)
        buffer.seek(0)
        
        # Convertir en base64 pour l'affichage HTML
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        print(f"❌ Erreur génération code-barres: {e}")
        return None

def reorganiser_ids():
    """Réorganise les IDs pour qu'ils soient séquentiels (1, 2, 3...)"""
    try:
        conn = get_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Récupérer tous les produits triés par ID
        cursor.execute('SELECT id, nom, code_barres, prix, stock FROM produits ORDER BY id')
        produits = cursor.fetchall()
        
        if not produits:
            conn.close()
            return True
        
        # Supprimer tous les produits
        cursor.execute('DELETE FROM produits')
        
        # Réinitialiser l'auto-increment
        cursor.execute('ALTER TABLE produits AUTO_INCREMENT = 1')
        
        # Réinsérer les produits (les IDs seront automatiquement 1, 2, 3...)
        for produit in produits:
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (%s, %s, %s, %s)',
                (produit[1], produit[2], produit[3], produit[4])
            )
        
        conn.commit()
        conn.close()
        print(f"✅ IDs réorganisés: {len(produits)} produits avec IDs séquentiels")
        return True
        
    except Exception as e:
        print(f"❌ Erreur réorganisation IDs: {e}")
        return False

def init_simple_db():
    """Initialise la base avec des produits simples"""
    try:
        conn = get_connection()
        if not conn:
            print("❌ Pas de connexion MySQL")
            return False
            
        cursor = conn.cursor()
        
        # Table simple
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                code_barres VARCHAR(50) NOT NULL,
                prix DECIMAL(10,2) NOT NULL,
                stock INT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # Vider et remplir avec des données simples
        cursor.execute('DELETE FROM produits')
        
        produits_simples = [
            ('Coca-Cola', '123456789', 1.50, 10),
            ('Pain', '987654321', 2.00, 0),  # Rupture de stock
            ('Lait', '555666777', 1.20, 2),  # Stock critique
            ('Pommes', '111222333', 3.50, 15),
            ('Yaourt', '444555666', 2.80, 1),  # Stock critique
            ('Biscuits', '777888999', 3.20, 0),  # Rupture de stock
            ('Eau', '333444555', 0.80, 4)  # Stock faible
        ]
        
        cursor.executemany(
            'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (%s, %s, %s, %s)',
            produits_simples
        )
        
        conn.commit()
        conn.close()
        print(f"✅ {len(produits_simples)} produits ajoutés")
        
        # S'assurer que les IDs sont séquentiels dès l'initialisation
        reorganiser_ids()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

@app.route('/')
def index():
    """Page principale SIMPLE avec tous les produits"""
    try:
        conn = get_connection()
        if not conn:
            return "Erreur de connexion MySQL", 500
            
        cursor = conn.cursor()
        cursor.execute('SELECT id, nom, code_barres, prix, stock FROM produits ORDER BY nom')
        produits_raw = cursor.fetchall()
        conn.close()
        
        # Convertir en format simple
        produits = []
        for p in produits_raw:
            produits.append({
                'id': p[0],
                'nom': p[1],
                'code_barres': p[2],
                'prix': float(p[3]),
                'stock': p[4]
            })
        
        print(f"📦 {len(produits)} produits récupérés pour affichage")
        
        # Debug - afficher les produits
        for p in produits:
            print(f"   - {p['nom']}: {p['stock']} unités")
        
        return render_template('simple.html', produits=produits)
        
    except Exception as e:
        print(f"❌ Erreur dans index(): {e}")
        return f"Erreur: {e}", 500

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """Ajouter un produit SIMPLE"""
    if request.method == 'POST':
        nom = request.form['nom']
        code_barres = request.form['code_barres']
        prix = float(request.form['prix'])
        stock = int(request.form['stock'])
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (%s, %s, %s, %s)',
                (nom, code_barres, prix, stock)
            )
            conn.commit()
            conn.close()
            
            # Réorganiser les IDs pour qu'ils restent séquentiels
            reorganiser_ids()
            
            return redirect(url_for('index'))
        except:
            return render_template('ajouter_simple.html', error='Erreur lors de l\'ajout')
    
    return render_template('ajouter_simple.html')

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    """Modifier un produit SIMPLE"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if request.method == 'POST':
            nom = request.form['nom']
            code_barres = request.form['code_barres']
            prix = float(request.form['prix'])
            stock = int(request.form['stock'])
            
            cursor.execute(
                'UPDATE produits SET nom=%s, code_barres=%s, prix=%s, stock=%s WHERE id=%s',
                (nom, code_barres, prix, stock, id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        
        # Récupérer le produit à modifier
        cursor.execute('SELECT id, nom, code_barres, prix, stock FROM produits WHERE id = %s', (id,))
        produit_raw = cursor.fetchone()
        conn.close()
        
        if not produit_raw:
            return redirect(url_for('index'))
        
        produit = {
            'id': produit_raw[0],
            'nom': produit_raw[1],
            'code_barres': produit_raw[2],
            'prix': float(produit_raw[3]),
            'stock': produit_raw[4]
        }
        
        return render_template('modifier_simple.html', produit=produit)
        
    except Exception as e:
        print(f"Erreur modification: {e}")
        return redirect(url_for('index'))

@app.route('/supprimer/<int:id>')
def supprimer(id):
    """Supprimer un produit"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produits WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        
        # Réorganiser les IDs après suppression pour maintenir la séquence
        reorganiser_ids()
        
    except Exception as e:
        print(f"❌ Erreur suppression: {e}")
    return redirect(url_for('index'))

@app.route('/scanner')
def scanner():
    """Page de scan simple"""
    return render_template('scanner_simple.html')

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Scanner automatique - Décrément immédiat du stock"""
    try:
        print("🔍 API SCAN APPELÉE")
        
        # Récupérer les données
        data = request.get_json()
        print(f"📥 Données reçues: {data}")
        
        code_barres = data.get('code_barres', '').strip()
        print(f"🔢 Code-barres extrait: '{code_barres}'")
        
        if not code_barres:
            print("❌ Code-barres vide")
            return jsonify({'success': False, 'message': 'Code-barres vide'})
        
        # Connexion base de données
        conn = get_connection()
        if not conn:
            print("❌ Erreur connexion MySQL")
            return jsonify({'success': False, 'message': 'Erreur connexion base de données'})
            
        cursor = conn.cursor()
        print(f"🔍 Recherche produit avec code: {code_barres}")
        
        cursor.execute('SELECT id, nom, stock FROM produits WHERE code_barres = %s', (code_barres,))
        produit = cursor.fetchone()
        print(f"📦 Produit trouvé: {produit}")
        
        if not produit:
            conn.close()
            print(f"❌ Aucun produit trouvé pour le code: {code_barres}")
            return jsonify({
                'success': False, 
                'message': f'❌ Produit non trouvé (Code: {code_barres})'
            })
        
        # Vérifier le stock avant décrément
        stock_actuel = produit[2]
        print(f"📊 Stock actuel: {stock_actuel}")
        
        if stock_actuel <= 0:
            conn.close()
            print(f"🚨 Stock déjà à zéro pour {produit[1]}")
            return jsonify({
                'success': False, 
                'message': f'🚨 {produit[1]} déjà en rupture de stock (Stock: {stock_actuel})'
            })
        
        # DÉCRÉMENTER AUTOMATIQUEMENT LE STOCK (-1)
        nouveau_stock = stock_actuel - 1
        print(f"⬇️ DÉCRÉMENT: {stock_actuel} → {nouveau_stock}")
        
        cursor.execute('UPDATE produits SET stock = %s WHERE id = %s', (nouveau_stock, produit[0]))
        rows_affected = cursor.rowcount
        print(f"💾 Lignes mises à jour: {rows_affected}")
        
        conn.commit()
        print("✅ Commit effectué")
        conn.close()
        
        # Messages avec émojis selon le niveau de stock
        if nouveau_stock == 0:
            message = f'🚨 {produit[1]}: RUPTURE DE STOCK ! (0 restant)'
            statut = 'rupture'
        elif nouveau_stock <= 2:
            message = f'⚠️ {produit[1]}: Stock CRITIQUE ({nouveau_stock} restants)'
            statut = 'critique'
        elif nouveau_stock <= 5:
            message = f'📦 {produit[1]}: Stock faible ({nouveau_stock} restants)'
            statut = 'faible'
        else:
            message = f'✅ {produit[1]}: Stock mis à jour ({nouveau_stock} restants)'
            statut = 'ok'
        
        print(f"📊 SCAN AUTOMATIQUE RÉUSSI: {code_barres} → {produit[1]} | Stock: {stock_actuel} → {nouveau_stock} (-1)")
        
        response_data = {
            'success': True,
            'message': message,
            'produit': produit[1],
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

@app.route('/export/stock-faible')
def export_stock_faible():
    """Exporter les articles en stock faible ou en rupture"""
    try:
        conn = get_connection()
        if not conn:
            return "Erreur de connexion MySQL", 500
            
        cursor = conn.cursor()
        
        # Récupérer les produits avec stock faible (≤ 5) ou en rupture (= 0)
        cursor.execute('''
            SELECT id, nom, code_barres, prix, stock,
                   CASE 
                       WHEN stock = 0 THEN 'RUPTURE'
                       WHEN stock <= 2 THEN 'CRITIQUE'
                       WHEN stock <= 5 THEN 'FAIBLE'
                       ELSE 'OK'
                   END as statut
            FROM produits 
            WHERE stock <= 5 
            ORDER BY stock ASC, nom ASC
        ''')
        
        produits_faibles = cursor.fetchall()
        conn.close()
        
        if not produits_faibles:
            return redirect(url_for('index'))
        
        # Créer le fichier CSV en mémoire
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # En-têtes du CSV
        writer.writerow([
            'ID', 'Nom du Produit', 'Code-barres', 'Prix (€)', 
            'Stock Actuel', 'Statut', 'Action Recommandée'
        ])
        
        # Données des produits
        for produit in produits_faibles:
            # Déterminer l'action recommandée
            if produit[4] == 0:  # stock = 0
                action = 'RÉAPPROVISIONNER IMMÉDIATEMENT'
            elif produit[4] <= 2:  # stock <= 2
                action = 'RÉAPPROVISIONNER RAPIDEMENT'
            else:  # stock <= 5
                action = 'Prévoir réapprovisionnement'
            
            writer.writerow([
                produit[0],  # ID
                produit[1],  # nom
                produit[2],  # code_barres
                f"{float(produit[3]):.2f}",  # prix
                produit[4],  # stock
                produit[5],  # statut
                action
            ])
        
        # Préparer la réponse
        output.seek(0)
        
        # Créer la réponse avec le bon type MIME
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        
        # Nom du fichier avec date et heure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'stock_faible_{timestamp}.csv'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        print(f"📊 Export généré: {len(produits_faibles)} articles en stock faible")
        
        return response
        
    except Exception as e:
        print(f"❌ Erreur export: {e}")
        return redirect(url_for('index'))

@app.route('/codes-barres')
def codes_barres():
    """Page d'affichage des codes-barres générés"""
    try:
        conn = get_connection()
        if not conn:
            return "Erreur de connexion MySQL", 500
            
        cursor = conn.cursor()
        cursor.execute('SELECT id, nom, code_barres, prix, stock FROM produits ORDER BY nom')
        produits_raw = cursor.fetchall()
        conn.close()
        
        # Générer les codes-barres pour chaque produit
        produits_avec_codes = []
        for p in produits_raw:
            code_barre_img = generer_code_barre(p[2])  # p[2] = code_barres
            produits_avec_codes.append({
                'id': p[0],
                'nom': p[1],
                'code_barres': p[2],
                'prix': float(p[3]),
                'stock': p[4],
                'code_barre_img': code_barre_img
            })
        
        print(f"📊 Codes-barres générés pour {len(produits_avec_codes)} produits")
        
        return render_template('codes_barres.html', produits=produits_avec_codes)
        
    except Exception as e:
        print(f"❌ Erreur codes-barres: {e}")
        return redirect(url_for('index'))

# Redirection QR codes vers codes-barres
@app.route('/qr-codes')
def qr_codes():
    """Redirection vers codes-barres"""
    return redirect(url_for('codes_barres'))

@app.route('/export/rupture')
def export_rupture():
    """Exporter uniquement les articles en rupture de stock"""
    try:
        conn = get_connection()
        if not conn:
            return "Erreur de connexion MySQL", 500
            
        cursor = conn.cursor()
        
        # Récupérer uniquement les produits en rupture (stock = 0)
        cursor.execute('''
            SELECT id, nom, code_barres, prix, stock
            FROM produits 
            WHERE stock = 0 
            ORDER BY nom ASC
        ''')
        
        produits_rupture = cursor.fetchall()
        conn.close()
        
        if not produits_rupture:
            return redirect(url_for('index'))
        
        # Créer le fichier CSV en mémoire
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # En-têtes du CSV
        writer.writerow([
            'ID', 'Nom du Produit', 'Code-barres', 'Prix (€)', 
            'Stock Actuel', 'Priorité', 'Date Export'
        ])
        
        # Données des produits en rupture
        date_export = datetime.now().strftime('%d/%m/%Y %H:%M')
        for produit in produits_rupture:
            writer.writerow([
                produit[0],  # ID
                produit[1],  # nom
                produit[2],  # code_barres
                f"{float(produit[3]):.2f}",  # prix
                produit[4],  # stock (0)
                'URGENT - RUPTURE',
                date_export
            ])
        
        # Préparer la réponse
        output.seek(0)
        
        # Créer la réponse avec le bon type MIME
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        
        # Nom du fichier avec date et heure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'articles_rupture_{timestamp}.csv'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        print(f"🚨 Export rupture généré: {len(produits_rupture)} articles en rupture")
        
        return response
        
    except Exception as e:
        print(f"❌ Erreur export rupture: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    print("🚀 APPLICATION SIMPLE - GESTION D'INVENTAIRE")
    print("=" * 50)
    
    if init_simple_db():
        print("✅ Base de données initialisée")
        print("📍 Application SIMPLE sur: http://localhost:5004")
        print("🎯 Interface ultra-simple et fonctionnelle")
        app.run(debug=True, host='0.0.0.0', port=5004)
    else:
        print("❌ Erreur d'initialisation")
