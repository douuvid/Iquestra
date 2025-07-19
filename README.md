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

## ⚠️ Avertissements

- Utiliser de manière responsable et éthique
- Respecter les conditions d'utilisation d'iQuesta
- Ne pas surcharger le serveur avec trop de requêtes simultanées

## 🤝 Contribution

Ce projet est en développement actif. Les améliorations sont les bienvenues !

---
**Dernière mise à jour** : 20 juillet 2025
**Statut** : Sélection de région ✅ | Candidatures en cours d'optimisation 🔄
