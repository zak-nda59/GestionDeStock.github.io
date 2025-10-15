-- Sauvegarde automatique de la base de données
-- Date: 2025-10-07 15:51:56

DELETE FROM produits;
ALTER TABLE produits AUTO_INCREMENT = 1;

INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('Coca-Cola', '123456789', 1.50, 10);
INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('Pain', '987654321', 2.00, 0);
INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('Lait', '555666777', 1.20, 2);
INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('Pommes', '111222333', 3.50, 15);
INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('Yaourt', '444555666', 2.80, 1);
INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('Eau', '333444555', 0.80, 4);
INSERT INTO produits (nom, code_barres, prix, stock) VALUES ('produit 1', '789525', 10.00, 2);
