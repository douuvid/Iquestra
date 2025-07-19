#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException
)

# Configuration du logging
logger = logging.getLogger(__name__)

# Variables et constantes
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def try_select_region(driver, region_target):
    """
    Tente de sélectionner la région spécifiée dans la liste déroulante.
    Fonction revue pour correspondre exactement au workflow manuel de l'utilisateur.
    
    Returns:
        bool: True si la sélection a réussi, False sinon
    """
    logger.info("========== RECHERCHE : SÉLECTION DE RÉGION ==========")
    logger.info(f"🌍 Tentative de sélection de la région: {region_target}")
    
    # Attendre que tous les éléments de la page soient bien chargés
    logger.info("Attente pour chargement complet de la page")
    time.sleep(5)  # Augmenté à 5 secondes
    
    # ÉTAPE 1: Vérifier si nous sommes sur la page de résultats avec le formulaire #offerFormSearch
    try:
        # Tenter de trouver le formulaire de résultats
        results_form = driver.find_elements(By.ID, "offerFormSearch")
        
        if results_form:
            logger.info("✓ Détecté le formulaire de résultats (#offerFormSearch)")
            
            # Tenter de trouver le sélecteur de région dans ce formulaire
            try:
                select_region_target = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#offerFormSearch #selectRegion"))
                )
                
                # Cliquer pour ouvrir la liste déroulante
                logger.info("Clic sur le select du formulaire de résultats")
                select_region_target.click()
                time.sleep(2)
                
                # Sélectionner Ile de France par sa value=10
                select_obj = Select(select_region_target)
                try:
                    select_obj.select_by_value("10")
                    time.sleep(1)
                    
                    # Vérification
                    selected_option = select_obj.first_selected_option
                    logger.info(f"Option sélectionnée dans le formulaire de résultats: '{selected_option.text}' (value='{selected_option.get_attribute('value')}')")
                    
                    if selected_option.get_attribute('value') == "10":
                        logger.info("✓ Région 'Ile de France' sélectionnée avec succès dans le formulaire de résultats")
                        return True
                    
                    # Si la sélection n'a pas fonctionné, essayer par JavaScript
                    logger.info("La sélection classique a échoué, tentative par JavaScript")
                    driver.execute_script("""
                        var select = document.querySelector('#offerFormSearch #selectRegion');
                        if (select) {
                            select.value = '10';
                            select.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    """)
                    time.sleep(1)
                    
                    # Vérifier à nouveau
                    selected_option = select_obj.first_selected_option
                    if selected_option.get_attribute('value') == "10":
                        logger.info("✓ Région sélectionnée via JavaScript dans le formulaire de résultats")
                        return True
                        
                except Exception as e:
                    logger.error(f"Erreur lors de la sélection de la région dans le formulaire de résultats: {e}")
            except Exception as e:
                logger.error(f"Erreur lors de l'accès au sélecteur dans le formulaire de résultats: {e}")
    except Exception as e:
        logger.info(f"Le formulaire de résultats n'a pas été trouvé: {e}")
    
    # ÉTAPE 2: Si nous n'avons pas réussi ou si nous ne sommes pas sur la page de résultats,
    # essayer avec le formulaire principal
    
    logger.info("Tentative avec le formulaire principal")
    
    # MÉTHODE 1: ID direct 'selectRegion' sur la page principale
    try:
        logger.info("Recherche par ID 'selectRegion' sur la page principale")
        select_region_target = driver.find_element(By.ID, "selectRegion")
        
        if select_region_target:
            logger.info("✓ Trouvé <select id='selectRegion'>")
            
            # Cliquer sur le select pour ouvrir la liste déroulante
            logger.info("Clic sur le select pour ouvrir la liste")
            select_region_target.click()
            time.sleep(2)
            
            # Créer un objet Select et tenter de sélectionner 'Ile de France' par value
            logger.info("Tentative de sélection par value='10' (Ile de France)")
            select_obj = Select(select_region_target)
            
            try:
                select_obj.select_by_value("10")  # 10 = Ile de France
                time.sleep(1)
                
                # Vérification
                selected_option = select_obj.first_selected_option
                logger.info(f"Option sélectionnée: '{selected_option.text}' (value='{selected_option.get_attribute('value')}')")
                
                if selected_option.get_attribute('value') == "10":
                    logger.info("✓ Région 'Ile de France' sélectionnée avec succès")
                    return True
                
                # Si la sélection n'a pas fonctionné, essayer par JavaScript
                logger.info("La sélection classique a échoué, tentative par JavaScript")
                driver.execute_script("""
                    var regionSelect = document.getElementById('selectRegion');
                    if (regionSelect) {
                        regionSelect.value = '10';
                        regionSelect.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                """)
                time.sleep(1)
                
                # Vérifier à nouveau
                selected_option = select_obj.first_selected_option
                if selected_option.get_attribute('value') == "10":
                    logger.info("✓ Région sélectionnée via JavaScript")
                    return True
            except Exception as e:
                logger.error(f"Erreur lors de la sélection de la région: {e}")
    except Exception as e:
        logger.error(f"Erreur lors de l'accès au sélecteur principal: {e}")
    
    # Si toutes les méthodes ont échoué
    logger.error("⛔ Impossible de sélectionner la région 'Ile de France'")
    return False

