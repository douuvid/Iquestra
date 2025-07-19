import sqlite3
import os

# Créer le répertoire de la base de données s'il n'existe pas
os.makedirs('database', exist_ok=True)

# Connexion à la base de données
conn = sqlite3.connect('database/users.db')
cursor = conn.cursor()

# Créer les tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    cv_path TEXT,
    lm_path TEXT,
    search_query TEXT,
    location TEXT,
    contract_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    job_url TEXT,
    job_title TEXT,
    company TEXT,
    location TEXT,
    description TEXT,
    status TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, job_url)
)
''')

# Insérer l'utilisateur de test
try:
    cv_path = os.path.abspath('cv_files/potatoes.pdf')
    lm_path = os.path.abspath('cv_files/potatoes.pdf')
    
    cursor.execute('''
    INSERT OR REPLACE INTO users (email, first_name, last_name, cv_path, lm_path, search_query, location, contract_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('test@example.com', 'Test', 'User', cv_path, lm_path, 'Développeur Web', 'Île-de-France', 'CDI'))
    
    print("Utilisateur test créé avec succès!")
    print(f"CV path: {cv_path}")
    print(f"LM path: {lm_path}")
except Exception as e:
    print(f"Erreur: {e}")

conn.commit()
conn.close()
