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

# Import des fonctions utilitaires
from search_utils import try_select_region, click_search_button, extraire_offres

# Configuration du logging
logger = logging.getLogger(__name__)

# Variables et constantes
URL_ACCUEIL = "https://www.iquesta.com/"
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def rechercher_offres(driver, metier=None, region_text=None):
    """Effectue une recherche d'offres sur iQuesta."""
    try:
        logger.info("========== ÉTAPE : RECHERCHE D'OFFRES ==========")
        logger.info(f"URL actuelle: {driver.current_url}")
        logger.info(f"Titre de la page: {driver.title}")
        logger.info(f"Métier recherché: {metier}, Région: {region_text}")
        
        # Attendre un peu pour que la page se charge complètement
        time.sleep(3)
        
        # Capturer une partie du HTML pour le debugging
        logger.info("Aperçu du HTML de la page:")
        html_source = driver.page_source
        html_preview = html_source[:200] if len(html_source) > 200 else html_source
        logger.info(f"{html_preview}...")
        
        # Capture la liste de tous les formulaires sur la page
        try:
            forms = driver.find_elements(By.TAG_NAME, "form")
            logger.info(f"Nombre de formulaires détectés sur la page: {len(forms)}")
            for i, form in enumerate(forms):
                action = form.get_attribute('action') or 'pas d\'action'
                form_id = form.get_attribute('id') or 'pas d\'id'
                form_class = form.get_attribute('class') or 'pas de classe'
                logger.info(f"Formulaire {i+1}: action={action}, id={form_id}, class={form_class}")
                
                # Afficher les champs du formulaire
                inputs = form.find_elements(By.TAG_NAME, "input")
                selects = form.find_elements(By.TAG_NAME, "select")
                logger.info(f"  - Champs: {len(inputs)} inputs, {len(selects)} selects")
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des formulaires: {e}")
            # Continuer même en cas d'erreur
        
        # Attente plus longue pour s'assurer que la page se charge complètement
        wait = WebDriverWait(driver, 30)  # Augmenté à 30 secondes
        
        # Essayer de trouver et remplir le champ de recherche métier/mot-clé
        try:
            # Essayer plusieurs sélecteurs pour le champ de recherche métier
            search_field_selectors = [
                "#controlTerm",
                "input[name='term']", 
                "input[placeholder='Que cherchez-vous ?']", 
                "input[type='search']",
                ".form-control"
            ]
            
            champ_metier = None
            for selector in search_field_selectors:
                try:
                    champs = driver.find_elements(By.CSS_SELECTOR, selector)
                    if champs:
                        logger.info(f"Trouvé {len(champs)} champs avec le sélecteur '{selector}'")
                        for idx, champ in enumerate(champs):
                            placeholder = champ.get_attribute('placeholder') or 'sans placeholder'
                            name = champ.get_attribute('name') or 'sans nom'
                            logger.info(f"  - Champ {idx+1}: placeholder='{placeholder}', name='{name}'")
                            
                            # Sélectionner uniquement le champ de recherche avec le bon placeholder ou le bon nom
                            if (placeholder and 'cherchez-vous' in placeholder.lower()) or (name == 'term'):
                                champ_metier = champ
                                logger.info(f"    ✓ Champ de recherche sélectionné: placeholder='{placeholder}', name='{name}'")
                                break
                        if champ_metier:
                            break
                    else:
                        logger.info(f"Aucun champ trouvé avec le sélecteur '{selector}'")
                except Exception as e:
                    logger.error(f"Erreur avec le sélecteur '{selector}': {e}")
            
            if not champ_metier:
                logger.error("Impossible de trouver le champ de recherche métier/mot-clé")
                
                # Tentative alternative avec JavaScript
                logger.warning("Aucun des sélecteurs n'a fonctionné pour le champ de recherche. Tentative via JS.")
                search_input_js = "document.querySelector('input[name=\"term\"]').value = arguments[0];"
                driver.execute_script(search_input_js, metier)
                
                # Simuler l'envoi du formulaire avec la touche Entrée
                active_element = driver.switch_to.active_element
                active_element.send_keys(Keys.RETURN)
                logger.info("Formulaire soumis via JavaScript et touche Entrée")
                time.sleep(5)  # Attendre que la page se charge
                return True
                
            # Si le champ est trouvé, le remplir
            if champ_metier and metier:
                champ_metier.clear()
                champ_metier.send_keys(metier)
                logger.info(f"Champ métier rempli avec: '{metier}'")
                
                # Pause explicite après remplissage du champ métier
                logger.info("Pause de 4 secondes après remplissage du champ métier")
                time.sleep(4)
                
                
                # Sélection de la région (appelée directement sans dépendre du formulaire parent)
                if region_text:
                    logger.info(f"Tentative de sélection de la région: {region_text}")
                    region_selected = try_select_region(driver, region_text)
                    if not region_selected:
                        logger.error(f"ERREUR : La région '{region_text}' n'a pas été sélectionnée. Tentative alternative.")
                        # Deuxième tentative directe sur toute la page
                        try:
                            logger.info("Tentative de trouver un champ région dans toute la page...")
                            all_selects = driver.find_elements(By.TAG_NAME, "select")
                            region_found = False
                            for select_elem in all_selects:
                                try:
                                    select = Select(select_elem)
                                    options = select.options
                                    options_text = [opt.text.strip() for opt in options]
                                    
                                    # Vérifier si ce select contient des options qui ressemblent à des régions
                                    logger.info(f"Options trouvées: {options_text}")
                                    
                                    # Si ce select contient l'option Île-de-France, la sélectionner
                                    for i, opt_text in enumerate(options_text):
                                        if ("ile" in opt_text.lower() and "france" in opt_text.lower()) or \
                                           ("île" in opt_text.lower() and "france" in opt_text.lower()):
                                            select.select_by_index(i)
                                            logger.info(f"Région '{opt_text}' sélectionnée via recherche globale")
                                            region_found = True
                                            break
                                    if region_found:
                                        break
                                except Exception as select_err:
                                    logger.error(f"Erreur lors de l'analyse d'un select: {select_err}")
                        except Exception as global_err:
                            logger.error(f"Erreur lors de la recherche globale de la région: {global_err}")
                    else:
                        logger.info(f"✅ Région '{region_text}' sélectionnée avec succès")
                
                # Cliquer sur le bouton de recherche
                click_search_button(driver)
                
                time.sleep(5)  # Attendre que les résultats se chargent
                logger.info(f"URL après recherche: {driver.current_url}")
                logger.info("Recherche effectuée avec succès")
                return True
                
            else:
                logger.warning("Champs de recherche incomplets.")
                return False
        except Exception as e:
            logger.error(f"Erreur lors du traitement des champs de recherche: {e}")
            return False
    except Exception as e:
        logger.error(f"Erreur lors de la recherche d'offres: {e}")
        
        # Afficher plus d'informations de debug
        try:
            logger.error("=== DEBUG - STRUCTURE DE LA PAGE ====")
            logger.error(f"URL actuelle: {driver.current_url}")
            logger.error(f"Titre de la page: {driver.title}")
            forms = driver.find_elements(By.TAG_NAME, "form")
            logger.error(f"Nombre de formulaires: {len(forms)}")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            logger.error(f"Nombre d'inputs: {len(inputs)}")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            logger.error(f"Nombre de boutons: {len(buttons)}")
            
            # Prendre une capture d'écran pour analyse
            screenshot_path = os.path.join(project_root, 'debug_screenshot.png')
            driver.save_screenshot(screenshot_path)
            logger.error(f"Capture d'écran sauvegardée: {screenshot_path}")
            
            # Plan B: Utiliser la recherche directe par URL
            logger.info("Tentative de recherche par URL directe")
            query_metier = metier.replace(' ', '+') if metier else ''
            query_region = region_text.replace(' ', '+') if region_text else ''
            direct_url = f"{URL_ACCUEIL}jobs?search_term={query_metier}&regions={query_region}"
            logger.info(f"Navigation directe vers: {direct_url}")
            driver.get(direct_url)
            time.sleep(5)  # Attendre le chargement de la page
            return True
        except Exception as debug_error:
            logger.error(f"Erreur lors du debug: {debug_error}")
            return False