def click_search_button(driver, form_element=None):
    """Tente de cliquer sur le bouton de recherche."""
    try:
        # Essayer différents sélecteurs pour le bouton
        bouton_selectors = [
            "button[type='submit'][class*='btn-primary']",
            "button[type='submit']",
            "input[type='submit']",
            "button.btn-primary",
            "a.btn-primary[href*='job']"
        ]
        
        bouton_recherche = None
        for selector in bouton_selectors:
            try:
                # Si un formulaire est fourni, chercher dedans
                if form_element:
                    buttons = form_element.find_elements(By.CSS_SELECTOR, selector)
                else:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                if buttons:
                    logger.info(f"Trouvé {len(buttons)} boutons avec le sélecteur '{selector}'")
                    for idx, button in enumerate(buttons):
                        text = button.text.strip() if button.text else 'sans texte'
                        logger.info(f"  - Bouton {idx+1}: texte='{text}'")
                        
                        if not bouton_recherche:
                            bouton_recherche = button
                            logger.info(f"    ✓ Premier bouton sélectionné: '{text}'")
                    break
            except Exception as e:
                logger.error(f"Erreur avec le sélecteur de bouton '{selector}': {e}")
        
        if bouton_recherche:
            try:
                # Faire défiler jusqu'au bouton pour s'assurer qu'il est visible
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bouton_recherche)
                logger.info("Attente de 3 secondes après scroll vers le bouton")
                time.sleep(3)
                
                # Cliquer sur le bouton
                try:
                    logger.info("Tentative de clic normal")
                    bouton_recherche.click()
                    logger.info("Bouton de recherche cliqué")
                    return True
                except Exception as e:
                    logger.info(f"Erreur lors du clic normal: {e}")
                    # Essayer via ActionChains
                    try:
                        logger.info("Tentative de clic via ActionChains")
                        from selenium.webdriver.common.action_chains import ActionChains
                        actions = ActionChains(driver)
                        actions.move_to_element(bouton_recherche).pause(1).click().perform()
                        logger.info("Bouton de recherche cliqué via ActionChains")
                        time.sleep(2)
                        return True
                    except Exception as action_error:
                        logger.info(f"Erreur lors du clic via ActionChains: {action_error}")
                        # Continuer avec le fallback JavaScript
            except Exception as click_error:
                logger.error(f"Erreur lors du clic sur le bouton de recherche: {click_error}")
                
                # Essayer via JavaScript
                try:
                    driver.execute_script("arguments[0].click();", bouton_recherche)
                    logger.info("Bouton de recherche cliqué via JavaScript")
                    return True
                except Exception as js_error:
                    logger.error(f"Erreur JavaScript pour cliquer sur le bouton: {js_error}")
        else:
            logger.error("Bouton de recherche non trouvé")
            
            # Si on a un formulaire, essayer de le soumettre directement
            if form_element:
                try:
                    driver.execute_script("arguments[0].submit();", form_element)
                    logger.info("Formulaire soumis via JavaScript")
                    return True
                except Exception as submit_error:
                    logger.error(f"Erreur lors de la soumission du formulaire: {submit_error}")
                    
                    # Dernier recours : simuler appui sur touche Entrée
                    try:
                        active_element = driver.switch_to.active_element
                        active_element.send_keys(Keys.RETURN)
                        logger.info("Touche Entrée envoyée pour soumettre le formulaire")
                        return True
                    except Exception as keys_error:
                        logger.error(f"Erreur lors de l'envoi de la touche Entrée: {keys_error}")
    except Exception as e:
        logger.error(f"Erreur générale lors de la recherche du bouton: {e}")
    
    return False

