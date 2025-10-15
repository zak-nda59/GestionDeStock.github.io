#!/usr/bin/env python3
"""
Application Flask - Boutique Mobile SIMPLIFIÉE
Toutes les fonctionnalités, interface ultra-simple
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import mysql.connector
from mysql.connector import Error
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mobile_shop_simple_2024'

# Configuration MySQL
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'gestion_inventaire',
    'charset': 'utf8mb4',
    'autocommit': True
}

def get_mysql_connection():
    """Connexion MySQL simplifiée"""
    try:
        config_no_db = MYSQL_CONFIG.copy()
        del config_no_db['database']
        
        conn = mysql.connector.connect(**config_no_db)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS gestion_inventaire")
        cursor.execute("USE gestion_inventaire")
        conn.close()
        
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn if conn.is_connected() else None
    except Error as e:
        print(f"❌ Erreur MySQL: {e}")
        return None

def init_simple_database():
    """Initialise la base avec structure simplifiée"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return False
            
        cursor = conn.cursor()
        
        # Table catégories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100) NOT NULL UNIQUE,
                emoji VARCHAR(10) DEFAULT '📦',
                description TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table produits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                code_barres VARCHAR(100) NOT NULL UNIQUE,
                prix DECIMAL(10,2) NOT NULL,
                stock INT NOT NULL DEFAULT 0,
                categorie VARCHAR(100) DEFAULT 'Général',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        
        # Catégories de base simplifiées
        cursor.execute('SELECT COUNT(*) FROM categories')
        if cursor.fetchone()[0] == 0:
            categories_base = [
                ('Général', '📦', 'Produits généraux'),
                ('Écran', '📱', 'Écrans et affichages'),
                ('Batterie', '🔋', 'Batteries et alimentation'),
                ('Protection', '🛡️', 'Coques et protections'),
                ('Accessoire', '📎', 'Accessoires divers'),
                ('Réparation', '🔧', 'Outils et pièces')
            ]
            
            for nom, emoji, description in categories_base:
                cursor.execute(
                    'INSERT INTO categories (nom, emoji, description) VALUES (%s, %s, %s)',
                    (nom, emoji, description)
                )
        
        cursor.execute('SELECT COUNT(*) FROM produits')
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✅ Base initialisée - {count} produits")
        return True
        
    except Error as e:
        print(f"❌ Erreur: {e}")
        return False

