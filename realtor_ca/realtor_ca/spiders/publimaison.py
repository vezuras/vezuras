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
        category = response.xpath("(//div[@class='one columns'])[1]/ul/li[2]/div/text()").get()
        price = response.xpath("//div[@class='prix']/h3/text()").get()
        map_url = response.url + "/carte"

        # Extraire le jeton de vérification de la requête '__RequestVerificationToken'
        request_verification_token = response.css('input[name="__RequestVerificationToken"]::attr(value)').get()
        
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

    def parse_telephone_response(self, response):
        annonce = response.meta['annonce']
        telephone_data = json.loads(response.text)

        telephone = telephone_data['value']
        annonce['telephone'] = telephone

        yield annonce

    def decode_telephone(self, url):
        url = urllib.parse.unquote(url)
        return url.replace("%C2%A0", "").replace("%2b", "+").replace("%2f", "/")
