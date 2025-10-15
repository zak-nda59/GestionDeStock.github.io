# 📱 Boutique Mobile - Gestion d'Inventaire

Application complète de gestion d'inventaire avec scanner de codes-barres, développée avec Flask et SQLite.

## 🚀 Fonctionnalités

### 📱 Scanner Intelligent
- **Scanner caméra** avec détection automatique (QuaggaJS)
- **Scanner douchette** USB/Bluetooth compatible
- **Saisie manuelle** de codes-barres
- **Gestion stock** : Ajouter/Retirer avec validation
- **Interface intuitive** avec overlay rectangulaire

### 📦 Gestion Produits
- **CRUD complet** : Créer, Lire, Modifier, Supprimer
- **Catégories** avec emojis personnalisés
- **Codes-barres** générés automatiquement
- **Stock en temps réel** avec alertes

### 📊 Fonctionnalités Avancées
- **Statistiques** détaillées avec graphiques
- **Export CSV** des données
- **API JSON** pour intégrations
- **Interface responsive** (mobile/desktop)
- **Base de données** SQLite persistante

## 🛠️ Installation Locale

### Prérequis
- Python 3.10+
- pip (gestionnaire de paquets Python)

### Installation
```bash
# Cloner le repository
git clone https://github.com/votre-username/GestionStock.git
cd GestionStock

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

L'application sera accessible sur : http://localhost:5000

## 🌐 Déploiement sur Render

### 1. Préparer le Repository GitHub
1. **Créer un nouveau repository** sur GitHub
2. **Uploader tous les fichiers** de ce dossier
3. **Vérifier** que les fichiers suivants sont présents :
   - `app.py` (application principale)
   - `requirements.txt` (dépendances)
   - `runtime.txt` (version Python)
   - `templates/` (dossier avec les templates HTML)

### 2. Déployer sur Render
1. **Aller sur** [render.com](https://render.com)
2. **Se connecter** avec votre compte GitHub
3. **Cliquer** "New +" → "Web Service"
4. **Connecter** votre repository GitHub
5. **Configurer** :
   - **Name** : `boutique-mobile` (ou votre choix)
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn main:app` (version simple)
   - **Plan** : Free (gratuit)

### 🔧 Débogage
Si erreurs 500, tester avec :
- **Start Command** : `python main.py` (version de débogage)
- **URL de test** : `https://votre-app.onrender.com/test`
- **Health check** : `https://votre-app.onrender.com/health`

### 3. Variables d'Environnement (Optionnel)
Aucune variable d'environnement requise pour la version de base.

### 4. Déploiement Automatique
- **Push** sur GitHub → **Déploiement automatique** sur Render
- **URL publique** générée automatiquement
- **HTTPS** activé par défaut

## 📁 Structure du Projet

```
GestionStock/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── runtime.txt           # Version Python pour Render
├── README.md             # Documentation
└── templates/            # Templates HTML
    ├── index.html        # Page d'accueil
    ├── scanner_parfait.html  # Scanner avec caméra
    └── error.html        # Page d'erreur
```

## 🎯 Utilisation

### Scanner de Codes-barres
1. **Aller** sur la page d'accueil
2. **Cliquer** "📱 Scanner"
3. **Choisir** le mode :
   - **Saisie** : Taper/Scanner avec douchette
   - **Caméra** : Scanner visuel automatique
4. **Pointer** vers un code-barres
5. **Choisir** l'action : Ajouter/Retirer stock
6. **Valider** la quantité

### Gestion des Produits
- **Ajouter** : Nouveau produit avec code-barres auto
- **Modifier** : Nom, prix, catégorie (stock via scanner)
- **Consulter** : Vue d'ensemble avec filtres
- **Statistiques** : Graphiques et métriques

## 🔧 Configuration

### Base de Données
- **SQLite** : Base locale `boutique_mobile.db`
- **Auto-création** : Tables et données d'exemple
- **Persistance** : Données conservées entre redémarrages

### Catégories par Défaut
- 📱 Écran, 🔋 Batterie, 🛡️ Coque
- 🔌 Câble, 🎧 Audio, 🔧 Outil
- 💾 Composant, 📎 Accessoire, 📦 Autre

## 🚨 Dépannage

### Problèmes Courants
1. **Caméra noire** : Autoriser l'accès caméra dans le navigateur
2. **Scanner ne détecte pas** : Utiliser le mode saisie manuelle
3. **Erreur de build** : Vérifier `requirements.txt` et `runtime.txt`

### Support Navigateurs
- ✅ **Chrome/Edge** : Support complet
- ✅ **Firefox** : Support complet  
- ✅ **Safari** : Support partiel (caméra limitée)
- ✅ **Mobile** : Compatible iOS/Android

## 📱 API Endpoints

### Scanner
- `POST /scan` : Scanner un code-barres
- `POST /ajuster-stock` : Ajuster stock manuellement

### Données
- `GET /api/produits` : Liste des produits (JSON)
- `GET /api/stats` : Statistiques (JSON)
- `GET /export` : Export CSV

## 🎨 Personnalisation

### Interface
- **Couleurs** : Modifier les gradients CSS
- **Emojis** : Changer les icônes des catégories
- **Layout** : Adapter les templates HTML

### Fonctionnalités
- **Ajouter routes** dans `app.py`
- **Nouveaux templates** dans `templates/`
- **Styles CSS** directement dans les templates

## 📄 Licence

Projet open source - Libre d'utilisation et modification.

## 🤝 Contribution

1. **Fork** le repository
2. **Créer** une branche feature
3. **Commit** les changements
4. **Push** et créer une Pull Request

---

**Développé avec ❤️ pour simplifier la gestion d'inventaire**
