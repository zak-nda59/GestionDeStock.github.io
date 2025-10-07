#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface web d'administration pour la base SQLite
Similaire à phpMyAdmin mais pour SQLite
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Template HTML pour l'interface d'administration
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin SQLite - Gestion Inventaire</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand">
                <i class="bi bi-database"></i> Admin SQLite - Inventaire
            </span>
            <span class="text-light">
                <i class="bi bi-file-earmark-text"></i> database.db
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Statistiques -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <h5>{{ stats.total_produits }}</h5>
                        <p class="mb-0">Produits Total</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <h5>{{ stats.total_stock }}</h5>
                        <p class="mb-0">Stock Total</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <h5>{{ "%.2f"|format(stats.valeur_totale) }} €</h5>
                        <p class="mb-0">Valeur Totale</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white">
                    <div class="card-body">
                        <h5>{{ stats.taille_db }} KB</h5>
                        <p class="mb-0">Taille DB</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Actions -->
        <div class="row mb-3">
            <div class="col-12">
                <div class="btn-group" role="group">
                    <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#addModal">
                        <i class="bi bi-plus"></i> Ajouter
                    </button>
                    <button class="btn btn-info" onclick="exportSQL()">
                        <i class="bi bi-download"></i> Export SQL
                    </button>
                    <button class="btn btn-warning" onclick="location.reload()">
                        <i class="bi bi-arrow-clockwise"></i> Actualiser
                    </button>
                    <a href="/" class="btn btn-primary">
                        <i class="bi bi-house"></i> Retour App
                    </a>
                </div>
            </div>
        </div>

        <!-- Table des produits -->
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="bi bi-table"></i> Table: produits ({{ produits|length }} enregistrements)
                </h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Nom</th>
                                <th>Code-barres</th>
                                <th>Prix</th>
                                <th>Stock</th>
                                <th>Date Création</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for produit in produits %}
                            <tr>
                                <td><strong>{{ produit.id }}</strong></td>
                                <td>{{ produit.nom }}</td>
                                <td><code>{{ produit.code_barres }}</code></td>
                                <td>{{ "%.2f"|format(produit.prix) }} €</td>
                                <td>
                                    <span class="badge {% if produit.stock == 0 %}bg-danger{% elif produit.stock < 2 %}bg-warning{% else %}bg-success{% endif %}">
                                        {{ produit.stock }}
                                    </span>
                                </td>
                                <td>{{ produit.date_creation or 'N/A' }}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary" onclick="editProduct({{ produit.id }})">
                                        <i class="bi bi-pencil"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct({{ produit.id }})">
                                        <i class="bi bi-trash"></i>
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Requêtes SQL personnalisées -->
        <div class="card mt-4">
            <div class="card-header">
                <h5 class="mb-0"><i class="bi bi-terminal"></i> Exécuter une requête SQL</h5>
            </div>
            <div class="card-body">
                <form onsubmit="executeSQL(event)">
                    <div class="mb-3">
                        <textarea class="form-control" id="sqlQuery" rows="3" placeholder="SELECT * FROM produits WHERE stock < 5;"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-play"></i> Exécuter
                    </button>
                </form>
                <div id="sqlResult" class="mt-3"></div>
            </div>
        </div>
    </div>

    <!-- Modal d'ajout -->
    <div class="modal fade" id="addModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Ajouter un produit</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form onsubmit="addProduct(event)">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Nom</label>
                            <input type="text" class="form-control" name="nom" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Code-barres</label>
                            <input type="text" class="form-control" name="code_barres" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Prix</label>
                            <input type="number" step="0.01" class="form-control" name="prix" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Stock</label>
                            <input type="number" class="form-control" name="stock" required>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Annuler</button>
                        <button type="submit" class="btn btn-primary">Ajouter</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function executeSQL(event) {
            event.preventDefault();
            const query = document.getElementById('sqlQuery').value;
            
            fetch('/admin/sql', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query})
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('sqlResult');
                if (data.success) {
                    resultDiv.innerHTML = '<div class="alert alert-success">Requête exécutée avec succès!</div>';
                    if (data.results) {
                        resultDiv.innerHTML += '<pre>' + JSON.stringify(data.results, null, 2) + '</pre>';
                    }
                } else {
                    resultDiv.innerHTML = '<div class="alert alert-danger">Erreur: ' + data.error + '</div>';
                }
            });
        }

        function addProduct(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const data = Object.fromEntries(formData);
            
            fetch('/admin/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Erreur: ' + data.error);
                }
            });
        }

        function deleteProduct(id) {
            if (confirm('Supprimer ce produit ?')) {
                fetch('/admin/delete/' + id, {method: 'DELETE'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Erreur: ' + data.error);
                    }
                });
            }
        }

        function exportSQL() {
            window.open('/admin/export-sql', '_blank');
        }
    </script>
