#!/usr/bin/env python3
"""
Script pour préparer le projet GestionDeStock pour GitHub
"""

import os
import shutil
import json

def prepare_for_github():
    """Prépare le projet pour GitHub"""
    
    print("🚀 Préparation du projet pour GitHub...")
    
    # Dossier de destination
    github_dir = "GestionDeStock_GitHub"
    
    # Créer le dossier de destination
    if os.path.exists(github_dir):
        shutil.rmtree(github_dir)
    os.makedirs(github_dir)
    
    # Fichiers à copier
    files_to_copy = [
        # Application principale
        "app_simple.py",
        
        # Configuration
        "requirements.txt",
        "config_example.py",
        
        # Base de données
        "import_mysql.sql",
        "admin_db.py",
        
        # Documentation
        "README_GITHUB.md",
        "LICENSE",
        ".gitignore",
        
        # Dossiers complets
        "templates",
        "static"
    ]
    
    # Copier les fichiers
    for item in files_to_copy:
        src = item
        dst = os.path.join(github_dir, item)
        
        if os.path.isfile(src):
            print(f"📄 Copie: {src}")
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            print(f"📁 Copie dossier: {src}")
            shutil.copytree(src, dst)
        else:
            print(f"⚠️  Fichier non trouvé: {src}")
    
    # Renommer README
    old_readme = os.path.join(github_dir, "README_GITHUB.md")
    new_readme = os.path.join(github_dir, "README.md")
    if os.path.exists(old_readme):
        os.rename(old_readme, new_readme)
        print("📝 README renommé")
    
    # Créer un fichier d'instructions
    instructions = """
🎯 INSTRUCTIONS POUR GITHUB

1. Ouvrez un terminal dans le dossier GestionDeStock_GitHub
2. Exécutez les commandes suivantes :

git init
git add .
git commit -m "Initial commit - Application de gestion d'inventaire"
git remote add origin https://github.com/VOTRE-USERNAME/GestionDeStock.git
git branch -M main
git push -u origin main

3. Remplacez VOTRE-USERNAME par votre nom d'utilisateur GitHub

✅ Votre projet sera en ligne !
"""
    
    with open(os.path.join(github_dir, "INSTRUCTIONS.txt"), "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print(f"\n✅ Projet préparé dans le dossier: {github_dir}")
    print("📋 Lisez le fichier INSTRUCTIONS.txt pour la suite")
    
    return github_dir

if __name__ == "__main__":
    prepare_for_github()
