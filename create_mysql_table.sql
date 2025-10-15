-- Script de création de la table MySQL pour WAMP
-- À exécuter dans phpMyAdmin

USE gestion_inventaire;

CREATE TABLE IF NOT EXISTS produits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    code_barres VARCHAR(100) NOT NULL UNIQUE,
    prix DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insertion des produits d'exemple
INSERT INTO produits (nom, code_barres, prix, stock) VALUES
('Coca-Cola', '123456789', 1.50, 10),
('Pain', '987654321', 2.00, 0),
('Lait', '555666777', 1.20, 2),
('Pommes', '111222333', 3.50, 15),
('Yaourt', '444555666', 2.80, 1),
('Biscuits', '777888999', 3.20, 0),
('Eau', '333444555', 0.80, 4),
('Fromage', '111333555', 4.20, 8),
('Pâtes', '222444666', 1.80, 12),
('Riz', '333555777', 2.50, 6);

-- Vérification
SELECT * FROM produits ORDER BY nom;
