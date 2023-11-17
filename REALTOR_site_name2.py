from pymongo import MongoClient
import scrapy
import xml.etree.ElementTree as ET
import re
import json
from scrapy import signals
from scrapy.signalmanager import dispatcher


class REALTORSpider(scrapy.Spider):
    name = "realtor"
    START_URLS = ["https://cdn.realtor.ca/sitemap/realtorsitemap/ListingSitemap{}.xml"]
    ANNONCEURS = ["duproprio", "kijiji", "lespac", "publimaison", "logisqc"]
    
    sitemap_number = 1
    results = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dispatcher.connect(self.save_results, signals.spider_closed)

    def start_requests(self):
        mongo_uri = self.settings.get('MONGO_URI')
        mongo_db = self.settings.get('MONGO_DATABASE')
        addresses = self.load_addresses_from_mongodb(mongo_uri, mongo_db)
        
        for url in self.START_URLS:
            yield scrapy.Request(url.format(self.sitemap_number), 
                                 callback=self.parse_sitemap,
                                 cb_kwargs={'addresses': addresses})

    def load_addresses_from_mongodb(self, mongo_uri, mongo_db):
        client = MongoClient(mongo_uri)
        db = client[mongo_db]
        collection = db["avpp_fr_2023-09-12"]
        addresses = []

        projection = {f"{annonceur}.address.street_address": 1 for annonceur in self.ANNONCEURS}
        projection.update({f"{annonceur}.url": 1 for annonceur in self.ANNONCEURS})
        # print(projection)
        for doc in collection.find({}, projection):
            for annonceur in self.ANNONCEURS:
                if annonceur in doc:
                    for obj in doc[annonceur]:  # assuming that doc[annonceur] is a list
                        # print(f"URL for {annonceur}: {obj.get('url')}")
                        if isinstance(obj, dict) and "address" in obj and "street_address" in obj["address"]:
                            address = obj["address"]["street_address"]
                            url = obj.get("url", "")  # Extract the URL
                            addresses.append((address, url))  # Store as a tuple

        return addresses

    def parse_sitemap(self, response, addresses):
        # Parser le contenu XML
        xml_content = response.body
        tree = ET.fromstring(xml_content)

        # Utilisez un set pour stocker les adresses traitées
        processed_addresses = set()
        for address, source_url in addresses:
            if address in processed_addresses:
                continue
            processed_addresses.add(address)

            if address not in self.results:
                self.results[address] = []

            # Rechercher les URL spécifiques dans le sitemap
            urls = tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
            found_match = False  # Ajoutez cette ligne pour suivre si un match est trouvé
            for url in urls:
                url_text = re.findall(r'\w+', url.text.lower())
                search_words = re.findall(r'\w+', address.lower())
                # Ignore address if it has less than 3 words or no numeric component
                if len(search_words) < 3 or not any(word.isdigit() for word in search_words):
                    continue

                # Séparer le numéro civique des autres mots
                civic_number = search_words[0] if search_words[0].isdigit() else None
                search_words = search_words[1:] if civic_number else search_words
                    
                matching = sum(word in url_text for word in search_words)
                matching_civic_numbers = 1 if civic_number and civic_number in url_text else 0

                # Vérification du dernier mot dans l'adresse
                last_word = search_words[-1]
                if len(last_word) < 3 or last_word not in url_text:
                    continue
                    
                # Calculer le ratio
                ratio = matching / len(search_words) * 100
                ratio = round(ratio)

                # Si une correspondance parfaite est trouvée
                if ratio == 1.0 and matching_civic_numbers >= 1:
                    perfect_match = len(matching) == len(search_words)
                    perfect_match_exists = any(result['matching_word'] == perfect_match for result in self.results[address] if 'matching_word' in result)

                    # Si une correspondance parfaite existe déjà, passer à l'URL suivante
                    if perfect_match_exists:
                        continue

                    # Ajouter la nouvelle correspondance parfaite à la liste des résultats pour cette adresse
                    result = {
                        'realtor_url': url.text,
                        'sitemap_url': response.url,
                        'annonceur_url': source_url,
                        'matching_word': '100%',
                        'matching_civic_numbers': matching_civic_numbers
                    }
                    self.results[address].append(result)
                    found_match = True  # Mettez à jour la variable pour indiquer qu'un match a été trouvé
                    break

                elif matching_civic_numbers >= 1 and len(self.results[address]) < 4:                                
                    result = {
                        'realtor_url': url.text,
                        'sitemap_url': response.url,
                        'annonceur_url': source_url,
                        'matching_word': f'{ratio}%',
                        'matching_civic_numbers': matching_civic_numbers
                    }
                    self.results[address].append(result)
                    found_match = True  # Mettez à jour la variable pour indiquer qu'un match a été trouvé

            # Si aucun match n'a été trouvé pour cette adresse, ajoutez un résultat avec "N/A" pour "matching"
            # if not found_match:
            #     self.results[address].append({
            #         'correspondance': 'N/A',
            #         'annonceur_url': source_url,
            #     })

            # Ajoutez l'adresse au set une fois qu'elle a été traitée
            processed_addresses.add(address)

        # Passer à la page de sitemap suivante
        self.sitemap_number += 1
        next_sitemap_url = self.START_URLS[0].format(self.sitemap_number)
        yield scrapy.Request(url=next_sitemap_url, callback=self.parse_sitemap, cb_kwargs={'addresses': addresses})

        # for address, results in self.results.items():
        #     yield {
        #         'address': address,
        #         'results': results
        #     }

    def save_results(self, spider):
        filename = 'results.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False)
        self.log(f'Results saved to {filename}')
