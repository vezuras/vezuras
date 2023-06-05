import scrapy
import json
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider
from urllib.parse import urljoin
import re
from datetime import datetime


class CentrisSpider(CrawlSpider):
    name = 'centris'
    allowed_domains = ['centris.ca']
    position = {
        "startPosition": 0  # Début à la position 0
    }
    query = {
        "pageNumber": 1,
        "pageSize": 100,
        "sortBy": "price",
        "propertyType": "residential"
    }

    def __init__(self, *args, **kwargs):
        super(CentrisSpider, self).__init__(*args, **kwargs)
        self.current_page = 1

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.centris.ca/UserContext/Lock',
            method='POST',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/json'
            },
            body=json.dumps({'uc': 0}),
            callback=self.generate_uck
        )

    def generate_uck(self, response):
        uck = response.body.decode('utf-8')
        self.query["uck"] = uck
        yield scrapy.Request(
            url='https://www.centris.ca/Property/GetInscriptions',
            method='POST',
            body=json.dumps(self.query),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.parse
        )

    def parse(self, response):
        resp_dict = json.loads(response.body)
        html = resp_dict.get('d').get('Result').get('html')
        parse_html = Selector(text=html)
        urls = parse_html.xpath("//a[@class='property-thumbnail-summary-link']")
        for url in urls:
            yield scrapy.Request(
                url=urljoin(response.url, url.xpath(".//@href").get()),
                callback=self.parse_listing,
                cb_kwargs={'page_number': self.current_page}  # Passer le numéro de page en tant qu'argument
            )

        count = resp_dict.get('d').get('Result').get('count')
        inscNumberPerPage = resp_dict.get('d').get('Result').get('inscNumberPerPage')

        if self.query['pageNumber'] * self.query['pageSize'] < count:
            self.query['pageNumber'] += 1
            self.current_page += 1
            if self.current_page % 20 == 0:  # Vérifier si c'est le dernier élément d'une page
                self.query['pageNumber'] += 1  # Passer à la page suivante
            yield self.update_query_request()

    def parse_listing(self, response, page_number):  # Ajouter le paramètre page_number pour récupérer le numéro de page
        category = response.css('span[data-id="PageTitle"]::text').get()
        category_text = self.extract_title_text(category)
        address = response.css('h2[itemprop="address"]::text').get()
        full_address = self.extract_full_address(address)
        address_components = self.extract_address_keys(full_address)
        price = response.css('span[id="BuyPrice"]::text').get()
        latitude = response.xpath("//meta[@itemprop='latitude']/@content").get()
        longitude = response.xpath("//meta[@itemprop='longitude']/@content").get()
        source = 'centris'
        yield {
            'source': source,
            'page_number': page_number,  # Ajouter le numéro de page au dictionnaire des annonces
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'titre': category_text,
            'prix': price,
            'full_address': full_address,
            'address': address_components,
            'latitude': latitude,
            'longitude': longitude,
            'url': response.url,
        }

    def update_query_request(self):
        self.position['startPosition'] += self.query['pageSize']
        return scrapy.Request(
            url='https://www.centris.ca/Property/GetInscriptions',
            method='POST',
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json',
                'Origin': 'https://www.centris.ca',
                'Referer': 'https://www.centris.ca/en/propriete~a-vendre?view=Thumbnail',
            },
            callback=self.parse
        )

    def extract_title_text(self, titre):
        if titre and isinstance(titre, str):
            pattern = r'(.*?)\s+(?:à vendre|for sale)'
            match = re.search(pattern, titre, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ''

    def extract_full_address(self, address):
        if address:
            return address.strip()
        else:
            return ''

    def extract_address_keys(self, full_address):
        street_address = ''
        unity = ''
        locality = ''
        region = ''
        postal_code = ''

        patterns = [
            r'^(.*?),\s*(.*?),\s*app\.\s*([\w]+)?,\s*(.*?),\s*(.*?)$',
            r'^(.*?),\s*(.*?),\s*(.*?),\s*(.*?)$',
            r'^(.*?),\s*(.*?),\s*(.*?)$',
            r'^(\w+),\s*(.*?)\s+\((.*?)\)$',
            r'^(.*?),\s*(.*?)$'
        ]

        for pattern in patterns:
            match = re.match(pattern, full_address)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    street_address = f"{groups[0]} {groups[1]}".strip()
                if len(groups) >= 3:
                    unity = groups[2].strip()
                if len(groups) >= 4:
                    locality = groups[3].strip()
                if len(groups) >= 5:
                    region = groups[4].strip()
                break

        return {
            'street_address': street_address,
            'unity': unity,
            'locality': locality,
            'region': region,
            'postal_code': postal_code
        }
