import os
import json
import sqlite3
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class UserDatabase:
    """Gère les interactions avec la base de données utilisateurs et candidatures."""
    
    def __init__(self, db_path=None):
        """Initialise la connexion à la base de données."""
        logger.info("========== DB : INITIALISATION DE LA CONNEXION ==========")
        if not db_path:
            # Utilise le chemin spécifié dans .env, ou le chemin par défaut
            db_path = os.getenv('DATABASE_PATH', os.path.join(os.path.dirname(__file__), 'users.db'))
            logger.info(f"Chemin de base de données utilisé: {db_path}")
        
        directory = os.path.dirname(db_path)
        if directory and not os.path.exists(directory):
            logger.info(f"Création du répertoire {directory}")
            os.makedirs(directory)
            
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Pour pouvoir accéder aux colonnes par nom
        self.cursor = self.conn.cursor()
        self._create_tables_if_not_exist()
    
    def _create_tables_if_not_exist(self):
        """Crée les tables nécessaires si elles n'existent pas."""
        # Table des utilisateurs
        self.cursor.execute('''
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
        
        # Table des candidatures
        self.cursor.execute('''
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
        
        self.conn.commit()
    
    def create_user(self, email, first_name, last_name, cv_path, lm_path, search_query=None, location=None, contract_type=None):
        """Crée un nouvel utilisateur dans la base de données."""
        try:
            self.cursor.execute('''
            INSERT INTO users (email, first_name, last_name, cv_path, lm_path, search_query, location, contract_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, first_name, last_name, cv_path, lm_path, search_query, location, contract_type))
            self.conn.commit()
            logger.info(f"Utilisateur {email} créé avec succès.")
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            logger.warning(f"L'utilisateur {email} existe déjà.")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
            self.conn.rollback()
            return None
    
    def get_user_by_email(self, email):
        """Récupère les informations d'un utilisateur par son email."""
        logger.info("========== DB : RECHERCHE D'UTILISATEUR ==========")
        logger.info(f"Recherche de l'utilisateur par email: {email}")
        try:
            self.cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = self.cursor.fetchone()
            if user:
                # Convertir le résultat en dictionnaire
                columns = [column[0] for column in self.cursor.description]
                user_dict = {columns[i]: user[i] for i in range(len(columns))}
                logger.info(f"Utilisateur trouvé: ID={user_dict['id']}, {user_dict['first_name']} {user_dict['last_name']}")
                return user_dict
            else:
                logger.warning(f"Aucun utilisateur trouvé avec l'email {email}")
                return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
    
    def update_user(self, user_id, **kwargs):
        """Met à jour les informations d'un utilisateur."""
        if not kwargs:
            logger.warning("Aucune information à mettre à jour.")
            return False
        
        try:
            set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
            values = list(kwargs.values())
            values.append(user_id)
            
            query = f"UPDATE users SET {set_clause} WHERE id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'utilisateur: {e}")
            self.conn.rollback()
            return False
    
    def record_application(self, user_id, offer_details):
        """Enregistre une candidature dans la base de données."""
        logger.info("========== DB : ENREGISTREMENT DE CANDIDATURE ==========")
        logger.info(f"Enregistrement pour utilisateur ID: {user_id}")
        logger.info(f"Détails de l'offre: Titre='{offer_details.get('Titre')}', Entreprise='{offer_details.get('Entreprise')}', Statut='{offer_details.get('Statut')}'")
        try:
            self.cursor.execute('''
            INSERT INTO applications (user_id, job_url, job_title, company, location, description, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                offer_details.get('Lien', ''),
                offer_details.get('Titre', ''),
                offer_details.get('Entreprise', ''),
                offer_details.get('Lieu', ''),
                offer_details.get('Description', ''),
                offer_details.get('Statut', '')
            ))
            self.conn.commit()
            logger.info(f"Candidature enregistrée pour le poste: {offer_details.get('Titre')} chez {offer_details.get('Entreprise')}")
            return True
        except sqlite3.IntegrityError:
            logger.info(f"Cette candidature a déjà été enregistrée (utilisateur {user_id}, URL {offer_details.get('Lien')})")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la candidature: {e}")
            self.conn.rollback()
            return False
    
    def check_if_applied(self, user_id, job_url):
        """Vérifie si un utilisateur a déjà postulé à une offre."""
        logger.info("========== DB : VÉRIFICATION DE CANDIDATURE ==========")
        logger.info(f"Vérification pour utilisateur ID: {user_id}")
        logger.info(f"URL de l'offre: {job_url}")
        try:
            self.cursor.execute('SELECT COUNT(*) FROM applications WHERE user_id = ? AND job_url = ?', 
                               (user_id, job_url))
            count = self.cursor.fetchone()[0]
            result = count > 0
            logger.info(f"Résultat de la vérification: {result} (count={count})")
            return result
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de candidature: {e}")
            return False
    
    def get_user_applications(self, user_id):
        """Récupère toutes les candidatures d'un utilisateur."""
        logger.info("========== DB : LISTE DES CANDIDATURES ==========")
        logger.info(f"Récupération des candidatures pour l'utilisateur ID: {user_id}")
        try:
            self.cursor.execute('''
            SELECT * FROM applications
            WHERE user_id = ?
            ORDER BY applied_at DESC
            ''', (user_id,))
            applications = self.cursor.fetchall()
            result = [dict(app) for app in applications]
            logger.info(f"Nombre de candidatures trouvées: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des candidatures: {e}")
            return []
    
    def close(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.conn.close()
