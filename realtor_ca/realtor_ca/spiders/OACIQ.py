import scrapy
from scrapy_selenium import SeleniumRequest
from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
import json
from collections import OrderedDict
import time
import random
from datetime import datetime

class OaciqSpider(scrapy.Spider):
    name = 'oaciq_spider'
    anti_captcha_key = 'fcb53455732f06bfb02d5f27a18813b7'
    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'result.json'
    }
    # Utilisez un ensemble pour garder une trace des URL déjà extraites
    extracted_urls = set()
    delay = random.uniform(10, 20)

    def __init__(self, *args, **kwargs):
        super(OaciqSpider, self).__init__(*args, **kwargs)
        self.load_existing_urls()

    def load_existing_urls(self):
        # Pour le fichier JSON
        try:
            with open('oaciq_result.json', 'r', encoding='utf-8') as json_file:
                existing_data = json.load(json_file)
                for item in existing_data:
                    self.extracted_urls.add(item['URL'])
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def handle_service_unavailable_popup(self, driver):
        try:
            # Vérifiez si le popup est présent
            popup = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Le service est indisponible pour le moment.")]'))
            )
            if popup:
                self.logger.warning("Service is unavailable. Waiting for 5 minutes before retrying.")
                time.sleep(300)  # Attendre 5 minutes
                return True  # Retournez True si le popup est détecté
            
        except TimeoutException:
            return False  # Retournez False si le popup n'est pas détecté

    def start_requests(self):
        yield SeleniumRequest(
            url='https://www.oaciq.com/fr#trouver-courtier',
            wait_time=10,
            callback=self.parse_initial,
            dont_filter=True,
            script='''document.querySelector('input[type="submit"][name="commit"]').click();'''
        )

    def parse_initial(self, response):
        driver = response.meta['driver']
        all_broker_elements = driver.find_elements_by_xpath('//*[@id="find-brokers-result"]/tbody/tr/td[1]/a')
        all_broker_links = [broker.get_attribute('href') for broker in all_broker_elements]#[:1]
        broker_links = [url for url in all_broker_links if url not in self.extracted_urls]

        if broker_links:
            # Si des liens de courtier non extraits sont trouvés, traitez le premier lien
            first_broker = broker_links.pop(0)
            yield SeleniumRequest(
                url=response.urljoin(first_broker),
                wait_time=60,
                callback=self.parse_captcha,
                meta={'handle': 'new', 'remaining_brokers': broker_links, 'retry_times': 3, 'current_broker_url': first_broker}
            )

        else:
            # Ajoutez l'indicateur clicked_next dans les métadonnées
            yield from self.handle_pagination(response, clicked_next=False)

    def handle_pagination(self, response, clicked_next):
        driver = response.meta['driver']
        
        # Si clicked_next est True, retournez sans cliquer à nouveau
        if clicked_next:
            self.logger.info("Already clicked 'Next'. Returning to the initial page.")
            yield SeleniumRequest(
                url='https://www.oaciq.com/fr#trouver-courtier',
                wait_time=10,
                callback=self.parse_initial,
                dont_filter=True,
                script='''document.querySelector('input[type="submit"][name="commit"]').click();'''
            )
            return

        # Vérifiez si le bouton "Suivant" est désactivé
        try:
            next_button_disabled = driver.find_element_by_xpath('//*[@id="find-brokers-result_next" and contains(@class, "disabled")]')
            if next_button_disabled:
                self.logger.info("Next button is disabled. Returning to the initial page.")
                yield SeleniumRequest(
                    url='https://www.oaciq.com/fr#trouver-courtier',
                    wait_time=10,
                    callback=self.parse_initial,
                    dont_filter=True,
                    script='''document.querySelector('input[type="submit"][name="commit"]').click();'''
                )
                return
        except NoSuchElementException:
            pass  # Le bouton "Suivant" n'est pas désactivé, continuez

        # Cliquez sur le bouton "Suivant"
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="find-brokers-result_next"]'))
            )
            next_button.click()
            time.sleep(2)
            
            # Attendez que la nouvelle page soit chargée
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="find-brokers-result"]/tbody/tr/td[1]/a'))
            )
            
            # Récupérez à nouveau les liens des courtiers
            all_broker_elements = driver.find_elements_by_xpath('//*[@id="find-brokers-result"]/tbody/tr/td[1]/a')
            all_broker_links = [broker.get_attribute('href') for broker in all_broker_elements]#[:1]
            broker_links = [url for url in all_broker_links if url not in self.extracted_urls]

            # Si de nouveaux liens sont trouvés, définissez first_broker comme le premier de ces nouveaux liens
            if broker_links:
                first_broker = broker_links.pop(0)
                yield SeleniumRequest(
                    url=response.urljoin(first_broker),
                    wait_time=60,
                    callback=self.parse_captcha,
                    meta={'handle': 'new', 'remaining_brokers': broker_links, 'retry_times': 3, 'current_broker_url': first_broker, 'clicked_next': True}
                )
            else:
                # Si aucun nouveau lien n'est trouvé, vérifiez si le bouton "Suivant" est toujours actif
                try:
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="find-brokers-result_next"]'))
                    )
                    # Si le bouton "Suivant" est actif, appelez à nouveau handle_pagination
                    yield from self.handle_pagination(response, clicked_next=False)
                except TimeoutException:
                    # Si le bouton "Suivant" n'est pas actif, retournez à la page initiale
                    self.logger.info("Next button is not clickable or all brokers on this page have been extracted. Returning to the initial page.")
                    yield SeleniumRequest(
                        url='https://www.oaciq.com/fr#trouver-courtier',
                        wait_time=10,
                        callback=self.parse_initial,
                        dont_filter=True,
                        script='''document.querySelector('input[type="submit"][name="commit"]').click();'''
                    )

        except TimeoutException:
            # Si le bouton "Suivant" n'est pas trouvé ou n'est pas cliquable, retournez à la page initiale
            self.logger.info("Next button is not clickable or all brokers on this page have been extracted. Returning to the initial page.")
            yield SeleniumRequest(
                url='https://www.oaciq.com/fr#trouver-courtier',
                wait_time=10,
                callback=self.parse_initial,
                dont_filter=True,
                script='''document.querySelector('input[type="submit"][name="commit"]').click();'''
            )

    def parse_captcha(self, response):
        driver = response.meta['driver']
        max_retry_attempts = 3
        retry_attempt = 0

        # Gérer le popup "Le service est indisponible pour le moment"
        if self.handle_service_unavailable_popup(driver):
            self.logger.warning("Service unavailable popup detected. Restarting from initial page.")
            yield SeleniumRequest(
                url='https://www.oaciq.com/fr#trouver-courtier',
                wait_time=10,
                callback=self.parse_initial,
                dont_filter=True,
                script='''document.querySelector('input[type="submit"][name="commit"]').click();'''
            )
            return

        while retry_attempt < max_retry_attempts:
            time.sleep(self.delay)
            solver = recaptchaV2Proxyless()
            solver.set_verbose(1)
            solver.set_key(self.anti_captcha_key)
            solver.set_website_url(response.url)
            solver.set_website_key('6LdHiVEUAAAAAJJXlKK1Jvpk5bk9jzzfnYCNdw53')

            g_response = solver.solve_and_return_solution()
            if g_response != 0:
                self.logger.info("Captcha solution: " + g_response)
                try:
                    textarea = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, '//textarea[@id="g-recaptcha-response"]'))
                    )
                    driver.execute_script("arguments[0].style.display = 'block';", textarea)
                    textarea.send_keys(g_response)

                    submit_button = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 'find_broker_show_info_submit_button'))
                    )
                    submit_button.click()
                    time.sleep(2)

                    # Vérifiez la présence du texte d'erreur
                    captcha_error_message = "La vérification de reCAPTCHA a échoué. Veuillez réessayer."
                    error_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, f'//*[contains(text(), "{captcha_error_message}")]'))
                    )
                    if error_element:
                        self.logger.warning("CAPTCHA verification failed. Retrying...")
                        retry_attempt += 1
                        continue  # Continue the while loop to retry CAPTCHA resolution

                except TimeoutException:
                    # Si le texte d'erreur n'est pas détecté, attendez l'élément souhaité
                    try:
                        WebDriverWait(driver, 20).until(
                            EC.presence_of_element_located((By.XPATH, '//div[@class="col-xs-12 col-sm-6 "]'))
                        )
                        break  # CAPTCHA solved successfully
                    except TimeoutException as e:
                        self.logger.error(f"Error during CAPTCHA resolution: {e}")
                        retry_attempt += 1

            else:
                self.logger.error(f"Error occurred during CAPTCHA resolution: {solver.error_code}")
                retry_attempt += 1

        if retry_attempt == max_retry_attempts:
            self.logger.error(f"Failed to solve CAPTCHA after {max_retry_attempts} attempts.")

        # Le reste du code pour extraire les informations après le CAPTCHA réussi peut rester inchangé.
        html_content = driver.page_source
        info_dict = OrderedDict()
        
        # Ajout du titre
        try:
            title_element = driver.find_element_by_xpath('//h1[@class="no_print"]')
            title_text = title_element.text.strip().upper() # Convertir en majuscules
            info_dict['Title'] = title_text
        except NoSuchElementException:
            info_dict['Title'] = "N/A"

        # Extraction du nom du courtier
        try:
            broker_name = driver.find_element_by_xpath('//*[@id="register-show"]/div[1]/div').text
            info_dict['Courtier'] = broker_name
        except NoSuchElementException:
            info_dict['Courtier'] = "N/A"

        labels = ['Numéro de permis', 'Statut', 'Avis et mentions disciplinaires', 'Champ de pratique autorisé', 'Catégorie de permis', 'Mode d\'exercice', 'Agence', 'Numéro de permis de l\'agence', 'Dirigeant d\'agence', 'Adresse professionnelle', 'Téléphone', 'Courriel', 'Adresse du site Web']

        def extract_information(label):
            try:
                label_element = driver.find_element_by_xpath(f'//div[b="{label}"]')
                label_text = label_element.text.strip()
                value_element = label_element.find_element_by_xpath('following-sibling::div')
                value_text = value_element.text.strip()

                # Si le label est "Adresse professionnelle", retirez tous les "\n"
                if label_text == "Adresse professionnelle":
                    value_text = value_text.replace("\n", " ")

                # Si le label est "Catégorie de permis", remplacez "\n" par ", "
                if label_text == "Catégorie de permis":
                    value_text = value_text.replace("\n", ", ")

                # Si le label est "Courtier", remplacez "\n" par ", "
                if label_text == "Courtier":
                    value_text = value_text.replace("\n", ", ")

                # Si le label est "Avis et mentions disciplinaires" et contient "\n", prenez uniquement le texte avant "\n"
                if label_text == "Avis et mentions disciplinaires" and "\n" in value_text:
                    value_text = value_text.split("\n")[0]

                info_dict[label_text] = value_text

            except NoSuchElementException:
                info_dict[label] = "N/A"

        for label in labels:
            extract_information(label)
        
        info_dict['URL'] = response.url

        # Vérifiez si l'URL a déjà été extraite
        if info_dict['URL'] not in self.extracted_urls:
            self.extracted_urls.add(info_dict['URL'])
            self.consecutive_existing_urls = 0  # Réinitialisez le compteur car nous avons trouvé une URL non existante
            print(info_dict)

            # Créez une sauvegarde avec la date et l'heure
            timestamp = datetime.now().strftime("%Y-%m-%d")
            backup_csv_filename = f'oaciq_result_{timestamp}.csv'
            backup_json_filename = f'oaciq_result_{timestamp}.json'

            # Sauvegarde CSV
            df = pd.DataFrame([info_dict])
            with open(backup_csv_filename, 'a', encoding='utf-8') as f:
                df.to_csv(f, index=False, header=f.tell() == 0)

            with open('oaciq_result.csv', 'a', encoding='utf-8') as f:
                df.to_csv(f, index=False, header=f.tell()==0)

            # Sauvegarde JSON
            try:
                # Lisez les données existantes de oaciq_result.json
                with open('oaciq_result.json', 'r', encoding='utf-8') as json_file:
                    existing_data = json.load(json_file)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = []

            # Ajoutez les nouvelles données
            existing_data.append(info_dict)

            # Écrivez les données combinées dans oaciq_result.json
            with open('oaciq_result.json', 'w', encoding='utf-8') as json_file:
                json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

            # Écrivez également les données combinées dans backup_json_filename
            with open(backup_json_filename, 'w', encoding='utf-8') as json_file:
                json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

        # Passez au courtier suivant
        remaining_brokers = response.meta.get('remaining_brokers', [])
        if remaining_brokers:
            next_broker = remaining_brokers.pop(0)
            yield SeleniumRequest(
                url=response.urljoin(next_broker),
                wait_time=self.delay,
                callback=self.parse_captcha,
                meta={'handle': 'new', 'remaining_brokers': remaining_brokers}
            )
            
        else:
            # Retournez à la page initiale pour recommencer le processus
            yield SeleniumRequest(
                url='https://www.oaciq.com/fr#trouver-courtier',
                wait_time=self.delay,
                callback=self.parse_initial,
                dont_filter=True,
                script='''document.querySelector('input[type="submit"][name="commit"]').click();'''
            )