def extraire_offres(driver):
    """Extrait les offres d'emploi de la page de résultats."""
    logger.info("Extraction des offres d'emploi...")
    offres = []
    
    try:
        # Attendre que les offres se chargent
        wait = WebDriverWait(driver, 10)
        
        # Essayer différents sélecteurs pour les cartes d'offres
        offre_selectors = [
            "div.job-card",
            "div.card",
            "div.job-offer",
            "div.job-listing",
            "div.job",
            "div[class*='job']",
            "article",
            "div.row a[href*='/job/']",
            "a[href*='/job/']"
        ]
        
        offre_elements = []
        for selector in offre_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logger.info(f"Trouvé {len(elements)} offres avec le sélecteur '{selector}'")
                    offre_elements = elements
                    break
            except Exception as e:
                logger.error(f"Erreur avec le sélecteur '{selector}': {e}")
        
        if not offre_elements:
            logger.error("Aucune offre trouvée avec les sélecteurs courants")
            
            # Essayer de trouver des liens qui pourraient être des offres
            try:
                links = driver.find_elements(By.TAG_NAME, "a")
                job_links = [link for link in links if '/job/' in (link.get_attribute('href') or '')]
                if job_links:
                    logger.info(f"Trouvé {len(job_links)} liens d'offres via recherche d'URL")
                    offre_elements = job_links
            except Exception as link_error:
                logger.error(f"Erreur lors de la recherche de liens d'offres: {link_error}")
        
        # Traitement des offres trouvées
        for idx, offre in enumerate(offre_elements):
            try:
                info_offre = {}
                
                # Essayer d'extraire l'URL
                try:
                    # Si l'élément est directement un lien
                    href = offre.get_attribute('href')
                    if not href:
                        # Chercher un lien à l'intérieur
                        links = offre.find_elements(By.TAG_NAME, "a")
                        for link in links:
                            link_href = link.get_attribute('href')
                            if link_href and '/job/' in link_href:
                                href = link_href
                                break
                    
                    info_offre['url'] = href
                except Exception as url_error:
                    logger.error(f"Erreur lors de l'extraction de l'URL pour l'offre {idx+1}: {url_error}")
                
                # Essayer d'extraire le titre
                try:
                    # Chercher dans différents éléments
                    title_elements = offre.find_elements(By.CSS_SELECTOR, "h2, h3, h4, .title, .job-title")
                    if title_elements:
                        info_offre['titre'] = title_elements[0].text.strip()
                    else:
                        # Si pas d'élément titre spécifique, utiliser le texte de l'offre
                        info_offre['titre'] = (offre.text[:50] + '...') if len(offre.text) > 50 else offre.text
                except Exception as title_error:
                    logger.error(f"Erreur lors de l'extraction du titre pour l'offre {idx+1}: {title_error}")
                    info_offre['titre'] = f"Offre {idx+1}"
                
                # Essayer d'extraire l'entreprise
                try:
                    company_elements = offre.find_elements(By.CSS_SELECTOR, ".company, .company-name, .employer")
                    if company_elements:
                        info_offre['entreprise'] = company_elements[0].text.strip()
                except Exception:
                    info_offre['entreprise'] = "Non spécifié"
                
                # Essayer d'extraire la localisation
                try:
                    location_elements = offre.find_elements(By.CSS_SELECTOR, ".location, .job-location, .city")
                    if location_elements:
                        info_offre['lieu'] = location_elements[0].text.strip()
                except Exception:
                    info_offre['lieu'] = "Non spécifié"
                
                # Ajouter l'offre à la liste si elle a au moins une URL
                if 'url' in info_offre and info_offre['url']:
                    offres.append(info_offre)
                    logger.info(f"Offre {idx+1} extraite: {info_offre.get('titre', 'Sans titre')} - {info_offre.get('entreprise', 'Entreprise inconnue')}")
            
            except Exception as offre_error:
                logger.error(f"Erreur lors du traitement de l'offre {idx+1}: {offre_error}")
        
        logger.info(f"Total: {len(offres)} offres extraites")
        return offres
    
    except Exception as e:
        logger.error(f"Erreur générale lors de l'extraction des offres: {e}")
        return []
