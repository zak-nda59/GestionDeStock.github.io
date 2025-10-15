-- Sauvegarde automatique de la base de données
-- Date: 2025-10-07 15:52:52

DELETE FROM produits;
ALTER TABLE produits AUTO_INCREMENT = 1;

INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('produit 1', '789525', 30.00, 2);
