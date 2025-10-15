# 🚀 DÉPLOIEMENT SIMPLE - BOUTIQUE MOBILE

## 📁 FICHIERS À UPLOADER SUR GITHUB

Uploadez **TOUS** les fichiers de ce dossier sur votre repository GitHub :

### ✅ Fichiers obligatoires
- `app.py` - Application Flask originale
- `requirements.txt` - Dépendances Python
- `runtime.txt` - Python 3.10.12
- `Procfile` - Configuration Render
- `templates/index.html` - Page d'accueil
- `templates/scanner_parfait.html` - Scanner avec caméra
- `templates/error.html` - Page d'erreur

### ✅ Fichiers optionnels
- `README.md` - Documentation
- `.gitignore` - Fichiers à ignorer

## 🔧 CONFIGURATION RENDER

### Settings → Build & Deploy
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
Health Check Path: /health
```

### Variables d'environnement
**Aucune variable requise** - Tout est auto-configuré !

## 🎯 FONCTIONNALITÉS INCLUSES

### ✅ Application complète
- 📱 **Scanner** avec caméra QuaggaJS + saisie manuelle
- 📊 **Base SQLite** avec 7 produits d'exemple
- 🔍 **Recherche** par nom/code-barres
- 🏷️ **Catégories** avec filtres
- 📈 **Statistiques** temps réel
- 🎨 **Interface moderne** Bootstrap responsive

### ✅ API REST
- `GET /` - Page d'accueil
- `GET /scanner` - Scanner
- `POST /scan` - API de scan
- `GET /api/produits` - Liste produits JSON
- `GET /health` - Health check

## 🚀 INSTRUCTIONS

1. **Supprimez** tout sur votre repository GitHub
2. **Uploadez** tous les fichiers de ce dossier
3. **Configurez** Render : `gunicorn app:app`
4. **Testez** votre application !

## ✅ APRÈS DÉPLOIEMENT

Votre application aura :
- 🏠 Page d'accueil avec produits
- 📱 Scanner fonctionnel
- 📊 Base de données persistante
- 🔧 API JSON complète

**C'est votre application originale, exactement comme elle était !** 🎉