def affiner_recherche_par_contrat(driver, contract_type):
    """Sélectionne le type de contrat pour affiner la recherche."""
    try:
        logger.info(f"========== ÉTAPE : FILTRAGE PAR TYPE DE CONTRAT ({contract_type}) ==========")
        
        # Mapping des types de contrat aux textes affichés sur le site
        contract_map = {
            "CDI": "Emploi",
            "CDD": "Emploi",
            "Alternance": "Contrat en alternance",
            "Stage": "Stage",
            "Emploi": "Emploi"
        }
        target_option_text = contract_map.get(contract_type)
    
        if not target_option_text:
            logger.error(f"Type de contrat non reconnu: {contract_type}")
            return False
        
        # Attendre que les filtres soient chargés
        time.sleep(2)
        
        # Aucun traitement spécifique à la région nécessaire ici
        
        # Chercher les différentes options de filtres
        filter_selectors = [
            "div.form-check",
            ".filter-section",
            "div.filters",
            ".form-group",
            "form"
        ]
        
        filter_container = None
        for selector in filter_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    filter_container = elements[0]
                    logger.info(f"Conteneur de filtres trouvé avec le sélecteur: '{selector}'")
                    break
            except Exception as e:
                logger.debug(f"Erreur avec le sélecteur '{selector}': {e}")
        
        if not filter_container:
            logger.error("Aucun conteneur de filtres trouvé")
            return False
        
        # Trouver et cliquer sur le filtre de type de contrat
        checkboxes = filter_container.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        labels = filter_container.find_elements(By.TAG_NAME, "label")
        
        logger.info(f"Nombre de checkboxes: {len(checkboxes)}, nombre de labels: {len(labels)}")
        
        # Chercher le bon label
        clicked = False
        for label in labels:
            if label.text and target_option_text.lower() in label.text.lower():
                logger.info(f"Label trouvé: '{label.text}'")
                try:
                    label.click()
                    clicked = True
                    logger.info(f"Filtre '{target_option_text}' sélectionné")
                    break
                except Exception as e:
                    logger.error(f"Erreur lors du clic sur le label: {e}")
                    
                    # Essayer de trouver et cliquer sur la checkbox associée
                    try:
                        checkbox_id = label.get_attribute("for")
                        if checkbox_id:
                            checkbox = driver.find_element(By.ID, checkbox_id)
                            checkbox.click()
                            clicked = True
                            logger.info(f"Checkbox pour '{target_option_text}' cliquée via ID")
                            break
                    except Exception as e2:
                        logger.error(f"Impossible de cliquer sur la checkbox via ID: {e2}")
        
        # Si aucun filtre n'a été trouvé/cliqué, essayer via JavaScript
        if not clicked:
            try:
                logger.info("Tentative via JavaScript pour cliquer sur le filtre")
                result = driver.execute_script(f"""
                var labels = document.querySelectorAll('label');
                for (var i = 0; i < labels.length; i++) {{
                    if (labels[i].textContent && labels[i].textContent.toLowerCase().includes('{target_option_text.lower()}')) {{
                        labels[i].click();
                        return true;
                    }}
                }}
                
                // Essayer de trouver les options de select qui contiennent le texte désiré
                var options = document.querySelectorAll('option');
                for (var i = 0; i < options.length; i++) {{
                    if (options[i].textContent && options[i].textContent.toLowerCase().includes('{target_option_text.lower()}')) {{
                        const select = options[i].closest('select');
                        if (select) {{
                            select.value = options[i].value;
                            const event = new Event('change', {{ bubbles: true }});
                            select.dispatchEvent(event);
                            return true;
                        }}
                    }}
                }}
                return false;
                """)
                
                if result:
                    logger.info("Filtre sélectionné via JavaScript")
                    clicked = True
                else:
                    logger.error("Filtre non trouvé même via JavaScript")
            except Exception as js_error:
                logger.error(f"Erreur JavaScript pour le filtre: {js_error}")
        
        # Attendre que les résultats se rechargent après le filtre
        if clicked:
            time.sleep(5)
            logger.info("Filtrage par type de contrat terminé")
            return True
        else:
            logger.error(f"Impossible de filtrer par le type de contrat: {contract_type}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de l'affinage par type de contrat: {e}")
        return False

# Cette fonction a été déplacée vers search_utils.py

# Cette fonction a été déplacée vers search_utils.py

# Cette fonction a été déplacée vers search_utils.py
