#!/usr/bin/env python3
"""
Script pour corriger la synchronisation base/application
"""

import mysql.connector

def fix_synchronization():
    """Corrige la synchronisation entre base et application"""
    try:
        print("🔧 CORRECTION SYNCHRONISATION BASE/APPLICATION")
        print("=" * 50)
        
        # Connexion à la base
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='gestion_inventaire'
        )
        cursor = conn.cursor()
        
        # 1. Vérifier l'état actuel
        cursor.execute('SELECT COUNT(*) FROM produits')
        count = cursor.fetchone()[0]
        print(f"📊 Produits dans la base: {count}")
        
        # 2. Lister tous les produits
        cursor.execute('SELECT id, nom, code_barres, prix, stock FROM produits ORDER BY id')
        produits = cursor.fetchall()
        
        print("\n📋 PRODUITS ACTUELS:")
        for p in produits:
            print(f"  ID: {p[0]} | {p[1]} | Code: {p[2]} | Prix: {p[3]}€ | Stock: {p[4]}")
        
        # 3. Vérifier s'il y a des doublons ou des problèmes
        cursor.execute('SELECT nom, COUNT(*) FROM produits GROUP BY nom HAVING COUNT(*) > 1')
        doublons = cursor.fetchall()
        
        if doublons:
            print(f"\n⚠️ DOUBLONS DÉTECTÉS: {len(doublons)}")
            for d in doublons:
                print(f"  - {d[0]}: {d[1]} occurrences")
        else:
            print("\n✅ Aucun doublon détecté")
        
        # 4. Vérifier les IDs
        cursor.execute('SELECT MIN(id), MAX(id) FROM produits')
        min_id, max_id = cursor.fetchone()
        print(f"\n🔢 IDs: Min={min_id}, Max={max_id}")
        
        # 5. Proposer une correction si nécessaire
        if count != 7:
            print(f"\n🚨 PROBLÈME: Attendu 7 produits, trouvé {count}")
            print("💡 Solution: Réinitialiser avec les bons produits")
            
            response = input("Voulez-vous réinitialiser les produits ? (o/n): ")
            if response.lower() == 'o':
                # Supprimer tous les produits
                cursor.execute('DELETE FROM produits')
                cursor.execute('ALTER TABLE produits AUTO_INCREMENT = 1')
                
                # Réinsérer les bons produits
                produits_corrects = [
                    ('Coca-Cola', '123456789', 1.50, 10),
                    ('Pain', '987654321', 2.00, 0),
                    ('Lait', '555666777', 1.20, 2),
                    ('Pommes', '111222333', 3.50, 15),
                    ('Yaourt', '444555666', 2.80, 1),
                    ('Biscuits', '777888999', 3.20, 0),
                    ('Eau', '333444555', 0.80, 4)
                ]
                
                cursor.executemany(
                    'INSERT INTO produits (nom, code_barres, prix, stock) VALUES (%s, %s, %s, %s)',
                    produits_corrects
                )
                
                conn.commit()
                print("✅ Produits réinitialisés avec succès!")
        else:
            print("\n✅ Base de données correcte")
        
        conn.close()
        print("\n🎯 Redémarrez l'application pour voir les changements")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    fix_synchronization()
