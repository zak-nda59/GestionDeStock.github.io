#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour migrer la base SQLite vers MySQL
Nécessite: pip install mysql-connector-python
"""

import sqlite3
import mysql.connector
from mysql.connector import Error
import os

def migrer_sqlite_vers_mysql():
    """Migre les données de SQLite vers MySQL"""
    
    # Configuration MySQL (à adapter selon votre configuration)
    mysql_config = {
        'host': 'localhost',
        'user': 'root',  # Votre utilisateur MySQL
        'password': '',  # Votre mot de passe MySQL
        'database': 'gestion_inventaire'  # Nom de la base MySQL
    }
    
    sqlite_db = 'database.db'
    
    if not os.path.exists(sqlite_db):
        print("❌ Fichier SQLite non trouvé!")
        return
    
    try:
        # Connexion SQLite
        sqlite_conn = sqlite3.connect(sqlite_db)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connexion MySQL
        mysql_conn = mysql.connector.connect(**mysql_config)
        mysql_cursor = mysql_conn.cursor()
        
        print("✅ Connexions établies")
        
        # Créer la table MySQL
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS produits (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nom VARCHAR(255) NOT NULL,
            code_barres VARCHAR(50) UNIQUE NOT NULL,
            prix DECIMAL(10,2) NOT NULL,
            stock INT NOT NULL DEFAULT 0,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        
        mysql_cursor.execute(create_table_sql)
        print("✅ Table MySQL créée")
        
        # Récupérer les données SQLite
        sqlite_cursor.execute("SELECT nom, code_barres, prix, stock FROM produits")
        produits = sqlite_cursor.fetchall()
        
        # Insérer dans MySQL
        insert_sql = """
        INSERT INTO produits (nom, code_barres, prix, stock) 
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        nom=VALUES(nom), prix=VALUES(prix), stock=VALUES(stock)
        """
        
        for produit in produits:
            mysql_cursor.execute(insert_sql, produit)
        
        mysql_conn.commit()
        print(f"✅ {len(produits)} produits migrés vers MySQL")
        
        # Fermer les connexions
        sqlite_conn.close()
        mysql_conn.close()
        
        print("🎉 Migration terminée avec succès!")
        print(f"Vous pouvez maintenant accéder à vos données via phpMyAdmin")
        print(f"Base de données: {mysql_config['database']}")
        print(f"Table: produits")
        
    except Error as e:
        print(f"❌ Erreur MySQL: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def generer_script_sql():
    """Génère un script SQL pour importer dans phpMyAdmin"""
    
    sqlite_db = 'database.db'
    
    if not os.path.exists(sqlite_db):
        print("❌ Fichier SQLite non trouvé!")
        return
    
    try:
        conn = sqlite3.connect(sqlite_db)
        cursor = conn.cursor()
        
        # Récupérer les données
        cursor.execute("SELECT nom, code_barres, prix, stock FROM produits")
        produits = cursor.fetchall()
        
        # Générer le script SQL
        sql_script = """-- Script SQL pour phpMyAdmin
-- Base de données: gestion_inventaire

CREATE DATABASE IF NOT EXISTS gestion_inventaire;
USE gestion_inventaire;

-- Structure de la table produits
CREATE TABLE IF NOT EXISTS produits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    code_barres VARCHAR(50) UNIQUE NOT NULL,
    prix DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Données des produits
"""
        
        for produit in produits:
            nom, code_barres, prix, stock = produit
            # Échapper les apostrophes
            nom = nom.replace("'", "\\'")
            sql_script += f"INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('{nom}', '{code_barres}', {prix}, {stock});\n"
        
        # Sauvegarder le script
        with open('import_mysql.sql', 'w', encoding='utf-8') as f:
            f.write(sql_script)
        
        conn.close()
        
        print("✅ Script SQL généré: import_mysql.sql")
        print("📋 Instructions:")
        print("1. Ouvrez phpMyAdmin")
        print("2. Créez une nouvelle base 'gestion_inventaire'")
        print("3. Importez le fichier 'import_mysql.sql'")
        print("4. Vos données seront disponibles dans phpMyAdmin")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🔄 Migration SQLite vers MySQL")
    print("=" * 40)
    
    choix = input("Choisissez une option:\n1. Migration directe (nécessite MySQL installé)\n2. Générer script SQL pour phpMyAdmin\nVotre choix (1 ou 2): ")
    
    if choix == "1":
        print("\n⚠️  Assurez-vous d'avoir installé: pip install mysql-connector-python")
        print("⚠️  Et configuré MySQL avec les bons paramètres dans le script")
        migrer_sqlite_vers_mysql()
    elif choix == "2":
        generer_script_sql()
    else:
        print("❌ Choix invalide")
