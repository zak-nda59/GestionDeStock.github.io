#!/usr/bin/env python3
"""
🚀 SCRIPT DE DÉPLOIEMENT AUTOMATIQUE
Prépare et guide le déploiement sur GitHub + Render
"""

import os
import subprocess
import sys

def print_banner():
    print("🚀 BOUTIQUE MOBILE - DÉPLOIEMENT AUTOMATIQUE")
    print("=" * 60)
    print("📱 Application de gestion d'inventaire")
    print("🌐 Déploiement sur GitHub + Render")
    print()

def check_git():
    """Vérifie si Git est installé"""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def init_git_repo():
    """Initialise le repository Git"""
    print("📁 Initialisation du repository Git...")
    
    try:
        # Initialiser le repo
        subprocess.run(['git', 'init'], check=True)
        print("✅ Repository Git initialisé")
        
        # Ajouter tous les fichiers
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Fichiers ajoutés au staging")
        
        # Premier commit
        subprocess.run(['git', 'commit', '-m', 'Initial commit - Boutique Mobile App'], check=True)
        print("✅ Premier commit créé")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur Git: {e}")
        return False

def list_files():
    """Liste tous les fichiers du projet"""
    print("📋 FICHIERS DU PROJET:")
    print("-" * 30)
    
    files = []
    for root, dirs, filenames in os.walk('.'):
        # Ignorer les dossiers cachés
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in filenames:
            if not filename.startswith('.'):
                filepath = os.path.join(root, filename)
                files.append(filepath)
    
    # Organiser par type
    templates = [f for f in files if 'templates' in f]
    config_files = [f for f in files if f.endswith(('.txt', '.yaml', '.md', '.py'))]
    
    print("🎨 Templates HTML:")
    for f in sorted(templates):
        print(f"   {f}")
    
    print("\n⚙️ Fichiers de configuration:")
    for f in sorted(config_files):
        if 'templates' not in f:
            print(f"   {f}")
    
    print(f"\n📊 Total: {len(files)} fichiers")
    return len(files)

def check_requirements():
    """Vérifie les fichiers requis"""
    print("\n🔍 VÉRIFICATION DES FICHIERS REQUIS:")
    print("-" * 40)
    
    required_files = [
        'app.py',
        'requirements.txt',
        'runtime.txt',
        'README.md',
        'templates/index.html',
        'templates/produits.html',
        'templates/ajouter.html',
        'templates/modifier.html',
        'templates/scanner.html',
        'templates/statistiques.html',
        'templates/codes_barres.html',
        'templates/ruptures.html',
        'templates/stock_faible.html',
        'templates/error.html'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MANQUANT")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ {len(missing_files)} fichier(s) manquant(s)")
        return False
    else:
        print(f"\n✅ Tous les fichiers requis sont présents ({len(required_files)} fichiers)")
        return True

def show_deployment_guide():
    """Affiche le guide de déploiement"""
    print("\n🌐 GUIDE DE DÉPLOIEMENT SUR RENDER:")
    print("=" * 50)
    
    print("\n1️⃣ CRÉER UN REPOSITORY GITHUB:")
    print("   • Allez sur https://github.com")
    print("   • Cliquez 'New repository'")
    print("   • Nom: 'boutique-mobile' (ou autre)")
    print("   • Public ou Private")
    print("   • Ne pas initialiser avec README")
    print("   • Créer le repository")
    
    print("\n2️⃣ POUSSER LE CODE:")
    print("   • Copiez l'URL de votre repository")
    print("   • Exécutez ces commandes:")
    print("     git remote add origin https://github.com/USERNAME/boutique-mobile.git")
    print("     git branch -M main")
    print("     git push -u origin main")
    
    print("\n3️⃣ DÉPLOYER SUR RENDER:")
    print("   • Allez sur https://render.com")
    print("   • Connectez-vous / Créez un compte")
    print("   • Cliquez 'New +' → 'Web Service'")
    print("   • Connectez votre repository GitHub")
    print("   • Sélectionnez 'boutique-mobile'")
    
    print("\n4️⃣ CONFIGURATION RENDER:")
    print("   • Name: boutique-mobile")
    print("   • Environment: Python 3")
    print("   • Build Command: pip install -r requirements.txt")
    print("   • Start Command: gunicorn app:app")
    print("   • Instance Type: Free")
    
    print("\n5️⃣ BASE DE DONNÉES:")
    print("   • Dans Render, cliquez 'New +' → 'PostgreSQL'")
    print("   • Name: boutique-mobile-db")
    print("   • Plan: Free")
    print("   • Créer la base")
    print("   • Copiez l'URL de connexion")
    
    print("\n6️⃣ VARIABLES D'ENVIRONNEMENT:")
    print("   • Dans votre Web Service → Environment")
    print("   • Ajoutez: DATABASE_URL = [URL PostgreSQL]")
    
    print("\n7️⃣ DÉPLOIEMENT:")
    print("   • Cliquez 'Create Web Service'")
    print("   • Attendez le build (5-10 minutes)")
    print("   • Votre app sera sur: https://boutique-mobile-XXXX.onrender.com")

def main():
    print_banner()
    
    # Vérifier Git
    if not check_git():
        print("❌ Git n'est pas installé. Installez Git d'abord.")
        print("   Téléchargez sur: https://git-scm.com/")
        return
    
    # Lister les fichiers
    file_count = list_files()
    
    # Vérifier les fichiers requis
    if not check_requirements():
        print("\n❌ Des fichiers sont manquants. Vérifiez votre installation.")
        return
    
    print(f"\n✅ PROJET PRÊT POUR LE DÉPLOIEMENT!")
    print(f"📁 {file_count} fichiers préparés")
    print("🚀 Application complète avec toutes les fonctionnalités")
    
    # Demander si on initialise Git
    response = input("\n🤔 Voulez-vous initialiser le repository Git ? (o/n): ").lower()
    if response in ['o', 'oui', 'y', 'yes']:
        if init_git_repo():
            print("\n✅ Repository Git prêt!")
        else:
            print("\n❌ Erreur lors de l'initialisation Git")
    
    # Afficher le guide
    show_deployment_guide()
    
    print("\n🎉 FÉLICITATIONS!")
    print("Votre application Boutique Mobile est prête à être déployée!")
    print("Suivez le guide ci-dessus pour la mettre en ligne.")
    print("\n📱 Fonctionnalités incluses:")
    print("   ✅ Gestion complète des produits")
    print("   ✅ Scanner codes-barres (caméra + douchette)")
    print("   ✅ Filtres et tris avancés")
    print("   ✅ Statistiques avec graphiques")
    print("   ✅ Alertes automatiques")
    print("   ✅ Export CSV")
    print("   ✅ Interface moderne et responsive")
    print("   ✅ Base de données persistante")
    
    print("\n🌐 Une fois déployée, votre app sera accessible partout!")

if __name__ == "__main__":
    main()
