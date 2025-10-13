# 📱 Gestion d'Inventaire - Boutique Réparation Mobile

Application Flask complète pour la gestion d'inventaire d'une boutique de réparation de téléphones mobiles.

## 🚀 Fonctionnalités

### 📦 Gestion des Produits
- ✅ **CRUD complet** : Créer, Lire, Modifier, Supprimer
- ✅ **Catégories spécialisées** : Écran, Batterie, Coque, Housse, Verre Trempé, Câble, Outil, Accessoire
- ✅ **Filtres avancés** : Par catégorie, recherche, tri multiple
- ✅ **Sauvegarde permanente** : Les produits restent en base jusqu'à suppression manuelle

### 📱 Scanner de Codes-barres
- ✅ **Scanner caméra** : Via navigateur avec QuaggaJS
- ✅ **Douchette USB/Bluetooth** : Compatible toutes marques
- ✅ **Décrément automatique** : -1 stock à chaque scan
- ✅ **Alertes intelligentes** : Stock critique, rupture

### 📊 Statistiques & Rapports
- ✅ **Graphiques interactifs** : Chart.js avec secteurs et barres
- ✅ **Stats par catégorie** : Répartition, stock, prix
- ✅ **Produits attention** : Stock faible/rupture
- ✅ **Export CSV** : Sauvegarde complète

### 🏷️ Codes-barres
- ✅ **Génération automatique** : Format Code 128
- ✅ **Impression sélective** : Par catégorie
- ✅ **Tailles ajustables** : Petite, moyenne, grande

## 🛠️ Stack Technique

### Backend
- **Python 3.10** : Langage principal
- **Flask 2.3.2** : Framework web
- **PostgreSQL** : Base de données production (Render)
- **MySQL** : Base de données développement local

### Frontend
- **Bootstrap 5.3.2** : Framework CSS responsive
- **JavaScript Vanilla** : Interactions dynamiques
- **QuaggaJS** : Scanner codes-barres caméra
- **Chart.js** : Graphiques statistiques
- **JsBarcode** : Génération codes-barres

## 🌐 Déploiement

### Production (Render)
1. **Fork ce repository** sur GitHub
2. **Connectez Render** à votre repository
3. **Render détecte automatiquement** :
   - `render.yaml` : Configuration service
   - `requirements.txt` : Dépendances Python
   - `runtime.txt` : Version Python 3.10.12
4. **Base PostgreSQL** créée automatiquement
5. **Application déployée** sur URL Render

### Développement Local
```bash
# Cloner le repository
git clone [votre-repo]
cd GestionDeStock_Render

# Installer les dépendances
pip install -r requirements.txt

# Démarrer WAMP/XAMPP (MySQL)
# Lancer l'application
python app.py
```

## 📁 Structure du Projet

```
GestionDeStock_Render/
├── app.py                          # Application Flask principale
├── requirements.txt                # Dépendances Python
├── runtime.txt                     # Version Python pour Render
├── render.yaml                     # Configuration Render
├── README.md                       # Documentation
└── templates/                      # Templates HTML
    ├── mobile_shop.html           # Page d'accueil avec filtres
    ├── ajouter_mobile.html        # Formulaire ajout produit
    ├── modifier_mobile.html       # Formulaire modification
    ├── scanner_mobile.html        # Scanner codes-barres
    ├── codes_barres_mobile.html   # Génération codes-barres
    └── statistiques_mobile.html   # Tableaux de bord
```

## 🎯 Utilisation

### 1. Ajouter des Produits
- Allez sur `/ajouter`
- Choisissez la catégorie (suggestions automatiques)
- Remplissez nom, code-barres, prix, stock
- **Sauvegarde permanente** en base

### 2. Scanner des Produits
- Allez sur `/scanner`
- **Caméra** : Cliquez "Démarrer" et pointez vers le code
- **Douchette** : Scannez dans le champ de saisie
- **Stock décrémenté automatiquement** (-1)

### 3. Gérer l'Inventaire
- **Page d'accueil** : Vue d'ensemble avec filtres
- **Tri** : Nom, prix, stock, catégorie
- **Recherche** : Par nom ou code-barres
- **Modification** : Clic sur un produit

### 4. Analyser les Données
- **Statistiques** : `/statistiques` pour graphiques
- **Codes-barres** : `/codes-barres` pour impression
- **Export** : `/export` pour CSV

## 🔧 Configuration

### Variables d'Environnement
- `DATABASE_URL` : URL PostgreSQL (auto sur Render)
- `SECRET_KEY` : Clé secrète Flask (auto-générée)
- `PORT` : Port d'écoute (auto sur Render)

### Base de Données
- **Production** : PostgreSQL automatique sur Render
- **Développement** : MySQL local (WAMP/XAMPP)
- **Auto-initialisation** : Tables créées au premier lancement

## 📱 Interface Mobile

- ✅ **Responsive Design** : Bootstrap 5 adaptatif
- ✅ **Touch-friendly** : Boutons optimisés tactile
- ✅ **Scanner mobile** : Caméra smartphone compatible
- ✅ **Navigation intuitive** : Menu burger, icônes

## 🔒 Sécurité

- ✅ **Validation des données** : Côté client et serveur
- ✅ **Protection CSRF** : Flask-WTF intégré
- ✅ **Sanitisation SQL** : Requêtes préparées
- ✅ **Variables d'environnement** : Secrets sécurisés

## 📈 Performance

- ✅ **CDN Bootstrap** : Chargement rapide CSS/JS
- ✅ **Requêtes optimisées** : Index sur codes-barres
- ✅ **Cache navigateur** : Assets statiques
- ✅ **Compression Gzip** : Render automatique

## 🆘 Support

### Problèmes Courants
1. **Erreur base de données** : Vérifiez WAMP/MySQL local
2. **Scanner ne fonctionne pas** : Autorisez accès caméra
3. **Codes-barres illisibles** : Ajustez taille/qualité impression

### Logs de Debug
- **Local** : Console Python avec messages détaillés
- **Production** : Logs Render dans dashboard

## 📄 Licence

MIT License - Libre d'utilisation commerciale et personnelle.

## 👨‍💻 Auteur

Développé pour boutique de réparation mobile avec focus sur l'efficacité et la simplicité d'utilisation.

---

**🚀 Prêt pour le déploiement sur Render !**
