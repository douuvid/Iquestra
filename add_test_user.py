#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
from dotenv import load_dotenv
import random
import string
import time

# Ajout du chemin racine pour les imports locaux
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
dotenv_path = os.path.join(project_root, '.env')

# Chargement des variables d'environnement
load_dotenv(dotenv_path=dotenv_path, override=True)

# Nouvel utilisateur Kim Alya pour tester le double clic
email = "keviv22161@modirosa.com"

# Connexion directe à la base de données
db_path = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'database', 'users.db'))
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
first_name = "Kim"
last_name = "Alya"
cv_path = os.path.join(project_root, "cv_files", "potatoes.pdf")
lm_path = os.path.join(project_root, "cv_files", "potatoes.pdf")
search_query = "Développeur Web"
location = "Ile de France"  # Format exact comme dans la liste déroulante
contract_type = "CDI"
timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

# Insertion directe dans la base de données
try:
    cursor.execute('''
    INSERT INTO users (email, first_name, last_name, cv_path, lm_path, search_query, location, contract_type, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (email, first_name, last_name, cv_path, lm_path, search_query, location, contract_type, timestamp))
    conn.commit()
    user_id = cursor.lastrowid
    
    print(f"Nouvel utilisateur créé:")
    print(f"- ID: {user_id}")
    print(f"- Email: {email}")
    print(f"- Nom: {first_name} {last_name}")
    print(f"- Recherche: {search_query} à {location}")
    print(f"- Contrat: {contract_type}")
    print("\nVous pouvez lancer le scraper avec cette commande:")
    print(f"python scraper/iquesta_scraper.py --email {email}")
    
except sqlite3.Error as e:
    print(f"Erreur SQLite: {e}")
finally:
    conn.close()
