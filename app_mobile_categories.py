#!/usr/bin/env python3
"""
Application Flask - Boutique Réparation Mobile
Version avec Gestion Dynamique des Catégories
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import mysql.connector
from mysql.connector import Error
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mobile_shop_categories_2024'

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

# Catégories par défaut (peuvent être modifiées)
CATEGORIES_DEFAULT = [
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
    """Connexion MySQL avec création automatique de la base"""
    try:
        # D'abord, se connecter sans spécifier la base pour la créer si nécessaire
        config_no_db = MYSQL_CONFIG.copy()
        del config_no_db['database']
        
        conn = mysql.connector.connect(**config_no_db)
        cursor = conn.cursor()
        
        # Créer la base de données si elle n'existe pas
        cursor.execute("CREATE DATABASE IF NOT EXISTS gestion_inventaire")
        cursor.execute("USE gestion_inventaire")
        
        conn.close()
        
        # Maintenant se connecter à la base spécifique
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if conn.is_connected():
            return conn
        else:
            print("❌ Connexion MySQL échouée")
            return None
    except Error as e:
        print(f"❌ Erreur MySQL: {e}")
        return None

def init_database_with_categories():
    """Initialise la base avec table produits ET table catégories"""
    try:
        conn = get_mysql_connection()
        if not conn:
            print("❌ Impossible de se connecter à MySQL")
            return False
            
        cursor = conn.cursor()
        
        # Créer la table catégories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL UNIQUE,
                emoji VARCHAR(10) DEFAULT '📦',
                description TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                est_systeme BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Créer la table produits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                code_barres VARCHAR(100) NOT NULL UNIQUE,
                prix DECIMAL(10,2) NOT NULL,
                stock INT NOT NULL DEFAULT 0,
                categorie VARCHAR(100) DEFAULT 'Autre',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # Vérifier si les catégories par défaut existent
        cursor.execute('SELECT COUNT(*) FROM categories')
        count_categories = cursor.fetchone()[0]
        
        if count_categories == 0:
            print("🔧 Ajout des catégories par défaut...")
            # Ajouter les catégories par défaut avec emojis
            categories_avec_emojis = [
                ('Écran', '📱', 'Écrans de remplacement pour smartphones et tablettes'),
                ('Batterie', '🔋', 'Batteries de remplacement pour appareils mobiles'),
                ('Coque', '🛡️', 'Coques de protection pour smartphones'),
                ('Housse', '👜', 'Housses et étuis de protection'),
                ('Verre Trempé', '🔍', 'Films et verres de protection d\'écran'),
                ('Câble', '🔌', 'Câbles de charge et accessoires de connexion'),
                ('Outil', '🔧', 'Outils de réparation et démontage'),
                ('Accessoire', '📎', 'Accessoires divers pour mobiles'),
                ('Autre', '📦', 'Autres produits non classifiés')
            ]
            
            for nom, emoji, description in categories_avec_emojis:
                cursor.execute(
                    'INSERT INTO categories (nom, emoji, description, est_systeme) VALUES (%s, %s, %s, %s)',
                    (nom, emoji, description, True)
                )
            
            print(f"✅ {len(categories_avec_emojis)} catégories par défaut ajoutées")
        
        # Compter les produits
        cursor.execute('SELECT COUNT(*) FROM produits')
        count_produits = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"📂 Catégories: {count_categories}")
        print(f"📦 Produits: {count_produits}")
        print("✅ Base de données avec catégories initialisée")
        
        return True
        
    except Error as e:
        print(f"❌ Erreur initialisation: {e}")
        return False

def get_all_categories():
    """Récupère toutes les catégories (système + personnalisées)"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return CATEGORIES_DEFAULT
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM categories ORDER BY est_systeme DESC, nom ASC')
        categories = cursor.fetchall()
        conn.close()
        
        return categories
    except Error as e:
        print(f"❌ Erreur récupération catégories: {e}")
        return [{'nom': cat, 'emoji': '📦'} for cat in CATEGORIES_DEFAULT]

