import os
import sys
import time
import json
import logging
import sqlite3
import argparse
import datetime
import platform
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import string
import random

# Import des fonctions des modules externes
from application_handler import verifier_et_postuler, extraire_details_offre, enregistrer_candidature
from search_handler import rechercher_offres, affiner_recherche_par_contrat, extraire_offres

# --- Configuration ---
# Ajout du chemin racine pour les imports locaux
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
dotenv_path = os.path.join(project_root, '.env')

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv(dotenv_path=dotenv_path, override=True)

URL_ACCUEIL = "https://www.iquesta.com/"

def initialiser_driver():
    """Initialisation du WebDriver avec Chrome."""
    try:
        logger.info("========== ÉTAPE : INITIALISATION DU NAVIGATEUR ==========")
        logger.info("Initialisation du driver Chrome...")
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        logger.info("Driver initialisé.")
        return driver
    except Exception as e:
        logger.critical(f"Erreur Driver: {e}")
        return None

def gerer_cookies(driver):
    """Tente de gérer la bannière de cookies si elle existe."""
    try:
        logger.info("========== ÉTAPE : GESTION DES COOKIES ==========")
        logger.info("Tentative de gestion des cookies...")
        logger.info(f"URL actuelle: {driver.current_url}")
        logger.info(f"Titre de la page: {driver.title}")
        wait = WebDriverWait(driver, 5)
        
        # Essaie plusieurs sélecteurs courants pour les boutons d'acceptation de cookies
        selectors = [
            "#didomi-notice-agree-button",
            ".cookies-accept",
            ".cookie-banner .accept",
            ".cookie-notice .accept"
        ]
        
        for selector in selectors:
            try:
                bouton_cookies = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                bouton_cookies.click()
                logger.info("Cookies acceptés.")
                break
            except:
                pass
    except TimeoutException:
        logger.info("Pas de bannière de cookies détectée.")

# Les fonctions rechercher_offres, affiner_recherche_par_contrat, try_select_region et click_search_button 
# ont été déplacées vers le module search_handler.py

def recuperer_liens_offres(driver):
    """Récupère tous les liens vers les offres d'emploi sur la page actuelle."""
    try:
        logger.info("========== ÉTAPE : RÉCUPÉRATION DES LIENS D'OFFRES ==========")
        logger.info(f"URL actuelle: {driver.current_url}")
        logger.info(f"Titre de la page: {driver.title}")
        
        # Attendre que la liste des offres soit chargée
        wait = WebDriverWait(driver, 10)
        try:
            selectors = [".job-list", ".offers-list", ".list-offers", ".search-results"]
            found = False
            for selector in selectors:
                try:
                    logger.info(f"Essai du sélecteur pour liste d'offres: {selector}")
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.info(f"Liste d'offres trouvée avec: {selector}")
                    found = True
                    break
                except:
                    pass
                    
            if not found:
                logger.warning("La liste d'offres n'est pas chargée avec les sélecteurs attendus.")
        except:
            logger.warning("La liste d'offres n'est pas chargée avec les sélecteurs attendus.")
            # On continue quand même
        
        # Récupérer les liens vers les offres
        liens_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.fw-bold")))
        liens = [elem.get_attribute('href') for elem in liens_elements]
        logger.info(f"DEBUG: {len(liens)} liens d'offres trouvés sur la page.")
        logger.info(f"{len(liens)} offres trouvées sur la page.")
        return liens
    except TimeoutException:
        logger.warning("Aucune offre trouvée sur la page de résultats.")
        return []

def collect_offer_details(driver, url):
    """Collecte les détails d'une offre depuis la page de l'offre."""
    logger.info("========== ÉTAPE : COLLECTE DES DÉTAILS D'OFFRE ==========")
    logger.info(f"URL de l'offre: {url}")
    logger.info(f"Titre de la page: {driver.title}")
    
    # Délégation à la fonction dans le module application_handler
    details = extraire_details_offre(driver)
    logger.info(f"Détails extraits: Titre='{details.get('Titre')}', Entreprise='{details.get('Entreprise')}', Lieu='{details.get('Lieu')}'")
    return details
    
    return details

# Cette fonction a été déplacée vers application_handler.py

