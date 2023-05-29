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

        next_page_url = response.xpath("//link[@rel='next']/@href").get()
        absolute_next_page_url = urljoin(response.url, next_page_url)

        if next_page_url:
            yield scrapy.Request(
                url=absolute_next_page_url,
                callback=self.parse,
            )

    def parse_summary(self, response):
        cookie_request_verification_token = response.headers.getlist('Set-Cookie')
        cookie_request_verification_token = cookie_request_verification_token[0].decode('utf-8') if cookie_request_verification_token else ''
        cookie_publimaisonalertelang = response.headers.getlist('Set-Cookie')
        cookie_publimaisonalertelang = cookie_publimaisonalertelang[1].decode('utf-8') if len(cookie_publimaisonalertelang) > 1 else ''
        request_verification_token = response.xpath('//input[@name="__RequestVerificationToken"]/@value').get()
        hash_value = response.xpath("//span[@class='telephone']/@data-url").get()
        category = response.xpath("(//div[@class='one columns'])[1]/ul/li[2]/div/text()").get()
        price = response.xpath("//div[@class='prix']/h3/text()").get()
        map_url = response.url + "/carte"
        # Construire les données pour la requête AJAX
        data = {
            '__RequestVerificationToken': request_verification_token,
            'hash': hash_value,
        }

        # Envoyer la requête AJAX avec les cookies inclus dans les headers
        ajax_url = 'https://www.publimaison.ca/StatCounter/Telephone'
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',  # Ajouter l'en-tête Content-Type
            'Cookie': f'{cookie_request_verification_token}; {cookie_publimaisonalertelang}'  # Inclure les cookies dans les headers de la requête
        }
        yield scrapy.FormRequest(
            url=ajax_url,
            method='POST',
            formdata=data,
            headers=headers,
            callback=self.parse_telephones
        )

        annonce = {
            'category': category,
            'price': price,
            '__RequestVerificationToken': request_verification_token,
        }

        yield scrapy.Request(
            url=map_url,
            callback=self.parse_map,
            meta={'annonce': annonce}
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

                telephone = response.xpath("//span[@class='telephone']/@data-url")
                if telephone:
                    encoded_telephone = telephone.get()
                    decoded_telephone = self.decode_telephone(encoded_telephone)
                    annonce['telephone'] = decoded_telephone
                    
                    # Envoyer une requête AJAX pour obtenir le numéro de téléphone
                    phone_url = 'https://www.publimaison.ca/StatCounter/Telephone'
                    form_data = {
                        '__RequestVerificationToken': annonce['__RequestVerificationToken'],
                        'hash': decoded_telephone,
                    }
                    yield scrapy.FormRequest(
                        url=phone_url,
                        formdata=form_data,
                        callback=self.parse_telephone_response,
                        meta={'annonce': annonce}
                    )
                else:
                    annonce['telephone'] = None

                yield annonce
            else:
                self.logger.info("Impossible d'extraire la latitude et la longitude")

    def parse_telephones(self, response):
        data = json.loads(response.text)
        phone_number = data.get("value")
        
        if phone_number:
            print("Phone number:", phone_number)
        else:
            print("No phone number found")
