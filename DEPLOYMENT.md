# 🚀 Déploiement de l'Application

## 🌐 Options d'Hébergement Gratuit

### 1. **Render** (Recommandé - Gratuit)

1. **Allez sur** : https://render.com
2. **Créez un compte** gratuit
3. **Cliquez** "New +" → "Web Service"
4. **Connectez** votre repository GitHub `GestionDeStock`
5. **Configuration** :
   - Name: `gestiondestock`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app_simple.py`
6. **Cliquez** "Create Web Service"

**✅ Votre app sera accessible sur** : `https://gestiondestock.onrender.com`

### 2. **Railway** (Alternative)

1. **Allez sur** : https://railway.app
2. **Connectez** GitHub
3. **Deploy** votre repository
4. **Variables d'environnement** : Aucune nécessaire

### 3. **Heroku** (Payant maintenant)

Heroku n'est plus gratuit depuis 2022.

## ⚙️ Configuration Automatique

L'application est déjà configurée pour :
- ✅ **Port dynamique** (variable PORT)
- ✅ **Base SQLite intégrée** (pas besoin de MySQL externe)
- ✅ **Produits d'exemple** auto-créés
- ✅ **Mode production** (debug désactivé)

## 🎯 Après Déploiement

Une fois déployé, votre application aura :
- **Scanner de codes-barres** fonctionnel
- **Gestion complète des produits**
- **Export CSV**
- **Interface responsive**
- **Accès mondial via URL**

## 🔧 Dépannage

Si l'application ne démarre pas :
1. Vérifiez les logs sur la plateforme
2. Assurez-vous que `requirements.txt` est correct
3. Le port est configuré automatiquement

## 📱 Test de l'Application

Une fois déployée, testez :
1. **Page d'accueil** : Liste des produits
2. **Scanner** : Fonctionne avec caméra
3. **Codes-barres** : Génération et affichage
4. **CRUD** : Ajouter/modifier/supprimer produits
