#!/usr/bin/env python3
"""
Test local de l'application ultra-simple
"""

import subprocess
import sys
import time
import requests

def test_app():
    print("🧪 Test de l'application ultra-simple...")
    
    # Lancer l'application
    print("🚀 Démarrage de l'application...")
    process = subprocess.Popen([sys.executable, "app_simple.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    # Attendre le démarrage
    time.sleep(3)
    
    try:
        # Tester les routes
        routes = [
            ('/', 'Page d\'accueil'),
            ('/test', 'Page de test'),
            ('/health', 'Health check'),
            ('/scanner', 'Scanner'),
            ('/api/produits', 'API produits')
        ]
        
        for route, description in routes:
            try:
                response = requests.get(f'http://localhost:5000{route}', timeout=5)
                status = "✅" if response.status_code == 200 else "❌"
                print(f"{status} {description}: {response.status_code}")
            except Exception as e:
                print(f"❌ {description}: Erreur - {str(e)}")
        
        # Test API scan
        try:
            response = requests.post('http://localhost:5000/api/scan', 
                                   json={'code': '1234567890123'}, 
                                   timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} API Scan: {response.status_code}")
        except Exception as e:
            print(f"❌ API Scan: Erreur - {str(e)}")
            
    finally:
        # Arrêter l'application
        process.terminate()
        print("🛑 Application arrêtée")

if __name__ == '__main__':
    test_app()