# Routes de l'application
@app.route('/')
def index():
    """Page d'accueil avec filtres et tri"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return "❌ Erreur de connexion MySQL - Vérifiez que WAMP est démarré", 500
            
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
        
        # Récupérer toutes les catégories disponibles
        categories = get_all_categories()
        
        return render_template('mobile_shop_categories.html', 
                             produits=produits,
                             categories=categories,
                             stats_categories=stats_categories,
                             tri_actuel=tri,
                             categorie_actuelle=categorie_filtre,
                             recherche_actuelle=recherche)
        
    except Error as e:
        print(f"❌ Erreur index: {e}")
        return f"Erreur serveur: {e}", 500

@app.route('/categories')
def gestion_categories():
    """Page de gestion des catégories"""
    try:
        categories = get_all_categories()
        
        # Compter les produits par catégorie
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT categorie, COUNT(*) as nb_produits 
                FROM produits 
                GROUP BY categorie
            """)
            usage_categories = {row['categorie']: row['nb_produits'] for row in cursor.fetchall()}
            conn.close()
        else:
            usage_categories = {}
        
        return render_template('gestion_categories.html', 
                             categories=categories,
                             usage_categories=usage_categories)
        
    except Error as e:
        return f"Erreur: {e}", 500

@app.route('/categories/creer')
def creer_categorie():
    """Page de création d'une nouvelle catégorie"""
    return render_template('creer_categorie.html')