</body>
</html>
"""

def get_db_connection():
    """Connexion à la base de données"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/admin')
def admin_index():
    """Page d'administration principale"""
    conn = get_db_connection()
    
    # Récupérer les produits
    produits = conn.execute('SELECT * FROM produits ORDER BY nom').fetchall()
    
    # Statistiques
    stats_query = conn.execute('''
        SELECT 
            COUNT(*) as total_produits,
            SUM(stock) as total_stock,
            SUM(stock * prix) as valeur_totale
        FROM produits
    ''').fetchone()
    
    stats = {
        'total_produits': stats_query['total_produits'],
        'total_stock': stats_query['total_stock'] or 0,
        'valeur_totale': stats_query['valeur_totale'] or 0,
        'taille_db': round(os.path.getsize('database.db') / 1024, 1) if os.path.exists('database.db') else 0
    }
    
    conn.close()
    
    return render_template_string(ADMIN_TEMPLATE, produits=produits, stats=stats)

@app.route('/admin/sql', methods=['POST'])
def execute_sql():
    """Exécuter une requête SQL personnalisée"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'error': 'Requête vide'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Exécuter la requête
        cursor.execute(query)
        
        # Si c'est un SELECT, récupérer les résultats
        if query.upper().startswith('SELECT'):
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return jsonify({'success': True, 'results': results})
        else:
            # Pour INSERT, UPDATE, DELETE
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Requête exécutée'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/add', methods=['POST'])
def add_product():
    """Ajouter un produit"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (?, ?, ?, ?)',
            (data['nom'], data['code_barres'], float(data['prix']), int(data['stock']))
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/delete/<int:id>', methods=['DELETE'])
def delete_product(id):
    """Supprimer un produit"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM produits WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/export-sql')
def export_sql():
    """Exporter la base en SQL"""
    try:
        conn = get_db_connection()
        produits = conn.execute('SELECT * FROM produits').fetchall()
        
        sql_content = """-- Export SQLite vers MySQL
-- Base de données: gestion_inventaire

CREATE DATABASE IF NOT EXISTS gestion_inventaire;
USE gestion_inventaire;

CREATE TABLE IF NOT EXISTS produits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    code_barres VARCHAR(50) UNIQUE NOT NULL,
    prix DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

"""
        
        for produit in produits:
            nom = produit['nom'].replace("'", "\\'")
            sql_content += f"INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('{nom}', '{produit['code_barres']}', {produit['prix']}, {produit['stock']});\n"
        
        conn.close()
        
        from flask import Response
        return Response(
            sql_content,
            mimetype='text/plain',
            headers={'Content-Disposition': 'attachment; filename=export_mysql.sql'}
        )
        
    except Exception as e:
        return f"Erreur: {e}"

if __name__ == '__main__':
    print("🔧 Interface d'administration SQLite")
    print("📍 Accès: http://localhost:5001/admin")
    app.run(debug=True, port=5001)