def get_categories():
    """Récupère toutes les catégories"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM categories ORDER BY nom')
        categories = cursor.fetchall()
        conn.close()
        return categories
    except:
        return []

# ROUTES PRINCIPALES
@app.route('/')
def index():
    """Page d'accueil simplifiée"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return render_template('simple_error.html', error="Connexion base de données")
            
        cursor = conn.cursor(dictionary=True)
        
        # Paramètres simples
        recherche = request.args.get('q', '')
        categorie = request.args.get('cat', '')
        
        # Requête simplifiée
        sql = "SELECT * FROM produits WHERE 1=1"
        params = []
        
        if recherche:
            sql += " AND (nom LIKE %s OR code_barres LIKE %s)"
            params.extend([f'%{recherche}%', f'%{recherche}%'])
        
        if categorie:
            sql += " AND categorie = %s"
            params.append(categorie)
        
        sql += " ORDER BY nom"
        
        cursor.execute(sql, params)
        produits = cursor.fetchall()
        
        # Stats rapides
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as ruptures FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()['ruptures']
        
        conn.close()
        
        return render_template('simple_index_ultra.html', 
                             produits=produits,
                             categories=get_categories(),
                             recherche=recherche,
                             categorie_filtre=categorie,
                             total=total,
                             ruptures=ruptures)
        
    except Exception as e:
        return render_template('simple_error.html', error=str(e))

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    """Ajouter un produit - Interface simplifiée"""
    if request.method == 'POST':
        try:
            nom = request.form.get('nom', '').strip()
            code_barres = request.form.get('code_barres', '').strip()
            prix = float(request.form.get('prix', 0))
            stock = int(request.form.get('stock', 0))
            categorie = request.form.get('categorie', 'Général')
            
            if not nom or not code_barres:
                return render_template('simple_ajouter.html', 
                                     categories=get_categories(),
                                     error='Nom et code-barres obligatoires')
            
            conn = get_mysql_connection()
            if not conn:
                return render_template('simple_ajouter.html', 
                                     categories=get_categories(),
                                     error='Erreur connexion')
            
            cursor = conn.cursor()
            
            # Vérifier unicité
            cursor.execute('SELECT COUNT(*) FROM produits WHERE code_barres = %s', (code_barres,))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return render_template('simple_ajouter.html', 
                                     categories=get_categories(),
                                     error=f'Code-barres "{code_barres}" déjà utilisé')
            
            # Ajouter
            cursor.execute(
                'INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES (%s, %s, %s, %s, %s)',
                (nom, code_barres, prix, stock, categorie)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
            
        except Exception as e:
            return render_template('simple_ajouter_modern.html', 
                                 categories=get_categories(),
                                 error=f'Erreur: {str(e)}')
    
    return render_template('simple_ajouter_modern.html', categories=get_categories())

@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
def modifier(id):
    """Modifier un produit - Interface simplifiée"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return redirect(url_for('index'))
            
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            nom = request.form.get('nom', '').strip()
            prix = float(request.form.get('prix', 0))
            stock = int(request.form.get('stock', 0))
            categorie = request.form.get('categorie', 'Général')
            
            cursor.execute(
                'UPDATE produits SET nom = %s, prix = %s, stock = %s, categorie = %s WHERE id = %s',
                (nom, prix, stock, categorie, id)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        
        cursor.execute('SELECT * FROM produits WHERE id = %s', (id,))
        produit = cursor.fetchone()
        conn.close()
        
        if not produit:
            return redirect(url_for('index'))
            
        return render_template('simple_modifier.html', 
                             produit=produit, 
                             categories=get_categories())
        
    except Exception as e:
        return redirect(url_for('index'))

@app.route('/supprimer/<int:id>')
def supprimer(id):
    """Supprimer un produit"""
    try:
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM produits WHERE id = %s', (id,))
            conn.commit()
            conn.close()
    except:
        pass
    return redirect(url_for('index'))

@app.route('/scanner')
def scanner():
    """Scanner simplifié"""
    return render_template('simple_scanner_modern.html')

@app.route('/scan', methods=['POST'])
def scan():
    """API scan simplifiée"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({'success': False, 'message': 'Code vide'})
        
        conn = get_mysql_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erreur connexion'})
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produits WHERE code_barres = %s', (code,))
        produit = cursor.fetchone()
        
        if not produit:
            conn.close()
            return jsonify({'success': False, 'message': f'Produit non trouvé: {code}'})
        
        if produit['stock'] <= 0:
            conn.close()
            return jsonify({'success': False, 'message': f'{produit["nom"]} en rupture'})
        
        # Décrémenter
        nouveau_stock = produit['stock'] - 1
        cursor.execute('UPDATE produits SET stock = %s WHERE id = %s', (nouveau_stock, produit['id']))
        conn.commit()
        conn.close()
        
        if nouveau_stock == 0:
            message = f'🚨 {produit["nom"]}: RUPTURE!'
        elif nouveau_stock <= 2:
            message = f'⚠️ {produit["nom"]}: Stock critique ({nouveau_stock})'
        else:
            message = f'✅ {produit["nom"]}: Stock {nouveau_stock}'
        
        return jsonify({
            'success': True,
            'message': message,
            'produit': produit['nom'],
            'nouveau_stock': nouveau_stock
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

@app.route('/categories')
def categories():
    """Gestion catégories simplifiée"""
    return render_template('simple_categories_modern.html', categories=get_categories())

@app.route('/categories/ajouter', methods=['POST'])
def ajouter_categorie():
    """Ajouter catégorie"""
    try:
        nom = request.form.get('nom', '').strip()
        emoji = request.form.get('emoji', '📦').strip()
        
        if not nom:
            return jsonify({'success': False, 'message': 'Nom obligatoire'})
        
        conn = get_mysql_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Erreur connexion'})
        
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categories (nom, emoji) VALUES (%s, %s)', (nom, emoji))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Catégorie "{nom}" ajoutée'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/categories/supprimer/<int:id>')
def supprimer_categorie(id):
    """Supprimer catégorie"""
    try:
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT nom FROM categories WHERE id = %s', (id,))
            cat = cursor.fetchone()
            if cat:
                # Déplacer produits vers Général
                cursor.execute('UPDATE produits SET categorie = %s WHERE categorie = %s', ('Général', cat['nom']))
                cursor.execute('DELETE FROM categories WHERE id = %s', (id,))
                conn.commit()
            conn.close()
    except:
        pass
    return redirect(url_for('categories'))

@app.route('/export')
def export():
    """Export CSV simplifié"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return "Erreur", 500
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produits ORDER BY categorie, nom')
        produits = cursor.fetchall()
        conn.close()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Nom', 'Code', 'Prix', 'Stock', 'Catégorie'])
        
        for p in produits:
            writer.writerow([p['nom'], p['code_barres'], p['prix'], p['stock'], p['categorie']])
        
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=inventaire_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
        
    except Exception as e:
        return f"Erreur: {e}", 500

@app.route('/codes-barres')
def codes_barres():
    """Page de génération de codes-barres"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return render_template('simple_error.html', error="Connexion base de données")
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produits ORDER BY categorie, nom')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('simple_codes_barres.html', produits=produits, categories=get_categories())
        
    except Exception as e:
        return render_template('simple_error.html', error=str(e))

@app.route('/statistiques')
def statistiques():
    """Statistiques simplifiées"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return render_template('simple_error.html', error="Connexion base de données")
            
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
                   AVG(prix) as prix_moyen
            FROM produits 
            GROUP BY categorie 
            ORDER BY total_produits DESC
        """)
        stats_categories = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_produits': total_produits,
            'stock_total': stock_total,
            'ruptures': ruptures,
            'stock_faible': stock_faible,
            'prix_moyen': round(prix_moyen, 2),
            'stats_categories': stats_categories
        }
        
        return render_template('simple_statistiques.html', stats=stats, categories=get_categories())
        
    except Exception as e:
        return render_template('simple_error.html', error=str(e))

@app.route('/produits')
def voir_produits():
    """Page dédiée pour voir tous les produits avec filtres avancés"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return render_template('simple_error.html', error="Connexion base de données")
            
        cursor = conn.cursor(dictionary=True)
        
        # Paramètres de filtrage
        recherche = request.args.get('q', '')
        categorie = request.args.get('cat', '')
        stock_filter = request.args.get('stock', '')  # 'ok', 'low', 'out'
        prix_min = request.args.get('prix_min', '')
        prix_max = request.args.get('prix_max', '')
        tri = request.args.get('sort', 'nom')  # nom, prix, stock, date
        ordre = request.args.get('order', 'asc')  # asc, desc
        
        # Construction de la requête
        sql = "SELECT * FROM produits WHERE 1=1"
        params = []
        
        if recherche:
            sql += " AND (nom LIKE %s OR code_barres LIKE %s)"
            params.extend([f'%{recherche}%', f'%{recherche}%'])
        
        if categorie:
            sql += " AND categorie = %s"
            params.append(categorie)
            
        if stock_filter == 'out':
            sql += " AND stock = 0"
        elif stock_filter == 'low':
            sql += " AND stock > 0 AND stock <= 5"
        elif stock_filter == 'ok':
            sql += " AND stock > 5"
            
        if prix_min:
            sql += " AND prix >= %s"
            params.append(float(prix_min))
            
        if prix_max:
            sql += " AND prix <= %s"
            params.append(float(prix_max))
        
        # Tri
        colonnes_tri = {
            'nom': 'nom',
            'prix': 'prix',
            'stock': 'stock',
            'date': 'date_creation',
            'categorie': 'categorie'
        }
        
        if tri in colonnes_tri:
            sql += f" ORDER BY {colonnes_tri[tri]} {ordre.upper()}"
        else:
            sql += " ORDER BY nom ASC"
        
        cursor.execute(sql, params)
        produits = cursor.fetchall()
        
        # Stats pour les filtres
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as ruptures FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()['ruptures']
        
        cursor.execute('SELECT COUNT(*) as stock_faible FROM produits WHERE stock > 0 AND stock <= 5')
        stock_faible = cursor.fetchone()['stock_faible']
        
        cursor.execute('SELECT MIN(prix) as prix_min, MAX(prix) as prix_max FROM produits')
        prix_range = cursor.fetchone()
        
        conn.close()
        
        stats = {
            'total': total,
            'ruptures': ruptures,
            'stock_faible': stock_faible,
            'prix_min': prix_range['prix_min'] or 0,
            'prix_max': prix_range['prix_max'] or 0,
            'resultats': len(produits)
        }
        
        return render_template('voir_produits_simple.html', 
                             produits=produits,
                             categories=get_categories(),
                             stats=stats,
                             filtres={
                                 'recherche': recherche,
                                 'categorie': categorie,
                                 'stock_filter': stock_filter,
                                 'prix_min': prix_min,
                                 'prix_max': prix_max,
                                 'tri': tri,
                                 'ordre': ordre
                             })
        
    except Exception as e:
        return render_template('simple_error.html', error=str(e))

@app.route('/api/suggestions/<categorie>')
def suggestions(categorie):
    """Suggestions simplifiées"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return jsonify([])
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT nom FROM produits WHERE categorie = %s ORDER BY date_creation DESC LIMIT 5', (categorie,))
        produits = cursor.fetchall()
        conn.close()
        
        suggestions = []
        for p in produits:
            nom = p['nom']
            mots = nom.split()
            if len(mots) >= 2:
                base = ' '.join(mots[:-1])
                suggestions.extend([f"{base} Pro", f"{base} Plus"])
        
        return jsonify(list(set(suggestions))[:6])
        
    except:
        return jsonify([])

@app.route('/ruptures')
def ruptures():
    """Page des produits en rupture de stock"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return render_template('simple_error.html', error="Connexion base de données")
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produits WHERE stock = 0 ORDER BY categorie, nom')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('ruptures_modern.html', produits=produits, categories=get_categories())
        
    except Exception as e:
        return render_template('simple_error.html', error=str(e))

@app.route('/stock-faible')
def stock_faible():
    """Page des produits à stock faible"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return render_template('simple_error.html', error="Connexion base de données")
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM produits WHERE stock > 0 AND stock <= 5 ORDER BY stock ASC, categorie, nom')
        produits = cursor.fetchall()
        conn.close()
        
        return render_template('stock_faible_modern.html', produits=produits, categories=get_categories())
        
    except Exception as e:
        return render_template('simple_error.html', error=str(e))

@app.route('/recherche')
def recherche_avancee():
    """Page de recherche avancée"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return render_template('simple_error.html', error="Connexion base de données")
            
        cursor = conn.cursor(dictionary=True)
        
        # Stats pour la recherche
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT categorie, COUNT(*) as count FROM produits GROUP BY categorie ORDER BY count DESC')
        categories_stats = cursor.fetchall()
        
        conn.close()
        
        return render_template('recherche_modern.html', 
                             categories=get_categories(),
                             categories_stats=categories_stats,
                             total=total)
        
    except Exception as e:
        return render_template('simple_error.html', error=str(e))

@app.route('/api/recherche')
def api_recherche():
    """API de recherche en temps réel"""
    try:
        query = request.args.get('q', '').strip()
        if len(query) < 2:
            return jsonify([])
            
        conn = get_mysql_connection()
        if not conn:
            return jsonify([])
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT nom, code_barres, prix, stock, categorie FROM produits WHERE nom LIKE %s OR code_barres LIKE %s LIMIT 10',
            (f'%{query}%', f'%{query}%')
        )
        produits = cursor.fetchall()
        conn.close()
        
        return jsonify(produits)
        
    except:
        return jsonify([])

@app.route('/dashboard')
def dashboard():
    """Tableau de bord complet"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return render_template('simple_error.html', error="Connexion base de données")
            
        cursor = conn.cursor(dictionary=True)
        
        # Stats complètes
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total_produits = cursor.fetchone()['total']
        
        cursor.execute('SELECT SUM(stock) as total FROM produits')
        result = cursor.fetchone()
        stock_total = result['total'] if result['total'] else 0
        
        cursor.execute('SELECT COUNT(*) as total FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM produits WHERE stock <= 5 AND stock > 0')
        stock_faible = cursor.fetchone()['total']
        
        cursor.execute('SELECT SUM(prix * stock) as valeur FROM produits')
        result = cursor.fetchone()
        valeur_stock = float(result['valeur']) if result['valeur'] else 0
        
        # Produits récents
        cursor.execute('SELECT * FROM produits ORDER BY date_creation DESC LIMIT 5')
        produits_recents = cursor.fetchall()
        
        # Top catégories
        cursor.execute("""
            SELECT categorie, COUNT(*) as count, SUM(stock) as stock_total
            FROM produits 
            GROUP BY categorie 
            ORDER BY count DESC 
            LIMIT 5
        """)
        top_categories = cursor.fetchall()
        
        conn.close()
        
        dashboard_data = {
            'total_produits': total_produits,
            'stock_total': stock_total,
            'ruptures': ruptures,
            'stock_faible': stock_faible,
            'valeur_stock': round(valeur_stock, 2),
            'produits_recents': produits_recents,
            'top_categories': top_categories
        }
        
        return render_template('dashboard_modern.html', 
                             data=dashboard_data, 
                             categories=get_categories())
        
    except Exception as e:
        return render_template('simple_error.html', error=str(e))

@app.route('/aide')
def aide():
    """Page d'aide et documentation"""
    return render_template('aide_modern.html')

@app.route('/api/stats')
def api_stats():
    """API pour les statistiques en temps réel"""
    try:
        conn = get_mysql_connection()
        if not conn:
            return jsonify({'error': 'Connexion impossible'})
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT COUNT(*) as total FROM produits')
        total = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as ruptures FROM produits WHERE stock = 0')
        ruptures = cursor.fetchone()['ruptures']
        
        cursor.execute('SELECT COUNT(*) as stock_faible FROM produits WHERE stock <= 5 AND stock > 0')
        stock_faible = cursor.fetchone()['stock_faible']
        
        conn.close()
        
        return jsonify({
            'total': total,
            'ruptures': ruptures,
            'stock_faible': stock_faible,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("📱 BOUTIQUE MOBILE - VERSION MODERNE COMPLÈTE")
    print("=" * 60)
    print("🚀 Interface ultra-moderne avec toutes les fonctionnalités")
    print("🔧 Filtres avancés, recherche intelligente, dashboard complet")
    print()
    print("📋 ROUTES DISPONIBLES:")
    print("   🏠 / → Accueil avec aperçu")
    print("   📦 /produits → Voir tous les produits avec filtres")
    print("   ➕ /ajouter → Ajouter un produit")
    print("   ✏️ /modifier/<id> → Modifier un produit")
    print("   🗑️ /supprimer/<id> → Supprimer un produit")
    print("   📱 /scanner → Scanner codes-barres")
    print("   📊 /statistiques → Statistiques complètes")
    print("   🏷️ /codes-barres → Générer codes-barres")
    print("   📂 /categories → Gérer catégories")
    print("   🚨 /ruptures → Produits en rupture")
    print("   ⚠️ /stock-faible → Stock faible")
    print("   🔍 /recherche → Recherche avancée")
    print("   📈 /dashboard → Tableau de bord")
    print("   💾 /export → Export CSV")
    print("   ❓ /aide → Documentation")
    print()
    
    if init_simple_database():
        print("✅ Base de données initialisée")
        print("🌐 Application disponible sur: http://localhost:5000")
        print("🎯 Cliquez sur 'Voir tous' pour accéder aux filtres avancés")
        print()
        app.run(host='127.0.0.1', port=5000, debug=True)
    else:
        print("❌ Erreur initialisation base de données")