@app.route('/categories/ajouter', methods=['POST'])
def ajouter_categorie():
    """Ajouter une nouvelle catégorie personnalisée"""
    try:
        nom = request.form.get('nom', '').strip()
        emoji = request.form.get('emoji', '📦').strip()
        description = request.form.get('description', '').strip()
        
        if not nom:
            return jsonify({'success': False, 'message': 'Le nom est obligatoire'})
        
        conn = get_mysql_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erreur de connexion'})
        
        cursor = conn.cursor()
        
        # Vérifier l'unicité
        cursor.execute('SELECT COUNT(*) FROM categories WHERE nom = %s', (nom,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return jsonify({'success': False, 'message': f'La catégorie "{nom}" existe déjà'})
        
        # Ajouter la catégorie
        cursor.execute(
            'INSERT INTO categories (nom, emoji, description, est_systeme) VALUES (%s, %s, %s, %s)',
            (nom, emoji, description, False)
        )
        conn.commit()
        
        # Récupérer l'ID de la nouvelle catégorie
        categorie_id = cursor.lastrowid
        conn.close()
        
        print(f"✅ NOUVELLE CATÉGORIE AJOUTÉE: {emoji} {nom}")
        
        return jsonify({
            'success': True, 
            'message': f'Catégorie "{nom}" ajoutée avec succès',
            'categorie': {'id': categorie_id, 'nom': nom, 'emoji': emoji}
        })
        
    except Error as e:
        print(f"❌ Erreur ajout catégorie: {e}")
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/categories/supprimer/<int:id>')
def supprimer_categorie(id):
    """Supprimer TOUTE catégorie (système ou personnalisée)"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return redirect(url_for('gestion_categories'))
        
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les infos de la catégorie
        cursor.execute('SELECT * FROM categories WHERE id = %s', (id,))
        categorie = cursor.fetchone()
        
        if not categorie:
            conn.close()
            return redirect(url_for('gestion_categories'))
        
        # SUPPRESSION AUTORISÉE POUR TOUTES LES CATÉGORIES
        # Vérifier s'il y a des produits dans cette catégorie
        cursor.execute('SELECT COUNT(*) FROM produits WHERE categorie = %s', (categorie['nom'],))
        nb_produits = cursor.fetchone()[0]
        
        if nb_produits > 0:
            # Déplacer les produits vers "Autre" ou créer "Autre" si nécessaire
            cursor.execute('SELECT COUNT(*) FROM categories WHERE nom = %s', ('Autre',))
            if cursor.fetchone()[0] == 0:
                # Créer la catégorie "Autre" si elle n'existe pas
                cursor.execute(
                    'INSERT INTO categories (nom, emoji, description, est_systeme) VALUES (%s, %s, %s, %s)',
                    ('Autre', '📦', 'Produits non classifiés', True)
                )
            
            cursor.execute('UPDATE produits SET categorie = %s WHERE categorie = %s', ('Autre', categorie['nom']))
            print(f"📦 {nb_produits} produits déplacés vers 'Autre'")
        
        # Supprimer la catégorie (même si système)
        cursor.execute('DELETE FROM categories WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        
        type_cat = "système" if categorie['est_systeme'] else "personnalisée"
        print(f"🗑️ CATÉGORIE {type_cat.upper()} SUPPRIMÉE: {categorie['nom']}")
        
        return redirect(url_for('gestion_categories'))
        
    except Error as e:
        print(f"❌ Erreur suppression catégorie: {e}")
        return redirect(url_for('gestion_categories'))

@app.route('/categories/modifier/<int:id>', methods=['GET', 'POST'])
def modifier_categorie(id):
    """Modifier TOUTE catégorie (système ou personnalisée)"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return redirect(url_for('gestion_categories'))
        
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            nouveau_nom = request.form.get('nom', '').strip()
            nouvel_emoji = request.form.get('emoji', '📦').strip()
            nouvelle_description = request.form.get('description', '').strip()
            
            if not nouveau_nom:
                return jsonify({'success': False, 'message': 'Le nom est obligatoire'})
            
            # Récupérer l'ancien nom pour mise à jour des produits
            cursor.execute('SELECT nom FROM categories WHERE id = %s', (id,))
            ancien_nom = cursor.fetchone()['nom']
            
            # Mettre à jour la catégorie
            cursor.execute(
                'UPDATE categories SET nom = %s, emoji = %s, description = %s WHERE id = %s',
                (nouveau_nom, nouvel_emoji, nouvelle_description, id)
            )
            
            # Mettre à jour tous les produits qui utilisent cette catégorie
            cursor.execute(
                'UPDATE produits SET categorie = %s WHERE categorie = %s',
                (nouveau_nom, ancien_nom)
            )
            
            conn.commit()
            conn.close()
            
            print(f"✅ CATÉGORIE MODIFIÉE: {ancien_nom} → {nouveau_nom}")
            return redirect(url_for('gestion_categories'))
        
        # GET - Afficher le formulaire
        cursor.execute('SELECT * FROM categories WHERE id = %s', (id,))
        categorie = cursor.fetchone()
        conn.close()
        
        if not categorie:
            return redirect(url_for('gestion_categories'))
        
        return render_template('modifier_categorie.html', categorie=categorie)
        
    except Error as e:
        print(f"❌ Erreur modification catégorie: {e}")
        return redirect(url_for('gestion_categories'))

@app.route('/api/suggestions/<categorie>')
def api_suggestions(categorie):
    """API pour récupérer les suggestions basées sur les produits existants de la catégorie"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return jsonify([])
        
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les produits existants de cette catégorie pour générer des suggestions
        cursor.execute(
            'SELECT nom FROM produits WHERE categorie = %s ORDER BY date_creation DESC LIMIT 10',
            (categorie,)
        )
        produits_existants = cursor.fetchall()
        
        # Générer des suggestions basées sur les produits existants
        suggestions = []
        for produit in produits_existants:
            nom = produit['nom']
            # Extraire des mots-clés pour suggestions
            mots = nom.split()
            if len(mots) >= 2:
                # Créer des variations
                base = ' '.join(mots[:-1])  # Tout sauf le dernier mot
                suggestions.append(f"{base} Pro")
                suggestions.append(f"{base} Plus")
                suggestions.append(f"{base} Mini")
                suggestions.append(f"{base} Max")
        
        # Supprimer les doublons et limiter
        suggestions = list(set(suggestions))[:8]
        
        conn.close()
        return jsonify(suggestions)
        
    except Error as e:
        print(f"❌ Erreur suggestions: {e}")
        return jsonify([])

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """Ajouter un produit avec catégories dynamiques"""
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '').strip()
            code_barres = request.form.get('code_barres', '').strip()
            prix = request.form.get('prix', '')
            stock = request.form.get('stock', '')
            categorie = request.form.get('categorie', 'Autre')
            
            # Validation des champs
            if not nom or not code_barres or not prix or not stock:
                return render_template('ajouter_mobile_categories.html', 
                                     categories=get_all_categories(),
                                     error='⚠️ Tous les champs sont obligatoires')
            
            try:
                prix = float(prix)
                stock = int(stock)
            except ValueError:
                return render_template('ajouter_mobile_categories.html', 
                                     categories=get_all_categories(),
                                     error='⚠️ Prix et stock doivent être des nombres valides')
            
            if prix < 0 or stock < 0:
                return render_template('ajouter_mobile_categories.html', 
                                     categories=get_all_categories(),
                                     error='⚠️ Prix et stock ne peuvent pas être négatifs')
            
            # Connexion à la base
            conn = get_mysql_connection()
            if not conn:
                return render_template('ajouter_mobile_categories.html', 
                                     categories=get_all_categories(),
                                     error='❌ Erreur de connexion MySQL')
            
            cursor = conn.cursor()
            
            # Vérifier l'unicité du code-barres
            cursor.execute('SELECT COUNT(*) FROM produits WHERE code_barres = %s', (code_barres,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return render_template('ajouter_mobile_categories.html', 
                                     categories=get_all_categories(),
                                     error=f'⚠️ Le code-barres "{code_barres}" existe déjà')
            
            # AJOUTER LE PRODUIT AVEC LA CATÉGORIE CHOISIE
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (%s, %s, %s, %s, %s)',
                (nom, code_barres, prix, stock, categorie)
            )
            conn.commit()
            
            # Récupérer l'ID du produit ajouté
            produit_id = cursor.lastrowid
            conn.close()
            
            print(f"✅ PRODUIT AJOUTÉ AVEC CATÉGORIE DYNAMIQUE - ID: {produit_id}")
            print(f"   Nom: {nom}")
            print(f"   Catégorie: {categorie}")
            print(f"   Code: {code_barres}")
            
            # Redirection vers la page principale
            return redirect(url_for('index'))
            
        except Error as e:
            print(f"❌ Erreur ajout produit: {e}")
            return render_template('ajouter_mobile_categories.html', 
                                 categories=get_all_categories(),
                                 error=f'❌ Erreur MySQL: {str(e)}')
    
    return render_template('ajouter_mobile_categories.html', categories=get_all_categories())

@app.route('/scanner')
def scanner():
    """Page de scan simple"""
    return render_template('scanner_mobile.html')

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Scanner automatique avec catégories dynamiques"""
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
        
        # Récupérer l'emoji de la catégorie
        cursor.execute('SELECT emoji FROM categories WHERE nom = %s', (produit['categorie'],))
        result = cursor.fetchone()
        emoji = result['emoji'] if result else '📦'
        
        conn.close()
        
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
            'prix': float(produit['prix'])
        })
        
    except Error as e:
        print(f"❌ ERREUR SCAN: {e}")
        return jsonify({'success': False, 'message': f'Erreur MySQL: {str(e)}'})

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    """Modifier un produit avec catégories dynamiques"""
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
            
            print(f"✅ Produit modifié avec catégorie: {nom} → {categorie}")
            return redirect(url_for('index'))
        
        cursor.execute('SELECT * FROM produits WHERE id = %s', (id,))
        produit = cursor.fetchone()
        conn.close()
        
        if not produit:
            return "Produit non trouvé", 404
            
        return render_template('modifier_mobile_categories.html', 
                             produit=produit, 
                             categories=get_all_categories())
        
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
        
        print(f"✅ Produit supprimé (ID: {id})")
        return redirect(url_for('index'))
        
    except Error as e:
        return f"Erreur MySQL: {e}", 500

