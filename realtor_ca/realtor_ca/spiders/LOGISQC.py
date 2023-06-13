import scrapy
import json
from datetime import datetime

class LOGISQCSpider(scrapy.Spider):
    name = 'logisqc'
    start_url = 'https://www.logisquebec.com/a-vendre/{}'
    custom_settings = {'CLOSESPIDER_ITEMCOUNT': 100}

    def __init__(self, *args, **kwargs):
        super(LOGISQCSpider, self).__init__(*args, **kwargs)
        self.previous_annonce_urls = []

    def start_requests(self):
        page_number = 1
        yield scrapy.Request(url=self.start_url.format(page_number), callback=self.parse, meta={'page_number': page_number})

    def parse(self, response):
        page_number = response.meta['page_number']
        annonce_urls = response.xpath("//div[@id='content-result']/ul/li/a/@href").getall()

        # Vérifier si les annonce_urls actuels sont identiques à ceux de la page précédente
        if self.previous_annonce_urls and set(annonce_urls) == set(self.previous_annonce_urls):
            self.logger.info('Aucune nouvelle annonce trouvée. Fermeture du spider.')
            return

        self.previous_annonce_urls = annonce_urls

        category = response.xpath("//div[@class='box-result-unit-type']/p/text()").get()
        for url in annonce_urls:
            full_url = 'https://www.logisquebec.com' + url
            yield scrapy.Request(url=full_url, callback=self.parse_summary_page, meta={'category': category})

        # Pagination
        next_page_number = page_number + 1
        next_page_url = self.start_url.format(next_page_number)
        yield scrapy.Request(url=next_page_url, callback=self.parse, meta={'page_number': next_page_number})

    def parse_summary_page(self, response):
        category = response.meta['category'].strip()
        script_content_1 = response.xpath("//script[contains(text(), 'SingleFamilyResidence')]/text()").get()
        data_1 = json.loads(script_content_1) if script_content_1 else {}
        script_content_2 = response.xpath("//script[contains(text(), 'Product')]/text()").get()
        data_2 = json.loads(script_content_2) if script_content_2 else {}

        address = data_1.get('address', {})
        street_address = address.get('streetAddress')
        locality = address.get('addressLocality')
        postal_code = address.get('postalCode')
        geo = data_1.get('geo', {})
        latitude = geo.get('latitude')
        longitude = geo.get('longitude')
        phones = data_1.get('telephone')
        phones = [phones] if phones else []  # Convertir en liste si non vide, sinon créer une liste vide

        url = data_1.get('url')

        description = data_2.get('description')
        offers = data_2.get('offers', {})
        price = offers.get('price')
        url = offers.get('url')
        sku = data_2.get('sku')

        # Normalize price
        price = self.normalize_price(price)

        annonce = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'source': self.name,
            'category': category,
            'price': price,
            'address': {
                'street_address': street_address,
                'locality': locality,
                'postal_code': postal_code,
            },
            'latitude': latitude,
            'longitude': longitude,
            'phone': phones,
            'description': description,
            'url': url,
            'sku': f"{self.name}-{sku}",
        }

        yield annonce

    def normalize_price(self, price):
        numeric_part = ''.join(filter(str.isdigit, price))
        formatted_price = '{:,}'.format(int(numeric_part))
        formatted_price = formatted_price.replace(',', ' ')
        formatted_price += ' $'
        return formatted_price
