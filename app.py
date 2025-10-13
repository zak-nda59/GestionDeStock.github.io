#!/usr/bin/env python3
"""
Application Flask - Boutique Réparation Mobile
Version Production pour Render avec PostgreSQL
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import os
import csv
import io
from datetime import datetime

# Configuration pour production/développement
if os.environ.get('DATABASE_URL'):
    # Production sur Render avec PostgreSQL
    import psycopg2
    from psycopg2.extras import RealDictCursor
    import urllib.parse as urlparse
else:
    # Développement local avec MySQL
    import mysql.connector
    from mysql.connector import Error

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mobile_shop_render_2024')

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

def get_database_connection():
    """Connexion base de données (PostgreSQL en prod, MySQL en dev)"""
    try:
        if os.environ.get('DATABASE_URL'):
            # Production PostgreSQL sur Render
            database_url = os.environ['DATABASE_URL']
            url = urlparse.urlparse(database_url)
            
            conn = psycopg2.connect(
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port
            )
            return conn
        else:
            # Développement MySQL local
            conn = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='',
                database='gestion_inventaire',
                charset='utf8mb4',
                autocommit=True
            )
            return conn
    except Exception as e:
        print(f"❌ Erreur connexion base: {e}")
        return None

def init_database():
    """Initialise la base de données selon l'environnement"""
    try:
        conn = get_database_connection()
        if not conn:
            print("❌ Impossible de se connecter à la base")
            return False
            
        if os.environ.get('DATABASE_URL'):
            # PostgreSQL
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS produits (
                    id SERIAL PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    code_barres VARCHAR(100) NOT NULL UNIQUE,
                    prix DECIMAL(10,2) NOT NULL,
                    stock INTEGER NOT NULL DEFAULT 0,
                    categorie VARCHAR(50) DEFAULT 'Autre',
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        else:
            # MySQL
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS gestion_inventaire")
            cursor.execute("USE gestion_inventaire")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS produits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(255) NOT NULL,
                    code_barres VARCHAR(100) NOT NULL UNIQUE,
                    prix DECIMAL(10,2) NOT NULL,
                    stock INT NOT NULL DEFAULT 0,
                    categorie VARCHAR(50) DEFAULT 'Autre',
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
        
        # Compter les produits
        cursor.execute('SELECT COUNT(*) FROM produits')
        count = cursor.fetchone()[0]
        
        conn.close()
        
        env = "Production (PostgreSQL)" if os.environ.get('DATABASE_URL') else "Développement (MySQL)"
        print(f"✅ Base initialisée - {env}")
        print(f"📦 Produits: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return False

# Routes de l'application
@app.route('/')
def index():
    """Page d'accueil avec filtres et tri"""
    try:
        conn = get_database_connection()
        if not conn:
            return "❌ Erreur de connexion base de données", 500
            
        if os.environ.get('DATABASE_URL'):
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
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
            if os.environ.get('DATABASE_URL'):
                sql += " AND categorie = %s"
            else:
                sql += " AND categorie = %s"
            params.append(categorie_filtre)
        
        # Filtre par recherche
        if recherche:
            if os.environ.get('DATABASE_URL'):
                sql += " AND (nom ILIKE %s OR code_barres ILIKE %s)"
            else:
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
        
    except Exception as e:
        print(f"❌ Erreur index: {e}")
        return f"Erreur serveur: {e}", 500

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """Ajouter un produit avec sauvegarde permanente"""
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '').strip()
            code_barres = request.form.get('code_barres', '').strip()
            prix = request.form.get('prix', '')
            stock = request.form.get('stock', '')
            categorie = request.form.get('categorie', 'Autre')
            
            # Validation des champs
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
            
            # Connexion à la base
            conn = get_database_connection()
            if not conn:
                return render_template('ajouter_mobile.html', 
                                     categories=CATEGORIES,
                                     error='❌ Erreur de connexion base de données')
            
            cursor = conn.cursor()
            
            # Vérifier l'unicité du code-barres
            if os.environ.get('DATABASE_URL'):
                cursor.execute('SELECT COUNT(*) FROM produits WHERE code_barres = %s', (code_barres,))
            else:
                cursor.execute('SELECT COUNT(*) FROM produits WHERE code_barres = %s', (code_barres,))
            
            if cursor.fetchone()[0] > 0:
                conn.close()
                return render_template('ajouter_mobile.html', 
                                     categories=CATEGORIES,
                                     error=f'⚠️ Le code-barres "{code_barres}" existe déjà')
            
            # AJOUTER LE PRODUIT DANS LA BASE
            if os.environ.get('DATABASE_URL'):
                cursor.execute(
                    'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (%s, %s, %s, %s, %s)',
                    (nom, code_barres, prix, stock, categorie)
                )
            else:
                cursor.execute(
                    'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (%s, %s, %s, %s, %s)',
                    (nom, code_barres, prix, stock, categorie)
                )
            
            conn.commit()
            conn.close()
            
            print(f"✅ PRODUIT SAUVEGARDÉ: {nom} ({categorie})")
            
            # Redirection vers la page principale
            return redirect(url_for('index'))
            
        except Exception as e:
            print(f"❌ Erreur ajout produit: {e}")
            return render_template('ajouter_mobile.html', 
                                 categories=CATEGORIES,
                                 error=f'❌ Erreur: {str(e)}')
    
    return render_template('ajouter_mobile.html', categories=CATEGORIES)

@app.route('/scanner')
def scanner():
    """Page de scan simple"""
    return render_template('scanner_mobile.html')

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Scanner automatique avec décrément stock"""
    try:
        data = request.get_json()
        code_barres = data.get('code_barres', '').strip()
        
        if not code_barres:
            return jsonify({'success': False, 'message': 'Code-barres vide'})
        
        conn = get_database_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erreur connexion base'})
            
        if os.environ.get('DATABASE_URL'):
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
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
            'Écran': '📱', 'Batterie': '🔋', 'Coque': '🛡️', 'Housse': '👜',
            'Verre Trempé': '🔍', 'Câble': '🔌', 'Outil': '🔧', 'Accessoire': '📎', 'Autre': '📦'
        }
        
        emoji = categorie_emoji.get(produit['categorie'], '📦')
        
        if nouveau_stock == 0:
            message = f'🚨 {emoji} {produit["nom"]}: RUPTURE DE STOCK !'
            statut = 'rupture'
        elif nouveau_stock <= 2:
            message = f'⚠️ {emoji} {produit["nom"]}: Stock CRITIQUE ({nouveau_stock})'
            statut = 'critique'
        elif nouveau_stock <= 5:
            message = f'📦 {emoji} {produit["nom"]}: Stock faible ({nouveau_stock})'
            statut = 'faible'
        else:
            message = f'✅ {emoji} {produit["nom"]}: Stock mis à jour ({nouveau_stock})'
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
        
    except Exception as e:
        print(f"❌ ERREUR SCAN: {e}")
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    """Modifier un produit"""
    try:
        conn = get_database_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        if os.environ.get('DATABASE_URL'):
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
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
        
    except Exception as e:
        return f"Erreur: {e}", 500

@app.route('/supprimer/<int:id>')
def supprimer(id):
    """Supprimer un produit"""
    try:
        conn = get_database_connection()
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
        conn = get_database_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        if os.environ.get('DATABASE_URL'):
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor(dictionary=True)
            
        cursor.execute('SELECT * FROM produits ORDER BY categorie, nom')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('codes_barres_mobile.html', produits=produits)
        
    except Exception as e:
        return f"Erreur: {e}", 500

@app.route('/statistiques')
def statistiques():
    """Statistiques détaillées"""
    try:
        conn = get_database_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        if os.environ.get('DATABASE_URL'):
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor(dictionary=True)
        
        # Stats générales
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total_produits = cursor.fetchone()['total']
        
        cursor.execute('SELECT COALESCE(SUM(stock), 0) as total FROM produits')
        stock_total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM produits WHERE stock <= 5 AND stock > 0')
        stock_faible = cursor.fetchone()['total']
        
        cursor.execute('SELECT COALESCE(AVG(prix), 0) as moyenne FROM produits')
        prix_moyen = float(cursor.fetchone()['moyenne'])
        
        # Stats par catégorie
        cursor.execute("""
            SELECT categorie,
                   COUNT(*) as total_produits,
                   COALESCE(SUM(stock), 0) as stock_total,
                   COUNT(CASE WHEN stock = 0 THEN 1 END) as ruptures,
                   COUNT(CASE WHEN stock <= 5 AND stock > 0 THEN 1 END) as stock_faible,
                   COALESCE(AVG(prix), 0) as prix_moyen,
                   COALESCE(MIN(prix), 0) as prix_min,
                   COALESCE(MAX(prix), 0) as prix_max
            FROM produits 
            GROUP BY categorie 
            ORDER BY total_produits DESC
        """)
        stats_categories = cursor.fetchall()
        
        # Produits nécessitant attention
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
        
    except Exception as e:
        return f"Erreur: {e}", 500

@app.route('/export')
def export_csv():
    """Export CSV des produits"""
    try:
        conn = get_database_connection()
        if not conn:
            return "Erreur de connexion", 500
            
        if os.environ.get('DATABASE_URL'):
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor(dictionary=True)
            
        cursor.execute('SELECT * FROM produits ORDER BY categorie, nom')
        produits = cursor.fetchall()
        conn.close()
        
        # Créer le CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # En-têtes
        writer.writerow(['ID', 'Nom', 'Code-barres', 'Prix', 'Stock', 'Catégorie', 'Date Création'])
        
        # Données
        for produit in produits:
            writer.writerow([
                produit['id'],
                produit['nom'],
                produit['code_barres'],
                produit['prix'],
                produit['stock'],
                produit['categorie'],
                produit['date_creation'].strftime('%d/%m/%Y %H:%M') if produit['date_creation'] else ''
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=inventaire_mobile_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'}
        )
        
    except Exception as e:
        return f"Erreur: {e}", 500

if __name__ == '__main__':
    print("📱 BOUTIQUE RÉPARATION MOBILE")
    print("=" * 40)
    
    env = "Production (Render)" if os.environ.get('DATABASE_URL') else "Développement"
    print(f"🌍 Environnement: {env}")
    
    if init_database():
        print("✅ Base de données initialisée")
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("❌ Erreur d'initialisation")
