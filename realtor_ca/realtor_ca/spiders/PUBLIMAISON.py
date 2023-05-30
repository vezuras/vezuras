import scrapy
import json
from urllib.parse import urljoin
import re

class PublimaisonSpider(scrapy.Spider):
    name = "publimaison"
    allowed_domains = ["publimaison.ca"]
    start_url = "https://www.publimaison.ca/fr/recherche/?hash=/show=recherche/regions=/villes=/type_propriete=6-1-3-5-4-7-2/categories=/prix_min=0/prix_max=0/caracteristiques=/chambres=0/salles_bain=0/etat=1/parution=4/construction=5/trier_par=3/nbr_item=20/page={}"
    custom_settings = {'CLOSESPIDER_ITEMCOUNT': 10}

    def __init__(self, *args, **kwargs):
        super(PublimaisonSpider, self).__init__(*args, **kwargs)
        self.visited_urls = set()
        self.annonces = []

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
                    meta={'hashes': []}
                )

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
        telephone_elements = response.xpath("//span[@class='telephone']")

        titre = response.css('div.titres h3::text').get()
        street_address, unity, locality, region, postal_code, mls = self.extract_address_info(titre)

        if titre:  # Vérifier si le titre existe
            annonce = {
                'url': response.url,
                'titre': titre,
                'category': response.css('div.one.columns ul li:nth-child(2) div::text').get(),
                'price': response.css('div.prix h3::text').get(),
                'telephone': [],
                'address': {
                    'street_address': street_address,
                    'unity': unity,
                    'locality': locality,
                    'region': region,
                    'postal_code': postal_code,
                    'latitude': None,
                    'longitude': None,
                    'mls': mls
                }
            }

            yield scrapy.Request(
                url=response.url + "/carte",
                callback=self.parse_map,
                meta={'annonce': annonce, 'hashes': []}
            )

            for element in telephone_elements:
                hash_value = element.xpath("./@data-url").get()

                data = {
                    '__RequestVerificationToken': request_verification_token,
                    'hash': hash_value,
                }

                ajax_url = 'https://www.publimaison.ca/StatCounter/Telephone'
                headers = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Cookie': f'{cookie_request_verification_token}; {cookie_publimaisonalertelang}'
                }
                yield scrapy.FormRequest(
                    url=ajax_url,
                    method='POST',
                    formdata=data,
                    headers=headers,
                    callback=self.parse_telephones,
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
                annonce['address']['latitude'] = latitude
                annonce['address']['longitude'] = longitude

                self.annonces.append(annonce)
                yield annonce

            else:
                self.logger.info("Impossible d'extraire la latitude et la longitude")

    def parse_telephones(self, response):
        data = json.loads(response.text)
        phone_number = data.get("value")

        if phone_number:
            annonce = response.meta['annonce']
            annonce['telephone'].append(phone_number)

            self.annonces.append(annonce)

    def extract_address_info(self, titre):
        address_match = re.search(r'^(.*?)\s*,\s*(.*?)\s+\((.*?)\)\s+(.*?)\s+\(No.\s+MLS\s+(\d+)\)', titre)
        street_address = address_match.group(1).strip() if address_match else ''
        unity_list = []  # Création d'une liste pour stocker les numéros d'unité

        if 'App.' in titre:
            unity_matches = re.findall(r'App\.(\d+)', titre)
            unity_range_matches = re.findall(r'App\.(\d+)-(\d+)', titre)

            if unity_matches:
                unity_list.extend(int(unity) for unity in unity_matches)  # Ajouter les numéros d'unité individuels à la liste
            if unity_range_matches:
                # Ajouter les numéros d'unité des plages à la liste
                for range_start, range_end in unity_range_matches:
                    unity_list.extend(range(int(range_start), int(range_end) + 1))

            street_address = re.sub(r'App\.\d+(-\d+)?', '', street_address).strip()

        # Supprimer le texte 'App.' de la valeur street_address
        street_address = re.sub(r'\bApp\.\d+\b', '', street_address).strip()

        locality = address_match.group(2).strip() if address_match else ''
        region = address_match.group(3).strip() if address_match else ''
        postal_code = address_match.group(4).strip() if address_match else ''
        mls = address_match.group(5).strip() if address_match else ''

        return street_address, list(set(unity_list)), locality, region, postal_code, mls
