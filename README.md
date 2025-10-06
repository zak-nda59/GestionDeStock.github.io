# 📦 GestionDeStock - Application de Gestion d'Inventaire

## 🎯 Description

Application web complète de gestion d'inventaire avec scanner de codes-barres intégré. Permet de gérer facilement les stocks de produits avec décrément automatique lors des scans.

## ✨ Fonctionnalités

- **📊 Gestion complète des produits** (CRUD)
- **📱 Scanner de codes-barres** (caméra + douchette)
- **⚡ Décrément automatique** du stock lors des scans
- **🚨 Alertes de stock** (rupture, stock faible, critique)
- **📈 Export CSV** des données
- **🖨️ Génération de codes-barres** pour impression
- **🔍 Recherche en temps réel**
- **📱 Interface responsive** (mobile-friendly)

## 🛠️ Technologies

- **Backend** : Python 3 + Flask
- **Base de données** : MySQL
- **Frontend** : HTML5 + CSS3 + Bootstrap 5 + JavaScript
- **Scanner** : QuaggaJS (codes-barres via caméra)
- **Codes-barres** : python-barcode

## 📋 Prérequis

- Python 3.7+
- MySQL Server
- Navigateur web moderne avec support caméra

## 🚀 Installation

### 1. Cloner le repository
```bash
git clone https://github.com/votre-username/GestionDeStock.git
cd GestionDeStock
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration MySQL
```bash
# Créer la base de données
mysql -u root -p
CREATE DATABASE gestion_inventaire;
USE gestion_inventaire;
SOURCE import_mysql.sql;
```

### 4. Configuration de l'application
Modifier les paramètres MySQL dans `app_simple.py` :
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'votre_mot_de_passe',
    'database': 'gestion_inventaire',
    'charset': 'utf8mb4'
}
```

### 5. Lancer l'application
```bash
python app_simple.py
```

L'application sera accessible sur : http://localhost:5004

## 📱 Utilisation

### Scanner de Codes-barres
1. **Caméra** : Cliquez "Démarrer Scanner" → Pointez vers le code-barres
2. **Douchette** : Connectez votre douchette → Scannez dans le champ
3. **Manuel** : Tapez le code-barres → Cliquez "-1 Stock"

### Gestion des Produits
- **Ajouter** : Formulaire simple avec nom, code-barres, prix, stock
- **Modifier** : Clic sur le produit dans la liste
- **Supprimer** : Bouton de suppression avec confirmation
- **Rechercher** : Barre de recherche en temps réel

### Codes-barres
- **Génération** : Automatique pour tous les produits
- **Impression** : Format étiquettes optimisé
- **Scan** : Compatible douchettes et caméras

## 📊 Structure du Projet

```
GestionDeStock/
├── app_simple.py          # Application Flask principale
├── requirements.txt       # Dépendances Python
├── import_mysql.sql      # Structure base de données
├── templates/            # Templates HTML
│   ├── simple.html       # Page d'accueil
│   ├── scanner_simple.html # Scanner
│   ├── codes_barres.html # Génération codes-barres
│   └── ...
├── static/              # Fichiers CSS/JS
│   ├── style.css
│   └── script.js
└── README.md
```

## 🔧 Configuration

### Codes de Test
- `123456789` - Coca-Cola (Stock: 10)
- `987654321` - Pain (Stock: 0)
- `555666777` - Lait (Stock: 2)

### Paramètres Scanner
- **Pause entre scans** : 1.5 secondes
- **Formats supportés** : Code128, EAN, UPC
- **Résolution caméra** : 640x480

## 📈 Fonctionnalités Avancées

### Alertes Stock
- **🚨 Rupture** : Stock = 0
- **⚠️ Critique** : Stock ≤ 2
- **📦 Faible** : Stock ≤ 5

### Export de Données
- **Stock faible** : Articles avec stock ≤ 5
- **Ruptures** : Articles en rupture de stock
- **Format** : CSV avec recommandations

## 🐛 Dépannage

### Problèmes courants
1. **Caméra ne fonctionne pas** : Vérifiez les permissions navigateur
2. **Codes-barres non détectés** : Améliorez l'éclairage
3. **Erreur MySQL** : Vérifiez la configuration de connexion

### Logs de Debug
L'application affiche des logs détaillés dans la console pour faciliter le debug.

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👤 Auteur

Votre nom - [@votre-github](https://github.com/votre-username)

## 🙏 Remerciements

- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Bootstrap](https://getbootstrap.com/) - Framework CSS
- [QuaggaJS](https://serratus.github.io/quaggaJS/) - Scanner codes-barres
- [python-barcode](https://python-barcode.readthedocs.io/) - Génération codes-barres
