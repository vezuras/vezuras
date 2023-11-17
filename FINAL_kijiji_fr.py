import scrapy
import json
from bs4 import BeautifulSoup
from datetime import datetime
import re
from urllib.parse import urljoin


class KIJIJI_FRSpider(scrapy.Spider):
    name = 'kijiji_fr'
    start_urls = ['https://www.kijiji.ca/b-a-vendre/quebec/c30353001l9001?ad=offering']
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
        "Accept-Language": "fr",},
    }
    # custom_settings = {'CLOSESPIDER_PAGECOUNT': 200}

    def __init__(self, *args, **kwargs):
        super(KIJIJI_FRSpider, self).__init__(*args, **kwargs)
        self.data = []
        self.items_processed = 0

    def start_requests(self):
        page_number = 1
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, meta={'page_number': page_number})

    # def parse(self, response):
    #     page_number = response.meta['page_number']
    #     vip_urls = response.css('.search-item[data-vip-url]::attr(data-vip-url)').getall()
    #     self.items_processed = 0
    #     for url in vip_urls:
    #         full_url = 'https://www.kijiji.ca' + url
    #         yield scrapy.Request(url=full_url, callback=self.parse_summary_page, meta={'page_number': page_number})

    def parse(self, response):
        page_number = response.meta['page_number']
        annonce_urls = response.xpath("(//ul[@class='sc-608fbfb8-0 hZVmEd'])[2]//li//a/@href").getall()
        self.items_processed = 0
        for url in annonce_urls:
            # Remplacer le segment en anglais par du français
            url_fr = url.replace('for-sale', 'a-vendre').replace('house', 'maison').replace('condo', 'condo-a-vendre')
            full_url = response.urljoin(url_fr)
            yield scrapy.Request(url=full_url, callback=self.parse_summary_page, meta={'page_number': page_number})

    # Le reste de la logique de pagination reste le même

        # Pagination
        next_page_number = page_number + 1
        next_page_url = urljoin(self.start_urls[0], f'page-{next_page_number}/c30353001l9001')
        yield scrapy.Request(url=next_page_url, callback=self.parse, meta={'page_number': next_page_number})

    def parse_summary_page(self, response):
        extracted_data = {}
        soup = BeautifulSoup(response.body, 'html.parser')
        meta_elements = soup.find_all('meta')
        for meta_element in meta_elements:
            property_name = meta_element.get('property')
            content = meta_element.get('content')
            if property_name and content:
                if property_name.startswith('og:'):
                    property_name = property_name[3:]
                extracted_data[property_name] = content

        addresses = response.xpath("//span[@itemprop='address']/text()").get()
        price = response.xpath("//span[contains(@class, 'currentPrice')]/span/text()").get()
        sku = response.xpath("//li[contains(@class, 'currentCrumb')]/a/text()").get()
        description = extracted_data['description']
        locality = extracted_data['locality']
        region = extracted_data['region']
        latitude = extracted_data['latitude']
        longitude = extracted_data['longitude']
        title = response.xpath("(//span[@itemprop='name'])[4]/text()").get()
        category_match = re.search(r'(.+)(?: à vendre| for sale)', title)
        category = category_match.group(1) if category_match else ''
        extracted_data = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'source': self.name[:-3],
            'category': category,  # Ajoutez la catégorie appropriée ici
            'price': price,
            'full_address': addresses,  # Ajoutez l'adresse complète ici
            'address': {
                'street_address': addresses,  # Assignez la rue extraite ici
                'postal_code': '',  # Assignez le code postal extrait ici
                'locality': locality,  # Assignez la localité extraite ici
                'region': region,  # Assignez la région extraite ici
            },
            'latitude': latitude,  # Ajoutez la latitude appropriée ici
            'longitude': longitude,  # Ajoutez la longitude appropriée ici
            'phone': [],  # Ajoutez la liste des numéros de téléphone vides ici
            'description': description,  # Ajoutez la description appropriée ici
            'url': response.url,
            'sku': f"{self.name}-{sku}",
        }

        # Extraction du code postal de l'adresse
        postal_code_match = re.search(r'\b[A-Za-z]\d[A-Za-z] \d[A-Za-z]\d\b|\b[A-Za-z]\d[A-Za-z]\d[A-Za-z]\d\b', addresses)
        if postal_code_match:
            postal_code = postal_code_match.group()
            extracted_data['address']['postal_code'] = postal_code

        yield extracted_data

        self.items_processed += 1

        if self.items_processed == len(response.css('.search-item[data-vip-url]::attr(data-vip-url)')):
            page_number = response.meta['page_number']
            next_page_number = page_number + 1
            next_page_url = self.start_urls[0].format(next_page_number)
            yield scrapy.Request(url=next_page_url, callback=self.parse_summary_page, meta={'page_number': next_page_number})



