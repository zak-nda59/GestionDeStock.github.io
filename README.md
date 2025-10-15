# 📱 Boutique Mobile - Gestion d'Inventaire

## 🚀 Description
Application de gestion d'inventaire avec scanner de codes-barres développée en Flask.

## ✨ Fonctionnalités
- 📱 Scanner de codes-barres (caméra + saisie manuelle)
- 📊 Gestion complète des produits et stock
- 🏷️ Catégories avec emojis
- 📈 Statistiques en temps réel
- 🔍 Recherche et filtres avancés
- 📤 Export CSV des données
- 🎨 Interface moderne et responsive

## 🛠️ Installation

### Prérequis
- Python 3.10+
- pip

### Installation locale
```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

L'application sera accessible sur http://localhost:5000

## 🌐 Déploiement sur Render

### Configuration
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Health Check Path**: `/health`

### Fichiers requis
- ✅ `app.py` - Application principale
- ✅ `requirements.txt` - Dépendances Python
- ✅ `runtime.txt` - Version Python (3.10.12)
- ✅ `Procfile` - Configuration serveur
- ✅ `templates/` - Templates HTML

## 📱 Utilisation

### Page d'accueil
- Vue d'ensemble des produits
- Statistiques en temps réel
- Recherche rapide

### Scanner
- Mode caméra avec détection automatique
- Mode saisie manuelle
- Gestion du stock en temps réel

### API
- `GET /api/produits` - Liste des produits
- `POST /scan` - Scanner un code-barres
- `GET /health` - Health check

## 🎯 Fonctionnalités principales

### Base de données
- SQLite intégré
- 7 produits d'exemple
- 9 catégories pré-définies
- Auto-création des tables

### Scanner
- Compatible caméra (QuaggaJS)
- Compatible douchette USB/Bluetooth
- Validation en temps réel
- Gestion des erreurs

### Interface
- Design Bootstrap moderne
- Responsive mobile/desktop
- Animations fluides
- Navigation intuitive

## 🔧 Structure du projet
```
GestionStock_Original/
├── app.py                    # Application Flask
├── requirements.txt          # Dépendances
├── runtime.txt              # Version Python
├── Procfile                 # Configuration Render
├── README.md                # Documentation
├── .gitignore               # Fichiers à ignorer
└── templates/               # Templates HTML
    ├── index.html           # Page d'accueil
    ├── scanner_parfait.html # Scanner
    └── error.html           # Page d'erreur
```

## 🚀 Prêt pour la production !

Cette application est optimisée pour un déploiement facile sur Render avec toutes les fonctionnalités de gestion d'inventaire.