def main():
    """Fonction principale pour orchestrer le scraping et enregistrer les données."""
    logger.info("========== DÉMARRAGE DU PROGRAMME ==========")
    logger.info(f"Date et heure de lancement: {datetime.datetime.now()}")
    logger.info(f"Système: {platform.system()} {platform.release()}")
    
    parser = argparse.ArgumentParser(description="Scraper iQuesta pour postuler aux offres d'emploi.")
    parser.add_argument('--email', type=str, help="L'email de l'utilisateur pour lequel lancer le scraper. Surcharge la variable d'environnement USER_EMAIL.")
    args = parser.parse_args()

    user_email_to_use = args.email if args.email else os.getenv("USER_EMAIL")
    logger.info(f"Email utilisateur spécifié: {user_email_to_use}")

    if not user_email_to_use:
        logger.critical("ERREUR: Email utilisateur non spécifié. Utilisez l'option --email ou définissez USER_EMAIL dans .env.")
        sys.exit(1)

    logger.info("========== LANCEMENT DU SCRAPER IQUESTA ==========")
    
    # Accès SQLite direct - Chemin de la base de données
    db_path = os.path.join(project_root, 'database', 'users.db')
    logger.info(f"Connexion à la base de données: {db_path}")
    
    # Récupération directe de l'utilisateur avec SQLite
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE email = ?', (user_email_to_use,))
        user_row = cursor.fetchone()
        
        if not user_row:
            logger.critical(f"Utilisateur '{user_email_to_use}' non trouvé dans la base de données. Arrêt.")
            conn.close()
            return
            
        # Convertir en dictionnaire
        user_data = dict(user_row)
        logger.info(f"Utilisateur '{user_data['first_name']}' (ID: {user_data['id']}) trouvé.")
    except Exception as e:
        logger.critical(f"Erreur lors de la récupération de l'utilisateur: {e}")
        if 'conn' in locals():
            conn.close()
        return

    logger.info("DEBUG: Données utilisateur récupérées de la base de données :")
    logger.info(json.dumps(user_data, indent=2, default=str))

    user_id = user_data['id']
    logger.info(f"Utilisateur '{user_data['first_name']}' (ID: {user_id}) trouvé.")

    if not os.path.exists(user_data['cv_path']) or not os.path.exists(user_data['lm_path']):
        logger.critical('Fichier CV ou LM introuvable. Vérifiez les chemins dans la base de données.')
        db.close()
        return
    logger.info("Chemins des fichiers CV et LM validés.")

    search_query = user_data.get('search_query')
    location = user_data.get('location')
    contract_type = user_data.get('contract_type')
    if not search_query or not location:
        logger.critical("--- ACTION REQUISE ---")
        logger.critical("Le 'poste recherché' (search_query) ou le 'lieu' (location) ne sont pas définis pour cet utilisateur.")
        logger.critical("Le scraper ne peut pas lancer de recherche. Veuillez mettre à jour le profil de l'utilisateur.")
        logger.critical("Arrêt du scraper.")
        db.close()
        return
    logger.info(f"Préférences : Poste='{search_query}', Lieu='{location}', Contrat='{contract_type or 'Tous'}'")

    driver = initialiser_driver()
    if not driver:
        db.close()
        return

    sent_applications_count = 0
    try:
        driver.get(URL_ACCUEIL)
        gerer_cookies(driver)
        
        if rechercher_offres(driver, metier=search_query, region_text=location):
            if contract_type:
                affiner_recherche_par_contrat(driver, contract_type)

            liens_offres = recuperer_liens_offres(driver)
            if not liens_offres:
                logger.info("Aucune offre à traiter. Fin.")
                conn.close()
                return

            for i, lien in enumerate(liens_offres):
                logger.info(f"--- Traitement de l'offre {i+1}/{len(liens_offres)} ---")
                driver.get(lien)
                
                offer_details = collect_offer_details(driver, lien)
                
                # Vérifier si déjà postulé
                cursor.execute('SELECT COUNT(*) FROM applications WHERE user_id = ? AND job_url = ?', 
                              (user_data['id'], lien))
                already_applied = cursor.fetchone()[0] > 0
                
                if already_applied:
                    logger.info("Déjà postulé (vérifié dans la DB).")
                    offer_details['Statut'] = 'Déjà postulé'
                else:
                    if verifier_et_postuler(driver, user_data):
                        logger.info("Candidature envoyée avec succès. Enregistrement dans la base de données...")
                        offer_details['Statut'] = 'Candidature envoyée'
                        sent_applications_count += 1
                    else:
                        offer_details['Statut'] = 'Échec candidature'
                
                # Enregistrer la candidature
                # Utilise la fonction du module application_handler pour enregistrer la candidature
                if not enregistrer_candidature(conn, cursor, user_data, offer_details):
                    logger.warning("Échec de l'enregistrement de la candidature en base de données.")


    finally:
        logger.info("\n--- Résumé de la session ---")
        logger.info(f"Nombre total de candidatures envoyées : {sent_applications_count}")
        if 'driver' in locals() and driver:
            logger.info("Fermeture du navigateur.")
            driver.quit()
        if 'conn' in locals() and conn:
            conn.close()
            logger.info("Connexion à la base de données fermée.")
        logger.info("--- Scraper iQuesta terminé ---")

if __name__ == "__main__":
    main()
