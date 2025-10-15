-- Mise à jour base de données pour boutique réparation mobile
-- Ajouter la colonne catégorie

ALTER TABLE produits ADD COLUMN categorie VARCHAR(50) DEFAULT 'Autre';

-- Mettre à jour les produits existants avec des catégories
UPDATE produits SET categorie = 'Écran' WHERE nom LIKE '%écran%' OR nom LIKE '%screen%' OR nom LIKE '%display%';
UPDATE produits SET categorie = 'Batterie' WHERE nom LIKE '%batterie%' OR nom LIKE '%battery%';
UPDATE produits SET categorie = 'Coque' WHERE nom LIKE '%coque%' OR nom LIKE '%case%' OR nom LIKE '%étui%';
UPDATE produits SET categorie = 'Câble' WHERE nom LIKE '%câble%' OR nom LIKE '%cable%' OR nom LIKE '%chargeur%';
UPDATE produits SET categorie = 'Verre Trempé' WHERE nom LIKE '%verre%' OR nom LIKE '%protection%' OR nom LIKE '%film%';

-- Supprimer les anciens produits et ajouter des produits spécialisés mobile
DELETE FROM produits;

-- Produits spécialisés réparation mobile
INSERT INTO produits (nom, code_barres, prix, stock, categorie) VALUES
-- ÉCRANS
('Écran iPhone 13 Pro Max OLED', 'ECR001', 89.99, 5, 'Écran'),
('Écran iPhone 12 LCD', 'ECR002', 65.50, 8, 'Écran'),
('Écran Samsung Galaxy S21', 'ECR003', 75.00, 3, 'Écran'),
('Écran iPhone 11 LCD', 'ECR004', 55.99, 12, 'Écran'),
('Écran Xiaomi Redmi Note 10', 'ECR005', 35.00, 6, 'Écran'),
('Écran Huawei P30 Pro', 'ECR006', 68.50, 2, 'Écran'),
('Écran OnePlus 9 Pro', 'ECR007', 82.00, 4, 'Écran'),

-- BATTERIES
('Batterie iPhone 13 Pro', 'BAT001', 25.99, 15, 'Batterie'),
('Batterie iPhone 12 Mini', 'BAT002', 22.50, 10, 'Batterie'),
('Batterie Samsung Galaxy S20', 'BAT003', 28.00, 8, 'Batterie'),
('Batterie iPhone 11 Pro Max', 'BAT004', 24.99, 20, 'Batterie'),
('Batterie Xiaomi Mi 11', 'BAT005', 18.50, 12, 'Batterie'),
('Batterie Huawei P40', 'BAT006', 26.00, 6, 'Batterie'),

-- COQUES
('Coque iPhone 13 Transparente', 'COQ001', 12.99, 25, 'Coque'),
('Coque Samsung S21 Antichoc', 'COQ002', 15.50, 18, 'Coque'),
('Coque iPhone 12 Pro Cuir', 'COQ003', 22.00, 8, 'Coque'),
('Coque Xiaomi Redmi Silicone', 'COQ004', 8.99, 30, 'Coque'),
('Coque iPhone 11 MagSafe', 'COQ005', 18.50, 12, 'Coque'),

-- HOUSSES
('Housse iPhone 13 Pro Max', 'HOU001', 16.99, 10, 'Housse'),
('Housse Samsung Galaxy Tab', 'HOU002', 24.50, 5, 'Housse'),
('Housse Universelle 6.1"', 'HOU003', 12.00, 15, 'Housse'),
('Housse iPhone 12 Portefeuille', 'HOU004', 19.99, 8, 'Housse'),

-- VERRE TREMPÉ
('Verre Trempé iPhone 13 Pro', 'VER001', 9.99, 50, 'Verre Trempé'),
('Verre Trempé Samsung S21', 'VER002', 8.50, 35, 'Verre Trempé'),
('Verre Trempé iPhone 12 Mini', 'VER003', 9.99, 40, 'Verre Trempé'),
('Verre Trempé Xiaomi Redmi', 'VER004', 6.99, 60, 'Verre Trempé'),
('Verre Trempé Huawei P30', 'VER005', 7.50, 25, 'Verre Trempé'),

-- CÂBLES
('Câble Lightning iPhone 1m', 'CAB001', 12.99, 30, 'Câble'),
('Câble USB-C Samsung 2m', 'CAB002', 14.50, 25, 'Câble'),
('Câble Micro-USB 1.5m', 'CAB003', 8.99, 20, 'Câble'),
('Chargeur Sans Fil iPhone', 'CAB004', 29.99, 8, 'Câble'),
('Adaptateur Lightning Jack', 'CAB005', 15.50, 12, 'Câble'),

-- OUTILS
('Kit Tournevis Réparation', 'OUT001', 19.99, 5, 'Outil'),
('Ventouse Démontage Écran', 'OUT002', 8.50, 10, 'Outil'),
('Spatule Plastique x5', 'OUT003', 5.99, 15, 'Outil'),
('Tapis Antistatique', 'OUT004', 12.00, 3, 'Outil'),

-- ACCESSOIRES
('Support Téléphone Bureau', 'ACC001', 16.99, 12, 'Accessoire'),
('Nettoyant Écran 250ml', 'ACC002', 6.50, 8, 'Accessoire'),
('Chiffon Microfibre x3', 'ACC003', 4.99, 20, 'Accessoire'),
('Adhésif Double Face Écran', 'ACC004', 3.50, 25, 'Accessoire');

-- Vérification
SELECT categorie, COUNT(*) as nombre FROM produits GROUP BY categorie ORDER BY nombre DESC;
