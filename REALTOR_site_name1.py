import scrapy
import xml.etree.ElementTree as ET
import re
import json
from scrapy import signals
# import codecs

class MODEL_realtorSpider(scrapy.Spider):
    name = "MODEL_realtor"
    start_urls = ["https://cdn.realtor.ca/sitemap/realtorsitemap/ListingSitemap{}.xml"]
    addresses = []
    sitemap_number = 1
    results = {address: [] for address in addresses}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.results = {address: [] for address in self.addresses}
    
    def start_requests(self):
        # Lire les adresses à partir du fichier texte
        with open('address_test.txt', 'r', encoding='utf-8') as f:
            self.addresses = [line.strip() for line in f.readlines()]

        self.results = {address: [] for address in self.addresses}  # Mettre à jour ici

        url = self.start_urls[0].format(self.sitemap_number)
        yield scrapy.Request(url=url, callback=self.parse_sitemap)

    def parse_sitemap(self, response):
        # Parser le contenu XML
        xml_content = response.body
        tree = ET.fromstring(xml_content)

        # Rechercher les URL spécifiques dans le sitemap
        urls = tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        for url in urls:
            url_text = re.findall(r'\w+', url.text.lower())
            for address in self.addresses:
                search_words = re.findall(r'\w+', address.lower())
                # Ignore address if it has less than 3 words or no numeric component
                if len(search_words) < 3 or not any(word.isdigit() for word in search_words):
                    continue

                # Séparer le numéro civique des autres mots
                civic_number = search_words[0] if search_words[0].isdigit() else None
                search_words = search_words[1:] if civic_number else search_words
                
                matching_words = sum(word in url_text for word in search_words)
                matching_civic_numbers = 1 if civic_number and civic_number in url_text else 0

                # Vérification du dernier mot dans l'adresse
                if search_words[-1] not in url_text:
                    continue

                # Nous ajoutons l'URL seulement si au moins 75% des mots correspondent
                if matching_words / len(search_words) >= 0.75 and matching_words >= 3 and matching_civic_numbers >= 1:
                    result = {
                        'url': url.text,
                        'sitemap_url': response.url,
                        'matching_words': f"{matching_words}/{len(search_words)}",
                        'matching_civic_numbers': matching_civic_numbers
                    }
                    self.results[address].append(result)

                    # Limite le nombre d'URLs à 4 par adresse
                    if len(self.results[address]) >= 4:
                        break

        # Passer à la page de sitemap suivante
        self.sitemap_number += 1
        next_sitemap_url = self.start_urls[0].format(self.sitemap_number)
        yield scrapy.Request(url=next_sitemap_url, callback=self.parse_sitemap)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.closed, signal=signals.spider_closed)
        return spider

    def closed(self, reason):
        # Enregistrer les résultats dans un fichier JSON
        filename = 'results.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False)
        self.log(f'Results saved to {filename}')
