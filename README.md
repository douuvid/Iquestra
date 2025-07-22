# iQuesta Automation - Scraper de Candidatures

🤖 **Automatisation de candidatures sur iQuesta.com**

Ce projet automatise le processus de candidature sur le site iQuesta en utilisant Selenium WebDriver pour :
- Rechercher des offres d'emploi par métier et région
- Filtrer par type de contrat (CDI, CDD, etc.)
- Remplir automatiquement les formulaires de candidature
- Télécharger CV et lettre de motivation
- Soumettre les candidatures

## 🎯 Fonctionnalités

### ✅ Fonctionnalités implémentées
- ✅ **Sélection de région** : Sélection automatique de "Île-de-France" (value="10")
- ✅ **Recherche par métier** : Recherche automatisée par mots-clés
- ✅ **Filtrage par contrat** : Filtrage CDI/CDD/Stage/Alternance
- ✅ **Gestion des cookies** : Acceptation automatique des cookies
- ✅ **Base de données** : Stockage des candidatures et profils utilisateurs
- ✅ **Gestion d'erreurs** : Logs détaillés et gestion des exceptions
- ✅ **Remplissage de formulaires** : Automatisation complète des champs

### 🚧 En cours de développement
- 🔄 **Optimisation de la soumission** : Amélioration de la robustesse du clic "Postuler"
- 🔄 **Gestion des erreurs réseau** : Récupération automatique en cas d'erreur

## 📁 Structure du projet

```
iquesta_automation/
├── scraper/
│   ├── iquesta_scraper.py       # Script principal
│   ├── search_handler.py        # Gestion de la recherche
│   ├── search_utils.py          # Utilitaires de recherche
│   └── application_handler.py   # Gestion des candidatures
├── database/
│   └── user_database.py         # Gestion de la base de données
├── cv_files/                    # Fichiers CV et LM (non versionnés)
├── .env                         # Variables d'environnement (non versionné)
└── README.md
```

## 🚀 Installation et utilisation

### Prérequis
- Python 3.8+
- Chrome/Chromium installé
- ChromeDriver (géré automatiquement par webdriver-manager)

### Installation
```bash
pip install selenium webdriver-manager python-dotenv
```

### Configuration
1. Créer un utilisateur test :
```bash
python add_test_user.py
```

2. Lancer l'automatisation :
```bash
python scraper/iquesta_scraper.py --email votre@email.com
```

## 📊 Résultats récents

### Test du 20/07/2025 - 00:54
- ✅ **Sélection de région** : "Île-de-France" correctement sélectionnée (`regions=10`)
- ✅ **Recherche** : 15 offres trouvées pour "Développeur Web"
- ✅ **Filtrage** : Filtrage CDI appliqué avec succès
- 🔄 **Candidatures** : En cours d'optimisation

## 🛠️ Corrections récentes

### Corrections majeures appliquées :
1. **Sélection de région** : Correction de la fonction `try_select_region`
   - Suppression de la dépendance à `form_parent`
   - Appel direct et systématique de la fonction
   - Sélection fiable par `value="10"` pour "Île-de-France"

2. **Gestion des variables** : 
   - Correction `region_target_target` → `region_target`
   - Suppression des références `form_parent` obsolètes

3. **Robustesse du code** :
   - Amélioration de la gestion d'erreurs
   - Logs détaillés pour le debugging
   - Fallbacks JavaScript pour les clics

## 🎯 Objectifs

L'objectif principal est de créer un système d'automatisation fiable qui :
- Respecte le workflow manuel exact du site
- Gère les erreurs de manière robuste
- Maintient un taux de succès élevé pour les candidatures
- Évite la détection comme bot

## 📝 Logs et debugging

Le système génère des logs détaillés pour chaque étape :
- Initialisation du navigateur
- Recherche et sélection de région
- Traitement des offres
- Remplissage et soumission des formulaires

## 📦 Extraction de code pour intégration

### 🎯 **Fonctions essentielles à conserver**

Si vous voulez intégrer cette automatisation dans un autre projet, voici les éléments **indispensables** :

#### 🥇 **PRIORITÉ 1 - Fonctions critiques :**

**1. Sélection de région** (`search_utils.py`) :
```python
def try_select_region(driver, region_target):
    """Sélectionne Île-de-France (value='10') dans le formulaire iQuesta"""
    # Cette fonction est CRUCIALE - elle gère la sélection "Île-de-France" (value="10")
    # C'était le problème principal que nous avons résolu !
```

**2. Soumission de candidature** (`application_handler.py`) :
```python
def verifier_et_postuler(driver, user_data):
    """Remplit et soumet le formulaire de candidature complet"""
    # Fonction complète qui :
    # - Remplit tous les champs (email, nom, prénom, message)
    # - Upload CV et lettre de motivation
    # - Clique sur "Postuler" avec plusieurs méthodes de fallback
```

**3. Recherche d'offres** (`search_handler.py`) :
```python
def rechercher_offres(driver, metier=None, region_text=None):
    """Gère la recherche complète avec sélection de région"""
```

#### 🥈 **PRIORITÉ 2 - Configuration Selenium :**
```python
def initialiser_driver():
    """Initialise Chrome avec les bonnes options"""
    # Configuration Chrome optimisée pour l'automatisation
```

### 📋 **Fichiers à extraire par ordre d'importance :**

1. **`scraper/search_utils.py`** - Fonction `try_select_region` ✅ **INDISPENSABLE**
2. **`scraper/application_handler.py`** - Fonction `verifier_et_postuler` ✅ **INDISPENSABLE**
3. **`scraper/search_handler.py`** - Logique de recherche
4. **Configuration Chrome** d'`iquesta_scraper.py`

### ❌ **Ce que vous pouvez ignorer :**
- `database/` (sauf si vous voulez la persistance)
- Scripts de test (`add_test_user.py`, etc.)
- `requirements.txt` (vous avez probablement vos propres dépendances)
- `.env`, `.gitignore` (spécifiques au projet)

### 🎯 **Code minimal pour intégration :**

Pour intégrer dans votre code, vous avez besoin de **ces 3 fonctions principales** :

1. `try_select_region()` - Sélection région Île-de-France
2. `verifier_et_postuler()` - Soumission candidature complète  
3. `initialiser_driver()` - Configuration Selenium

Avec ces 3 fonctions, vous avez l'essentiel de l'automatisation qui **fonctionne et a prouvé son efficacité** (3 candidatures réussies) ! 🚀

## ⚠️ Avertissements

- Utiliser de manière responsable et éthique
- Respecter les conditions d'utilisation d'iQuesta
- Ne pas surcharger le serveur avec trop de requêtes simultanées

## 🤝 Contribution

Ce projet est en développement actif. Les améliorations sont les bienvenues !

---
**Dernière mise à jour** : 20 juillet 2025
**Statut** : Automatisation complète ✅ | 3 candidatures réussies 🎉
