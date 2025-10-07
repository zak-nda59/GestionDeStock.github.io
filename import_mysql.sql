-- Script SQL pour phpMyAdmin
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
INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('ecran iphone 11', '123456789', 35.0, 25);
