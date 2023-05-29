import scrapy
import json
import re
from urllib.parse import urljoin

class PublimaisonSpider(scrapy.Spider):
    name = "publimaison"
    allowed_domains = ["publimaison.ca"]
    start_url = "https://www.publimaison.ca/fr/recherche/?hash=/show=recherche/regions=/villes=/type_propriete=6-1-3-5-4-7-2/categories=/prix_min=0/prix_max=0/caracteristiques=/chambres=0/salles_bain=0/etat=1/parution=4/construction=5/trier_par=3/nbr_item=20/page={}"
    # custom_settings = {'CLOSESPIDER_PAGECOUNT': 2}
    # custom_settings = {'CLOSESPIDER_ITEMCOUNT': 2}

    def __init__(self, *args, **kwargs):
        super(PublimaisonSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()

    def start_requests(self):
        yield scrapy.Request(url=self.start_url.format(0), callback=self.parse)

    def parse(self, response):
        urls = response.xpath("//div[@class='infos']/a/@href").getall()
        absolute_urls = [response.urljoin(url) for url in urls]
        for url in absolute_urls:
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_summary,
                    meta={'hashes': []}  # Ajout de la liste hashes en tant que méta-donnée
                )

        # Pagination
        next_page_url = response.xpath("//link[@rel='next']/@href").get()
        if next_page_url:
            absolute_next_page_url = urljoin(response.url, next_page_url)
            yield scrapy.Request(url=absolute_next_page_url, callback=self.parse)

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

        # Ajout des informations dans le dictionnaire de l'annonce
        annonce = {
            'url': response.url,
            'titre': titre,
            'category': category,
            'price': price,
            'telephone': []  # Initialisation de la liste de numéros de téléphone
        }

        yield scrapy.Request(
            url=map_url,
            callback=self.parse_map,
            meta={'annonce': annonce, 'hashes': hashes}  # Passer l'annonce et les hashes en tant que méta-données
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
            annonce['telephone'].append(phone_number)

        # Vérifier s'il reste d'autres hashes non traités
        hashes = response.meta['hashes']
        if hashes:
            hash_value = hashes.pop(0)
            data = {
                '__RequestVerificationToken': response.meta['__RequestVerificationToken'],
                'hash': hash_value
            }
            yield scrapy.FormRequest(
                url='https://www.publimaison.ca/StatCounter/Telephone',
                method='POST',
                formdata=data,
                headers={'X-Requested-With': 'XMLHttpRequest'},
                callback=self.parse_telephones,
                meta={'annonce': annonce, 'hashes': hashes}  # Passer l'annonce et les hashes en tant que méta-données
            )
        else:
            yield annonce