@app.route('/api/categories')
def api_categories():
    """API pour récupérer toutes les catégories"""
    try:
        categories = get_all_categories()
        return jsonify([{
            'id': cat['id'],
            'nom': cat['nom'],
            'emoji': cat['emoji'],
            'est_systeme': cat['est_systeme']
        } for cat in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("📱 BOUTIQUE RÉPARATION MOBILE - CATÉGORIES DYNAMIQUES")
    print("=" * 60)
    print("🔧 Configuration:")
    print(f"   Host: {MYSQL_CONFIG['host']}")
    print(f"   Port: {MYSQL_CONFIG['port']}")
    print(f"   Database: {MYSQL_CONFIG['database']}")
    
    print("\n🚀 Initialisation avec catégories dynamiques...")
    
    # Initialiser la base avec catégories
    if init_database_with_categories():
        categories = get_all_categories()
        print(f"📂 Catégories disponibles: {len(categories)}")
        for cat in categories[:5]:  # Afficher les 5 premières
            print(f"   - {cat['emoji']} {cat['nom']}")
        if len(categories) > 5:
            print(f"   ... et {len(categories) - 5} autres")
        
        print("✅ Système prêt - Catégories dynamiques")
        print("🌐 Application disponible sur: http://localhost:5000")
        print("\n💡 Nouvelles fonctionnalités:")
        print("   1. /categories → Gérer vos catégories")
        print("   2. Ajouter des catégories personnalisées")
        print("   3. Supprimer les catégories non-système")
        print("   4. Choisir parmi toutes vos catégories")
        
        # Lancer l'app
        app.run(host='127.0.0.1', port=5000, debug=True)
    else:
        print("❌ Erreur d'initialisation")
        print("🔧 Vérifiez que WAMP est démarré (icône verte)")
