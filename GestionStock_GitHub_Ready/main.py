#!/usr/bin/env python3
"""
🚀 BOUTIQUE MOBILE - VERSION SIMPLE POUR RENDER
Application Flask minimale pour débogage
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Page d'accueil simple"""
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📱 Boutique Mobile</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 40px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 500px;
                text-align: center;
                box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
                font-size: 2.5rem;
                margin-bottom: 20px;
            }
            .subtitle {
                color: #666;
                font-size: 1.2rem;
                margin-bottom: 30px;
            }
            .btn {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 30px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                margin: 10px;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
                color: white;
            }
            .status {
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                font-weight: 500;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 Boutique Mobile</h1>
            <p class="subtitle">Gestion d'inventaire simplifiée</p>
            <div class="status">
                ✅ Application déployée avec succès !
            </div>
            <a href="/scanner" class="btn">📱 Scanner</a>
            <a href="/test" class="btn">🔧 Test</a>
        </div>
    </body>
    </html>
    """

@app.route('/scanner')
def scanner():
    """Scanner simple"""
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📱 Scanner - Boutique Mobile</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 40px;
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
                margin: 0 auto;
                text-align: center;
                box-shadow: 0 15px 40px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
                font-size: 2rem;
                margin-bottom: 30px;
            }
            .input-group {
                margin: 30px 0;
            }
            input {
                padding: 15px 20px;
                font-size: 18px;
                width: 300px;
                max-width: 100%;
                border: 3px solid #e9ecef;
                border-radius: 12px;
                text-align: center;
                font-family: monospace;
            }
            input:focus {
                border-color: #667eea;
                outline: none;
                box-shadow: 0 0 0 0.3rem rgba(102, 126, 234, 0.25);
            }
            .btn {
                background: linear-gradient(45deg, #28a745, #20c997);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 30px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                margin: 10px;
                transition: all 0.3s ease;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(40, 167, 69, 0.4);
            }
            .btn-secondary {
                background: linear-gradient(45deg, #6c757d, #5a6268);
            }
            .result {
                margin: 20px 0;
                padding: 15px;
                border-radius: 8px;
                display: none;
                font-weight: 500;
            }
            .success {
                background: #d4edda;
                color: #155724;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 Scanner Simple</h1>
            <p>Tapez ou scannez un code-barres</p>
            
            <div class="input-group">
                <input type="text" id="codeInput" placeholder="Code-barres..." autofocus>
            </div>
            
            <button class="btn" onclick="scanCode()">🔍 Rechercher</button>
            <button class="btn btn-secondary" onclick="location.href='/'">🏠 Accueil</button>
            
            <div id="result" class="result"></div>
        </div>
        
        <script>
            function scanCode() {
                const code = document.getElementById('codeInput').value.trim();
                if (!code) {
                    showResult('Veuillez saisir un code-barres', 'error');
                    return;
                }
                
                showResult('🔍 Recherche en cours...', 'success');
                
                // Simulation de recherche
                setTimeout(() => {
                    showResult('✅ Code scanné: ' + code + ' (Mode démo)', 'success');
                }, 1000);
            }
            
            function showResult(message, type) {
                const result = document.getElementById('result');
                result.textContent = message;
                result.className = 'result ' + type;
                result.style.display = 'block';
            }
            
            document.getElementById('codeInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') scanCode();
            });
        </script>
    </body>
    </html>
    """

@app.route('/test')
def test():
    """Page de test"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔧 Test - Boutique Mobile</title>
        <meta charset="UTF-8">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: #f0f8ff; 
                text-align: center; 
            }
            .container { 
                max-width: 600px; 
                margin: 0 auto; 
                background: white; 
                padding: 30px; 
                border-radius: 15px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            }
            h1 { color: #28a745; }
            .status { 
                background: #d4edda; 
                color: #155724; 
                padding: 15px; 
                border-radius: 8px; 
                margin: 20px 0; 
            }
            a { 
                color: #007bff; 
                text-decoration: none; 
                font-weight: bold; 
                margin: 0 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ Test Réussi !</h1>
            <div class="status">
                🚀 L'application Flask fonctionne parfaitement sur Render
            </div>
            <p><strong>Boutique Mobile</strong> - Version de test</p>
            <p>
                <a href="/">🏠 Accueil</a>
                <a href="/scanner">📱 Scanner</a>
                <a href="/health">💚 Health</a>
            </p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check pour Render"""
    return jsonify({
        'status': 'ok',
        'app': 'Boutique Mobile',
        'version': '1.0',
        'message': 'Application fonctionnelle'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Démarrage sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
