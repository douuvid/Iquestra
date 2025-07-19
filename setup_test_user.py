import os
import sys
from dotenv import load_dotenv

# Ajout du chemin racine pour les imports locaux
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
dotenv_path = os.path.join(project_root, '.env')

# Chargement des variables d'environnement
load_dotenv(dotenv_path=dotenv_path, override=True)

# Import après avoir configuré les chemins
from database.user_database import UserDatabase

# Création d'un utilisateur de test
db = UserDatabase()

email = "test@example.com"
first_name = "Test"
last_name = "User"
cv_path = os.path.join(project_root, "cv_files", "potatoes.pdf")
lm_path = os.path.join(project_root, "cv_files", "potatoes.pdf")
search_query = "Développeur Web"
location = "Île-de-France"
contract_type = "CDI"

# Vérifier si l'utilisateur existe déjà
existing_user = db.get_user_by_email(email)
if existing_user:
    print(f"L'utilisateur {email} existe déjà avec l'ID: {existing_user['id']}")
else:
    # Créer un nouvel utilisateur
    user_id = db.create_user(
        email=email, 
        first_name=first_name, 
        last_name=last_name, 
        cv_path=cv_path, 
        lm_path=lm_path, 
        search_query=search_query, 
        location=location, 
        contract_type=contract_type
    )
    print(f"Nouvel utilisateur créé avec l'ID: {user_id}")

# Mise à jour du fichier .env pour utiliser cet utilisateur par défaut
with open(dotenv_path, 'r') as f:
    content = f.read()

if "USER_EMAIL=example@email.com" in content:
    content = content.replace("USER_EMAIL=example@email.com", f"USER_EMAIL={email}")
    with open(dotenv_path, 'w') as f:
        f.write(content)
    print(f"Fichier .env mis à jour pour utiliser l'email {email}")

db.close()
print("Configuration terminée.")
