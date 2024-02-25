import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from collections import OrderedDict
from datetime import datetime
import pandas as pd
import json



class CENTRIS_BROKER(scrapy.Spider):
    name = 'centris_broker'
    allowed_domains = ['centris.ca']
    extracted_urls = set()  # Initialisation ici

    def __init__(self, *args, **kwargs):
        super(CENTRIS_BROKER, self).__init__(*args, **kwargs)
        self.extracted_urls = set()  # Initialisation de l'ensemble des URL extraites


    def start_requests(self):
        yield SeleniumRequest(
            url='https://www.centris.ca/fr/courtiers-immobiliers?view=Summary&pback=true&uc',
            callback=self.parse,
            wait_time=3,
        )


    def parse(self, response):
        driver = response.meta['driver']
        self.handle_cookie_popup(driver)

        info_dict = OrderedDict([
            ("Name", ""),
            ("Agency", ""),
            ("Phone", ""),
            ("Speak", ""),
            ("Area", ""),
            ("Date", datetime.now().strftime('%Y-%m-%d')),
            # ("URL", current_url)
        ])

        # Capture d'écran après la gestion de la popup des cookies
        driver.save_screenshot("centris_broker.png")

        # XPath pour le nom et le téléphone du courtier
        broker_name_xpath = "//h1[contains(@class, 'broker-info__broker-title')]"
        broker_agency_xpath = "//h2[contains(@class, 'p1 font-weight-medium m-0')]"
        broker_phone_xpath = "(//a[@itemprop='telephone'])[1]"
        broker_langage_xpath = "//div[@class='p2']/span"
        broker_area_xpath = "//div[@class='col-lg-6']/div[@class='p2']"
        try:
            broker_name_element = driver.find_element_by_xpath(broker_name_xpath)
            broker_name = broker_name_element.text.strip()
            info_dict['Name'] = broker_name
            print("Broker Name:", broker_name)

        except NoSuchElementException:
            print("Broker name not found")

        try:
            broker_agency_element = driver.find_element_by_xpath(broker_agency_xpath)
            broker_agency = broker_agency_element.text.strip()
            info_dict['Agency'] = broker_agency
            print("Broker Agency:", broker_agency)

        except NoSuchElementException:
            print("Broker agency not found")

        try:
            broker_phone_element = driver.find_element_by_xpath(broker_phone_xpath)
            broker_phone = broker_phone_element.get_attribute('content').strip()
            info_dict['Phone'] = broker_phone
            print("Broker Phone:", broker_phone)

        except NoSuchElementException:
            print("Broker phone not found")

        try:
            broker_langage_element = driver.find_element_by_xpath(broker_langage_xpath)
            broker_speak = broker_langage_element.text.strip()
            info_dict['Speak'] = broker_speak
            print("Broker Speak:", broker_speak)
            
        except NoSuchElementException:
            print("Broker speak not found")

        try:
            broker_area_element = driver.find_element_by_xpath(broker_area_xpath)
            broker_area = broker_area_element.text.strip()
            info_dict['Area'] = broker_area
            print("Broker Area:", broker_area)
            
        except NoSuchElementException:
            print("Broker area not found")

        # Créez une sauvegarde avec la date et l'heure
        timestamp = datetime.now().strftime("%Y-%m-%d")
        backup_csv_filename = f'centris_broker_{timestamp}.csv'
        backup_json_filename = f'centris_broker_{timestamp}.json'

        # Sauvegarde CSV
        df = pd.DataFrame([info_dict])
        with open(backup_csv_filename, 'a', encoding='utf-8') as f:
            df.to_csv(f, index=False, header=f.tell() == 0)

        with open('centris_broker.csv', 'a', encoding='utf-8') as f:
            df.to_csv(f, index=False, header=f.tell()==0)

        # Sauvegarde JSON
        try:
            # Lisez les données existantes de centris_broker.json
            with open('centris_broker.json', 'r', encoding='utf-8') as json_file:
                existing_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # Ajoutez les nouvelles données
        existing_data.append(info_dict)

        # Écrivez les données combinées dans centris_broker.json
        with open('centris_broker.json', 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

        # Écrivez également les données combinées dans backup_json_filename
        with open(backup_json_filename, 'w', encoding='utf-8') as json_file:
            json.dump(existing_data, json_file, ensure_ascii=False, indent=4)

       # Tentative de clic sur le bouton "Suivant"
        try:
            print("Recherche du bouton 'Suivant'...")
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//li[@class='next'])[1]/a"))
            )
            print("Bouton 'Suivant' trouvé. Tentative de clic...")

            # Scroll jusqu'au bouton
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)

            # Clic via JavaScript
            driver.execute_script("arguments[0].click();", next_button)

            # Attente de chargement de la nouvelle page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'broker-info__broker-title')]"))
            )
            print("Page suivante chargée avec succès.")

            # Continuation de la pagination
            yield SeleniumRequest(
                url=driver.current_url,
                callback=self.parse,
                dont_filter=True
            )

        except TimeoutException:
            print("Le bouton 'Suivant' n'a pas été trouvé ou il n'y a plus de pages à traiter.") 


    def handle_cookie_popup(self, driver):
        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@id='didomi-notice-agree-button']"))
            )
            accept_button.click()
            print("Cookie popup handled.")

        except TimeoutException:
            print("No cookie popup found.")

    def is_duplicate(existing_data, current_dict):
        for data in existing_data:
            if data['Name'] == current_dict['Name'] and data['Phone'] == current_dict['Phone']:
                return True
        return False
