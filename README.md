# 📦 Application de Gestion d'Inventaire avec Scanner

Une application web complète et responsive pour la gestion d'inventaire avec scanner de codes-barres intégré, développée avec Flask et compatible avec tous les appareils (PC, tablettes, smartphones).

## 🎯 Fonctionnalités

### ✅ Gestion des Produits
- **Ajout de produits** avec nom, code-barres, prix et stock initial
- **Modification** des informations produit
- **Suppression** de produits avec confirmation
- **Visualisation** de la liste complète avec statuts de stock

### 📱 Scanner de Codes-barres
- **Scanner par douchette USB/Bluetooth** (fonctionne comme un clavier)
- **Scanner par caméra** (smartphone, tablette, webcam PC)
- **Saisie manuelle** de codes-barres
- **Décrément automatique** du stock à chaque scan
- **Historique des scans** en temps réel

### 📊 Alertes de Stock
- **Rupture de stock** (stock = 0) → Message rouge
- **Stock faible** (stock < 2) → Alerte orange
- **Stock disponible** (stock ≥ 2) → Statut vert

### 📈 Statistiques et Rapports
- **Graphiques interactifs** (Chart.js) :
  - Stock par produit (barres)
  - Répartition du stock (secteurs)
  - Valeur par produit (ligne)
  - Statut des stocks (donut)
- **Statistiques générales** : total produits, stock total, prix moyen
- **Export CSV/Excel** de l'inventaire complet

### 🎨 Interface Utilisateur
- **Design responsive** (Bootstrap 5)
- **Compatible** PC, tablettes, smartphones
- **Interface moderne** avec icônes Bootstrap
- **Navigation intuitive**
- **Thème professionnel**

## 🛠️ Technologies Utilisées

### Backend
- **Python 3.8+**
- **Flask** (serveur web)
- **SQLite** (base de données)
- **Pandas** (export Excel/CSV)

### Frontend
- **HTML5 + CSS3**
- **Bootstrap 5** (interface responsive)
- **JavaScript Vanilla** (interactions)
- **QuaggaJS** (scanner caméra)
- **Chart.js** (graphiques)

## 📋 Prérequis

- **Python 3.8 ou supérieur**
- **Navigateur web moderne** (Chrome, Firefox, Safari, Edge)
- **Caméra** (optionnel, pour le scan par caméra)
- **Douchette USB/Bluetooth** (optionnel)

## 🚀 Installation

### 1. Cloner ou télécharger le projet
```bash
# Si vous avez git
git clone <url-du-projet>
cd GestionDestock

# Ou téléchargez et décompressez l'archive
```

### 2. Installer Python et les dépendances
```bash
# Vérifier la version de Python
python --version

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Lancer l'application
```bash
# Démarrer le serveur Flask
python app.py

# Ou avec flask run
flask run
```

### 4. Accéder à l'application
Ouvrez votre navigateur et allez à :
- **URL locale** : http://localhost:5000
- **Réseau local** : http://[votre-ip]:5000

## 📱 Utilisation

### Premier Démarrage
1. L'application crée automatiquement la base de données `database.db`
2. Des produits d'exemple sont ajoutés pour tester
3. Accédez à l'interface via votre navigateur

### Ajouter un Produit
1. Cliquez sur **"Ajouter un produit"**
2. Remplissez les informations :
   - Nom du produit
   - Code-barres (ou scannez avec la caméra)
   - Prix unitaire
   - Stock initial
3. Validez avec **"Ajouter le produit"**

### Scanner un Produit
1. Allez dans **"Scanner"**
2. Choisissez votre méthode :
   - **Douchette** : Scannez directement dans le champ
   - **Caméra** : Cliquez sur "Démarrer la caméra"
   - **Manuel** : Tapez le code-barres
3. Le stock est automatiquement décrémenté

### Consulter les Statistiques
1. Cliquez sur **"Statistiques"**
2. Visualisez :
   - Graphiques interactifs
   - Statistiques générales
   - Tableau détaillé par produit

### Exporter les Données
1. Dans le menu **"Exporter"**
2. Choisissez le format :
   - **CSV** : Compatible Excel, LibreOffice
   - **Excel** : Fichier .xlsx natif

## 🔧 Configuration

### Modifier le Port
Dans `app.py`, ligne finale :
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Changez 5000
```

