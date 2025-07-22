# 🚀 Guide de Configuration - iQuesta Automation

## 📋 Fichiers nécessaires pour le fonctionnement

Quand vous partagez ou déployez ce projet, certains fichiers **non versionnés** sont **OBLIGATOIRES** pour le bon fonctionnement.

## 🔴 **FICHIERS CRITIQUES À CRÉER**

### 1. **Fichier `.env` (OBLIGATOIRE)**
```bash
# Copiez .env.example vers .env et remplissez :
cp .env.example .env
```

Contenu minimum requis :
```env
USER_EMAIL=votre@email.com
DATABASE_PATH=./database/users.db
```

### 2. **Dossier `cv_files/` avec fichiers (OBLIGATOIRE)**
```bash
mkdir -p cv_files
# Ajoutez vos fichiers :
# - CV au format PDF
# - Lettre de motivation au format PDF
```

Exemple de structure :
```
cv_files/
├── mon_cv.pdf
└── ma_lettre_motivation.pdf
```

### 3. **Créer un utilisateur de test (OBLIGATOIRE)**
```bash
python add_test_user.py
```

## ⚠️ **Conséquences si fichiers manquants :**

| Fichier manquant | Impact | Erreur |
|------------------|--------|---------|
| `.env` | ❌ **Critique** | Script ne démarre pas |
| `cv_files/` | ❌ **Critique** | Erreur upload fichiers |
| Base utilisateur | ❌ **Critique** | Aucun utilisateur configuré |
| `__pycache__/` | ✅ **OK** | Se recrée automatiquement |

## 🛠️ **Installation complète sur nouvelle machine :**

### Étape 1 : Cloner le repository
```bash
git clone git@github.com:douuvid/Iquestra.git
cd Iquestra
```

### Étape 2 : Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 3 : Configuration
```bash
# 1. Créer le fichier de configuration
cp .env.example .env
# Éditer .env avec vos valeurs

# 2. Créer le dossier CV
mkdir -p cv_files
# Ajouter vos fichiers CV et LM

# 3. Créer un utilisateur de test
python add_test_user.py
```

### Étape 4 : Test
```bash
python scraper/iquesta_scraper.py --email votre@email.com
```

## 📦 **Partage sécurisé du projet :**

### ✅ **Méthode recommandée :**
1. **Partager via GitHub** (code source uniquement)
2. **Fournir ce guide** pour la configuration
3. **L'autre personne crée ses propres fichiers** `.env` et `cv_files/`

### ❌ **À éviter :**
- Partager le dossier complet avec vos CV personnels
- Inclure le fichier `.env` avec vos données
- Partager la base de données avec vos informations

## 🎯 **Résumé :**

**Fichiers versionnés** (sur GitHub) : ✅ Code source complet  
**Fichiers à créer** : ⚠️ `.env`, `cv_files/`, utilisateur test  
**Fichiers optionnels** : ✅ Se recréent automatiquement  

Avec ce guide, n'importe qui peut configurer et utiliser l'automatisation iQuesta ! 🚀
