#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from dotenv import load_dotenv
import random
import string

# Ajout du chemin racine pour les imports locaux
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
dotenv_path = os.path.join(project_root, '.env')

# Chargement des variables d'environnement
load_dotenv(dotenv_path=dotenv_path, override=True)

# Import après avoir configuré les chemins
from database.user_database import UserDatabase

# Génération d'un email aléatoire pour avoir un nouvel ID utilisateur
def generate_random_email():
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for i in range(8))
    return f"{random_string}@testmail.com"

# Création d'un utilisateur de test avec un nouvel ID
db = UserDatabase()

email = generate_random_email()
first_name = "Test"
last_name = "Nouveau"
cv_path = os.path.join(project_root, "cv_files", "potatoes.pdf")
lm_path = os.path.join(project_root, "cv_files", "potatoes.pdf")
search_query = "Développeur Web"
location = "Ile de France"  # Utilisation du format exact vu dans la liste déroulante
contract_type = "CDI"

# Créer un nouvel utilisateur
user_id = db.create_user(
    email, 
    first_name, 
    last_name, 
    cv_path, 
    lm_path, 
    search_query, 
    location,
    contract_type
)

print(f"Nouvel utilisateur créé:")
print(f"- ID: {user_id}")
print(f"- Email: {email}")
print(f"- Nom: {first_name} {last_name}")
print(f"- Recherche: {search_query} à {location}")
print(f"- Contrat: {contract_type}")
print("\nVous pouvez lancer le scraper avec cette commande:")
print(f"python scraper/iquesta_scraper.py --email {email}")

# Fermer la connexion à la base de données
db.close()