### Accès Réseau
Pour accéder depuis d'autres appareils :
1. Trouvez votre adresse IP locale
2. Accédez à `http://[votre-ip]:5000`
3. Assurez-vous que le pare-feu autorise le port 5000

### Base de Données
- **Fichier** : `database.db` (créé automatiquement)
- **Sauvegarde** : Copiez simplement le fichier
- **Reset** : Supprimez le fichier, il sera recréé au démarrage

## 📂 Structure du Projet

```
GestionDestock/
├── app.py                     # Application Flask principale
├── database.db                # Base de données SQLite (auto-créée)
├── requirements.txt           # Dépendances Python
├── README.md                  # Ce fichier
├── static/                    # Fichiers statiques
│   ├── style.css              # Styles personnalisés
│   └── script.js              # JavaScript principal
└── templates/                 # Templates HTML
    ├── layout.html            # Template de base
    ├── index.html             # Page d'accueil
    ├── scanner.html           # Page de scan
    ├── ajouter.html           # Ajout de produit
    ├── modifier.html          # Modification de produit
    └── statistiques.html      # Page des statistiques
```

## 🔍 Dépannage

### Problèmes Courants

**1. Erreur "Module not found"**
```bash
pip install -r requirements.txt
```

**2. Port déjà utilisé**
- Changez le port dans `app.py`
- Ou arrêtez l'autre application utilisant le port 5000

**3. Caméra ne fonctionne pas**
- Vérifiez les permissions de la caméra dans le navigateur
- Utilisez HTTPS pour certains navigateurs (Chrome sur mobile)
- Testez avec un autre navigateur

**4. Scanner ne détecte pas les codes**
- Assurez-vous que le code-barres est bien visible
- Ajustez l'éclairage
- Testez avec différents types de codes-barres

**5. Base de données corrompue**
- Supprimez `database.db`
- Redémarrez l'application (elle recrée la base)

### Logs et Debug
- Les erreurs s'affichent dans la console du navigateur (F12)
- Les logs serveur s'affichent dans le terminal
- Mode debug activé par défaut (désactivez en production)

## 🔒 Sécurité

### Recommandations
- **Changez la clé secrète** dans `app.py`
- **Désactivez le mode debug** en production
- **Utilisez HTTPS** pour l'accès distant
- **Sauvegardez régulièrement** la base de données

### Production
Pour un déploiement en production :
```python
# Dans app.py, changez :
app.run(debug=False, host='127.0.0.1', port=5000)
```

## 📞 Support

### Fonctionnalités Supportées
- ✅ Tous navigateurs modernes
- ✅ Windows, macOS, Linux
- ✅ Android, iOS (navigateur)
- ✅ Tablettes
- ✅ Douchettes USB/Bluetooth
- ✅ Webcams et caméras mobiles

### Codes-barres Supportés
- EAN-13, EAN-8
- UPC-A, UPC-E
- Code 128, Code 39
- Codabar
- Interleaved 2 of 5

## 🎉 Utilisation Avancée

### Raccourcis Clavier
- **Ctrl+K** : Focus sur la recherche
- **Échap** : Fermer les scanners/modals
- **Ctrl+S** : Démarrer le scanner (page scanner)

### API Endpoints
- `GET /` : Page d'accueil
- `GET /scanner` : Page de scan
- `POST /api/scan` : Traiter un scan
- `GET /api/produits` : Liste des produits (JSON)
- `GET /export/csv` : Export CSV
- `GET /export/excel` : Export Excel

### Personnalisation
- Modifiez `static/style.css` pour le design
- Ajoutez des fonctionnalités dans `app.py`
- Personnalisez les templates HTML

## 📄 Licence

Ce projet est fourni "tel quel" à des fins éducatives et professionnelles.

---

**🚀 Votre application de gestion d'inventaire est prête !**

Lancez `python app.py` et accédez à http://localhost:5000 pour commencer.
