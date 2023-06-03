import scrapy
from scrapy.selector import Selector
import json
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
        "query": {
            "UseGeographyShapes": 0,
            "Filters": [
                {
                    "MatchType": "CityDistrictAll",
                    "Text": "",
                    "Id": ""
                }
            ],
            "FieldsValues": [
                {
                    "fieldId": "CityDistrictAll",
                    "value": "",
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "Category",
                    "value": "Residential",
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "SellingType",
                    "value": "Sale",
                    "fieldConditionId": "",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "LandArea",
                    "value": "SquareFeet",
                    "fieldConditionId": "IsLandArea",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "SalePrice",
                    "value": 0,
                    "fieldConditionId": "ForSale",
                    "valueConditionId": ""
                },
                {
                    "fieldId": "SalePrice",
                    "value": 999999999999,
                    "fieldConditionId": "ForSale",
                    "valueConditionId": ""
                }
            ]
        },
        "isHomePage": True
    }

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.centris.ca/property/UpdateQuery',
            method='POST',
            body=json.dumps(self.query),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.update_query
        )

    def update_query(self, response):
        yield scrapy.Request(
            url='https://www.centris.ca/Property/GetInscriptions',
            method='POST',
            body=json.dumps(self.position),
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
                callback=self.parse_listing
            )

        count = resp_dict.get('d').get('Result').get('count')
        inscNumberPerPage = resp_dict.get('d').get('Result').get('inscNumberPerPage')

        if self.position['startPosition'] < count:
            self.position['startPosition'] += inscNumberPerPage
            yield self.update_query_request()

    def parse_listing(self, response):
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
        return scrapy.Request(
            url='https://www.centris.ca/Property/GetInscriptions',
            method='POST',
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.parse
        )

    def extract_title_text(self, titre):
        pattern = r'(.*?)\s+(?:à vendre|for sale)'
        match = re.search(pattern, titre, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        else:
            return titre.strip()

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
