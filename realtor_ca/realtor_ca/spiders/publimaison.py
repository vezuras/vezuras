import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.selector import Selector
import re
from urllib.parse import urljoin
import urllib.parse
import json


class PublimaisonSpider(scrapy.Spider):
    name = "publimaison"
    allowed_domains = ["publimaison.ca"]
    start_urls = ["https://www.publimaison.ca/fr/recherche/?hash=/show=recherche/regions=/villes=/type_propriete=6-1-3-5-4-7-2/categories=/prix_min=0/prix_max=0/caracteristiques=/chambres=0/salles_bain=0/etat=1/parution=4/construction=5/trier_par=3/nbr_item=20/page=0"]
    custom_settings = {'CLOSESPIDER_ITEMCOUNT': 10}

    def parse(self, response):
        urls = response.xpath("//div[@class='infos']/a/@href").getall()
        absolute_urls = [response.urljoin(url) for url in urls]
        for url in absolute_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_summary,
            )

    def parse_summary(self, response):
        cookie_request_verification_token = response.headers.getlist('Set-Cookie')
        cookie_request_verification_token = cookie_request_verification_token[0].decode('utf-8') if cookie_request_verification_token else ''
        cookie_publimaisonalertelang = response.headers.getlist('Set-Cookie')
        cookie_publimaisonalertelang = cookie_publimaisonalertelang[1].decode('utf-8') if len(cookie_publimaisonalertelang) > 1 else ''
        request_verification_token = response.xpath('//input[@name="__RequestVerificationToken"]/@value').get()
        hashes = response.css('span.telephone::attr(data-url)').getall()

        titre = response.xpath("//div[@class='titres']/h2/text()").get()
        category = response.xpath("(//div[@class='one columns'])[1]/ul/li[2]/div/text()").get()
        price = response.css('div.prix h3::text').get()
        map_url = response.url + "/carte"
        # Construire les données pour la requête AJAX
        data = {
            '__RequestVerificationToken': request_verification_token,
        }

        # Envoyer la requête AJAX avec les cookies inclus dans les headers
        ajax_url = 'https://www.publimaison.ca/StatCounter/Telephone'
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',  # Ajouter l'en-tête Content-Type
            'Cookie': f'{cookie_request_verification_token}; {cookie_publimaisonalertelang}'  # Inclure les cookies dans les headers de la requête
        }

        for hash_value in hashes:
            data['hash'] = hash_value
            yield scrapy.FormRequest(
                url=ajax_url,
                method='POST',
                formdata=data,
                headers=headers,
                callback=self.parse_telephones,
                meta={'annonce': {'url': response.url, 'titre': titre, 'category': category, 'price': price}}
            )

        yield scrapy.Request(
            url=map_url,
            callback=self.parse_map,
            meta={'annonce': {'url': response.url, 'titre': titre, 'category': category, 'price': price}}
        )

    def parse_map(self, response):
        script = response.xpath("//script[contains(., 'markerClusterer=new MarkerClusterer')]").get()

        if script:
            extracted_content = script.strip()

            latitude_match = re.search(r'var latitude=(-?\d+\.\d+);', extracted_content)
            longitude_match = re.search(r'var longitude=(-?\d+\.\d+);', extracted_content)

            if latitude_match and longitude_match:
                latitude = latitude_match.group(1)
                longitude = longitude_match.group(1)
                self.logger.info("Latitude: %s, Longitude: %s", latitude, longitude)

                annonce = response.meta['annonce']
                annonce['latitude'] = latitude
                annonce['longitude'] = longitude
                yield annonce

            else:
                self.logger.info("Impossible d'extraire la latitude et la longitude")

    def parse_telephones(self, response):
        data = json.loads(response.text)
        phone_number = data.get("value")
        
        if phone_number:
            annonce = response.meta['annonce']
            annonce['telephone'] = phone_number
            yield annonce
