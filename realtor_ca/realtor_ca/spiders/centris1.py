import scrapy
from scrapy.selector import Selector
import json
from scrapy.spiders import CrawlSpider
from urllib.parse import urljoin
import re
from datetime import datetime
from urllib.parse import urlencode


class CentrisSpider(CrawlSpider):
    name = 'centris'
    allowed_domains = ['centris.ca']
    position = {"startPosition": 0}  
    PROPERTY_COUNT_QUERY   = {
        "UseGeographyShapes": 0,
        "Filters": [],
        "FieldsValues": [
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
                "fieldId":"LastModifiedDate",
                "value":"2023-06-06",
                "fieldConditionId":"",
                "valueConditionId":""
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
    }
    UPDATE_QUERY  = {
        "query": {
            "UseGeographyShapes": 0,
            "Filters": [],
            "FieldsValues": [
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
            url='https://www.centris.ca/UserContext/Lock',
            method='POST',
            headers={
                'content-type': 'application/json',
                'Origin': 'https://www.centris.ca',
            },
            body=json.dumps({'uc': 0}),
            callback=self.GetPropertyCount
        )

    # def start_requests(self):
    def GetPropertyCount(self, response):
        uck = response.body.decode('utf-8')
        yield scrapy.Request(
            url='https://www.centris.ca/property/GetPropertyCount',
            method='POST',
            body=json.dumps(self.PROPERTY_COUNT_QUERY),
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Origin': 'https://www.centris.ca',
                'X-Centris-Uc': '0',
                'X-Centris-Uck': uck,
            },
            callback=self.UpdateQuery,
            meta={'uck': uck}
        )

    def UpdateQuery(self, response):
        uck = response.meta.get('uck')
        yield scrapy.Request(
            url='https://www.centris.ca/property/UpdateQuery',
            method='POST',
            body=json.dumps(self.UPDATE_QUERY),
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Origin': 'https://www.centris.ca',
                'X-Centris-Uc': '0',
                'X-Centris-Uck': uck,
            },
            callback=self.lock_response,
            meta={'uck': uck}
        )

    def lock_response(self, response):
        yield scrapy.Request(
            url='https://www.centris.ca/UserContext/Lock',
            method='POST',
            headers={
                'content-type': 'application/json',
                'Origin': 'https://www.centris.ca',
            },
            body=json.dumps({'uc': 0}),
            callback=self.GetInscriptions,
            dont_filter=True,
        )

    def GetInscriptions(self, response):
        uck = response.body.decode('utf-8')
        self.uck = uck
        yield scrapy.Request(
            url='https://www.centris.ca/Property/GetInscriptions',
            method='POST',
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Origin': 'https://www.centris.ca',
                'X-Centris-Uc': '0',
                'X-Centris-Uck': self.uck,
            },
            callback=self.parse,
            meta={
                'page_number': 1,
            }
        )

    def parse(self, response):
        page_number = response.meta.get('page_number')
        resp_dict = json.loads(response.body)
        html = resp_dict.get('d').get('Result').get('html')
        parse_html = Selector(text=html)
        urls = parse_html.xpath("//a[@class='property-thumbnail-summary-link']")
        for url in urls:
            yield scrapy.Request(
                url=urljoin(response.url, url.xpath(".//@href").get()),
                callback=self.parse_listing,
                meta={
                    'page_number': page_number,
                }
            )

        count = resp_dict.get('d').get('Result').get('count')
        inscNumberPerPage = resp_dict.get('d').get('Result').get('inscNumberPerPage')

        if self.position['startPosition'] < count:
            self.position['startPosition'] += inscNumberPerPage
            yield from self.update_query(response, inscNumberPerPage=inscNumberPerPage)

    def update_query(self, response, inscNumberPerPage):
        page_number = response.meta.get('page_number')
        yield scrapy.Request(
            url='https://www.centris.ca/Property/GetInscriptions',
            method='POST',
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json; charset=UTF-8',
                'Origin': 'https://www.centris.ca',
                'X-Centris-Uc': '0',
                'X-Centris-Uck': self.uck,
            },
            callback=self.parse,
            meta={
                'page_number': page_number + 1,
                'inscNumberPerPage': inscNumberPerPage,
            }
        )

    def parse_listing(self, response):
        page_number = response.meta.get('page_number')
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
            'page_number': page_number,
            'titre': category_text,
            'prix': price,
            'full_address': full_address,
            'address': address_components,
            'latitude': latitude,
            'longitude': longitude,
            'url': response.url,
        }

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
                for group in groups[2:]:
                    if 'app.' in group:
                        unity = group.replace('app.', '').strip()
                        break
                    elif 'Quartier' in group or 'Neighbourhood' in group:
                        locality_match = re.search(r'(?:Quartier|Neighbourhood)\s*(.*?)$', group)
                        if locality_match:
                            locality = locality_match.group(1).strip()
                    elif not unity:  # Ajout de cette condition pour extraire le contenu dans la clé "region" si "unity" n'est pas trouvé
                        unity_match = re.search(r'app\.\s*([\w]+)', group)
                        if unity_match:
                            unity = unity_match.group(1).strip()
                        else:
                            region = group.strip()
                break

        return {
            'street_address': street_address,
            'unity': unity,
            'locality': locality,
            'region': region,
            'postal_code': postal_code
        }
