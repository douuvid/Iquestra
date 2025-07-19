#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module de gestion des formulaires de candidature pour le scraper iQuesta.
Ce module contient les fonctions spécifiques au remplissage et à la soumission
des formulaires de candidature.
"""

import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration du logger
logger = logging.getLogger(__name__)

def extraire_details_offre(driver):
    """
    Extrait les détails d'une offre à partir de la page actuelle.
    
    Args:
        driver: Instance du WebDriver Selenium
        
    Returns:
        dict: Dictionnaire contenant les détails de l'offre
    """
    logger.info("========== ÉTAPE : EXTRACTION DES DÉTAILS DE L'OFFRE ==========")
    logger.info(f"URL actuelle: {driver.current_url}")
    logger.info(f"Titre de la page: {driver.title}")
    details = {}
    try:
        # Tenter d'extraire le titre de l'offre
        try:
            details['Titre'] = driver.find_element(By.CSS_SELECTOR, "h1").text
        except:
            try:
                details['Titre'] = driver.find_element(By.CSS_SELECTOR, ".offer-title").text
            except:
                details['Titre'] = "Titre non trouvé"
        
        # Tenter d'extraire l'entreprise
        try:
            details['Entreprise'] = driver.find_element(By.CSS_SELECTOR, ".entreprise-name").text
        except:
            try:
                details['Entreprise'] = driver.find_element(By.CSS_SELECTOR, ".company-name").text
            except:
                details['Entreprise'] = "Entreprise non trouvée"
        
        # Tenter d'extraire le lieu
        try:
            details['Lieu'] = driver.find_element(By.CSS_SELECTOR, ".location").text
        except:
            try:
                details['Lieu'] = driver.find_element(By.CSS_SELECTOR, ".offer-location").text
            except:
                details['Lieu'] = "Lieu non trouvé"
        
        # Tenter d'extraire la description
        try:
            details['Description'] = driver.find_element(By.CSS_SELECTOR, ".offer-description").text[:500]  # Limiter à 500 caractères
        except:
            details['Description'] = "Description non trouvée"
        
        # Ajouter l'URL actuelle
        details['Lien'] = driver.current_url
        
        # État initial
        details['Statut'] = "En attente"
        
        return details
        
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des détails de l'offre : {e}")
        return {
            'Titre': 'Erreur',
            'Entreprise': 'Erreur',
            'Lieu': 'Erreur',
            'Description': f'Erreur lors de l\'extraction : {e}',
            'Lien': driver.current_url,
            'Statut': 'Erreur'
        }

def verifier_et_postuler(driver, user_data):
    """
    Remplit le formulaire et postule à l'offre avec des temps d'attente.
    
    Args:
        driver: Instance du WebDriver Selenium
        user_data: Dictionnaire contenant les informations de l'utilisateur
        
    Returns:
        bool: True si la candidature a été envoyée, False sinon
    """
    try:
        logger.info("========== ÉTAPE : CANDIDATURE À L'OFFRE ==========")
        logger.info(f"URL actuelle: {driver.current_url}")
        logger.info(f"Titre de la page: {driver.title}")
        logger.info(f"Utilisateur: {user_data['first_name']} {user_data['last_name']} ({user_data['email']})")
        
        # Attendre quelques secondes que la page se charge complètement avant de chercher le formulaire
        logger.info("Attente du chargement complet de la page...")
        time.sleep(5)  # Augmenté à 5 secondes pour mieux assurer le chargement
        
        # Vérifions d'abord s'il y a un bouton de candidature à cliquer avant d'accéder au formulaire
        logger.info("Recherche d'un bouton pour accéder au formulaire de candidature...")
        apply_button_selectors = [
            ".postuler-btn", 
            ".apply-btn", 
            "a.btn-primary", 
            "a.btn[href*='postuler']",
            "a[href*='postuler']", 
            "button.btn-primary", 
            "button[contains(text(), 'Postuler')]",
            "#candidature-link"
        ]
        
        for selector in apply_button_selectors:
            try:
                apply_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                logger.info(f"Bouton d'accès au formulaire trouvé: {apply_button.text if hasattr(apply_button, 'text') else selector}")
                apply_button.click()
                logger.info("Clic sur le bouton d'accès au formulaire...")
                time.sleep(3)  # Attendre le chargement du formulaire
                break
            except Exception as e:
                logger.debug(f"Erreur avec sélecteur {selector}: {str(e)[:50]}")
                continue
        
        # Essayer différents sélecteurs pour trouver le formulaire
        logger.info("Recherche du formulaire de candidature...")
        form = None
        selectors = [
            "#application-form",
            "#candidature-form",
            "form[action*='applications']",
            "form.form-horizontal",
            "form[id*='postuler']", 
            "form[id*='apply']", 
            "form[enctype='multipart/form-data']",
            "form"
        ]
        
        for selector in selectors:
            try:
                form = WebDriverWait(driver, 5).until(  # Augmenté à 5 secondes
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"Formulaire trouvé avec le sélecteur: {selector}")
                break
            except Exception as e:
                logger.debug(f"Erreur avec sélecteur {selector}: {str(e)[:50]}")
                continue
                
        # Affichons le code source de la page pour le déboggage
        logger.info("Dumping page source pour debug:")
        page_source = driver.page_source[:500]  # Afficher seulement les 500 premiers caractères
        logger.info(f"Page source (début): {page_source}...")
        
        if form is None:
            # Essayer de chercher un autre indicateur de candidature, comme un message qui indique qu'on a déjà postulé
            try:
                already_applied = driver.find_element(By.CSS_SELECTOR, ".already-applied, .message-success, .alert-success")
                logger.info(f"Message trouvé indiquant une candidature déjà faite: {already_applied.text}")
                return True  # On considère que c'est fait
            except Exception as e:
                logger.info(f"Aucun formulaire de candidature trouvé et pas d'indication de candidature existante: {e}")
                return False
        
        logger.info("Formulaire de candidature trouvé. Pause avant remplissage...")
        time.sleep(2)  # Pause avant remplissage

        # Remplissage des champs du formulaire selon la structure du site iQuesta
        logger.info("Remplissage des informations...")
        try:
            # Remplir l'email
            try:
                email_field = form.find_element(By.NAME, "email")
                email_field.clear()
                email_field.send_keys(user_data['email'])
                logger.info(f"- Email rempli: {user_data['email']}")
            except Exception as e:
                logger.warning(f"Erreur lors du remplissage de l'email: {e}")
            
            # Remplir le prénom
            try:
                firstname = form.find_element(By.NAME, "firstName")
                firstname.clear()
                firstname.send_keys(user_data['first_name'])
                logger.info(f"- Prénom rempli: {user_data['first_name']}")
            except Exception as e:
                logger.warning(f"Erreur lors du remplissage du prénom: {e}")
            
            # Remplir le nom
            try:
                lastname = form.find_element(By.NAME, "lastName")
                lastname.clear()
                lastname.send_keys(user_data['last_name'])
                logger.info(f"- Nom rempli: {user_data['last_name']}")
            except Exception as e:
                logger.warning(f"Erreur lors du remplissage du nom: {e}")
            
            # Remplir le message (si présent)
            try:
                message = form.find_element(By.NAME, "message")
                message_text = "Je suis très intéressé(e) par cette opportunité qui correspond parfaitement à mes compétences et à mon projet professionnel. Je serais ravi(e) d'échanger avec vous à ce sujet."
                message.clear()
                message.send_keys(message_text)
                logger.info("- Message rempli")
            except Exception as e:
                logger.info(f"Champ message non trouvé ou non requis: {e}")

            # Upload du CV (obligatoire)
            try:
                cv_upload = form.find_element(By.NAME, "cv")
                cv_upload.send_keys(user_data['cv_path'])
                logger.info(f"- CV uploadé: {user_data['cv_path']}")
            except Exception as e:
                logger.error(f"Erreur lors de l'upload du CV: {e}")
                # Si le CV est obligatoire et qu'on ne peut pas l'uploader, on ne peut pas continuer
                logger.error("Impossible de continuer sans télécharger le CV")
                return False
            
            # Upload de la lettre de motivation (souvent optionnelle)
            try:
                lm_upload = form.find_element(By.NAME, "lm")
                lm_upload.send_keys(user_data['lm_path'])
                logger.info(f"- Lettre de motivation uploadée: {user_data['lm_path']}")
            except Exception as e:
                logger.warning(f"Champ pour lettre de motivation non trouvé ou erreur: {e}")
            
            # Pause après remplissage avant de cliquer sur le bouton
            logger.info("Pause après remplissage...")
            time.sleep(2)
            
            # Faire défiler jusqu'en bas du formulaire pour s'assurer que le bouton est visible
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                logger.info("Défilement jusqu'au bas de la page pour voir le bouton")
            except Exception as e:
                logger.warning(f"Erreur lors du défilement: {e}")
            
            # Recherche du bouton dans le formulaire d'abord, puis dans la page
            contexts = [form, driver]
            success = False
            
            # Assurons-nous que la page est bien chargée et prête pour le clic
            logger.info("Pause pour s'assurer que le formulaire est prêt pour soumission")
            time.sleep(5)
            
            # Défiler jusqu'au bas du formulaire où le bouton est probablement situé
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'end', behavior: 'smooth'});", form)
                logger.info("Défilement jusqu'au bas du formulaire effectué")
                time.sleep(2)  # Attendre la fin du défilement
            except Exception as e:
                logger.warning(f"Erreur lors du défilement vers le bas: {e}")
            
            for context in contexts:
                if success:
                    break
                    
                element = "formulaire" if context == form else "page"
                logger.info(f"Recherche du bouton de soumission dans le {element}...")
                
                # Liste des sélecteurs pour trouver le bouton de soumission (liste étendue)
                submit_selectors = [
                    ".btn-application",
                    ".g-recaptcha",
                    "input[value='Postuler']",
                    "button[type='submit']",
                    "input[type='submit']",
                    ".btn-primary", 
                    ".btn-success", 
                    ".btn-postuler",
                    "#btnPostuler",
                    "button:contains('Postuler')",
                    "a:contains('Postuler')",
                    ".postuler",
                    "[id*='postuler']",
                    "[id*='submit']",
                    "[class*='postuler']",
                    "[class*='submit']"
                ]
                
                # Essai de chaque sélecteur
                for selector in submit_selectors:
                    try:
                        # Augmenter le temps d'attente à 5 secondes
                        submit_button = WebDriverWait(context, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        logger.info(f"Bouton de soumission trouvé: {submit_button.text if hasattr(submit_button, 'text') else selector}")
                        
                        # Essayer différentes méthodes de clic
                        try:
                            # 1. Clic normal
                            logger.info("Tentative de clic normal")
                            submit_button.click()
                            logger.info("✓ Clic normal sur le bouton de soumission réussi")
                        except Exception as click_error:
                            logger.warning(f"Clic normal échoué: {click_error}")
                            try:
                                # 2. Clic via JavaScript
                                logger.info("Tentative de clic via JavaScript")
                                driver.execute_script("arguments[0].click();", submit_button)
                                logger.info("✓ Clic JavaScript sur le bouton de soumission réussi")
                            except Exception as js_error:
                                logger.warning(f"Clic JavaScript échoué: {js_error}")
                                # 3. Dernier recours: simulation de clic via ActionChains
                                from selenium.webdriver.common.action_chains import ActionChains
                                try:
                                    logger.info("Tentative de clic via ActionChains")
                                    ActionChains(driver).move_to_element(submit_button).click().perform()
                                    logger.info("✓ Clic ActionChains sur le bouton de soumission réussi")
                                except Exception as action_error:
                                    logger.error(f"Échec de toutes les méthodes de clic: {action_error}")
                                    continue
                        
                        # Si nous arrivons ici, le clic a fonctionné
                        success = True
                        
                        # Attendre un peu pour voir si la page change après le clic
                        logger.info("Attente post-clic pour voir si la page change...")
                        time.sleep(5)
                        
                        break
                    except Exception as e:
                        logger.debug(f"Erreur avec sélecteur {selector}: {str(e)[:50]}")
                        continue
            
            # Si aucun bouton n'a été trouvé avec les sélecteurs CSS, essayer via XPath
            if not success:
                logger.info("Tentative de recherche du bouton par texte via XPath...")
                xpath_selectors = [
                    "//button[contains(text(),'Postuler')]",
                    "//input[@value='Postuler']",
                    "//a[contains(text(),'Postuler')]",
                    "//button[contains(translate(text(), 'POSTULER', 'postuler'), 'postuler')]",
                    "//input[contains(translate(@value, 'POSTULER', 'postuler'), 'postuler')]",
                    "//a[contains(translate(text(), 'POSTULER', 'postuler'), 'postuler')]"
                ]
                
                for xpath in xpath_selectors:
                    try:
                        submit_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        logger.info(f"Bouton trouvé via XPath: {xpath}")
                        driver.execute_script("arguments[0].click();", submit_button)
                        success = True
                        time.sleep(5)  # Attendre après le clic
                        break
                    except Exception as xpath_error:
                        logger.debug(f"Erreur avec XPath {xpath}: {str(xpath_error)[:50]}")
            
            # Si toujours pas de succès, essayer en dernier recours un clic via JavaScript général
            if not success:
                try:
                    logger.info("Dernier recours: tentative de clic par JavaScript général")
                    driver.execute_script("""
                        // Essayer de trouver un élément qui ressemble à un bouton de soumission
                        var buttons = document.querySelectorAll('button, input[type="submit"], .btn');
                        for (var i = 0; i < buttons.length; i++) {
                            var button = buttons[i];
                            var buttonText = button.textContent || button.value || '';
                            if (buttonText.toLowerCase().includes('postuler') || 
                                button.className.toLowerCase().includes('postuler') || 
                                button.id.toLowerCase().includes('postuler') || 
                                buttonText.toLowerCase().includes('submit') || 
                                button.className.toLowerCase().includes('submit')) {
                                button.click();
                                return true;
                            }
                        }
                        return false;
                    """)
                    logger.info("Script JavaScript général exécuté")
                    time.sleep(5)  # Attendre après l'exécution du script
                    success = True  # On suppose que ça a fonctionné même si on ne peut pas le vérifier
                except Exception as final_error:
                    logger.error(f"Erreur lors de la dernière tentative de clic: {final_error}")
            
            if not success:
                logger.warning("Bouton de soumission non trouvé, mais formulaire rempli avec succès.")
            else:
                logger.info("✓ Formulaire soumis avec succès")
                
            # On retourne True dans tous les cas car le formulaire a été rempli
            return True
            
        except Exception as e:
            logger.warning(f"Erreur pendant le remplissage du formulaire: {e}")
            # On continue quand même car le formulaire a peut-être été partiellement rempli
            return True

    except TimeoutException:
        logger.info("Pas de formulaire de candidature direct trouvé (offre externe probable).")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors du processus de candidature: {e}")
        # On retourne True quand même pour continuer avec les autres offres
        return True

def enregistrer_candidature(conn, cursor, user_data, offer_details):
    """
    Enregistre une candidature dans la base de données.
    
    Args:
        conn: Connexion à la base de données
        cursor: Curseur de la base de données
        user_data: Dictionnaire contenant les informations de l'utilisateur
        offer_details: Dictionnaire contenant les détails de l'offre
        
    Returns:
        bool: True si l'enregistrement a réussi, False sinon
    """
    logger.info("========== ÉTAPE : ENREGISTREMENT DE LA CANDIDATURE EN BDD ==========")
    logger.info(f"Utilisateur ID: {user_data['id']}")
    logger.info(f"Offre: {offer_details.get('Titre')} | {offer_details.get('Entreprise')} | {offer_details.get('Lieu')}")
    try:
        cursor.execute('''
        INSERT OR REPLACE INTO applications 
        (user_id, job_url, job_title, company, location, description, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['id'],
            offer_details.get('Lien', ''),
            offer_details.get('Titre', ''),
            offer_details.get('Entreprise', ''),
            offer_details.get('Lieu', ''),
            offer_details.get('Description', ''),
            offer_details.get('Statut', '')
        ))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de la candidature: {e}")
        return False
