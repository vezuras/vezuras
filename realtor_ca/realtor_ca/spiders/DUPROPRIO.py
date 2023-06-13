import scrapy
import json
import csv
from datetime import datetime

class DUPROPRIOSpider(scrapy.Spider):
    name = 'duproprio'
    start_url = 'https://duproprio.com/fr/rechercher/liste?search=true&is_for_sale=1&with_builders=1&parent=1&pageNumber={}&sort=-published_at'

    # custom_settings = {'CLOSESPIDER_PAGECOUNT': 10}

    def start_requests(self):
        page_number = 1
        yield scrapy.Request(url=self.start_url.format(page_number), meta={'page_number': page_number}, callback=self.parse)

    def parse(self, response):
        page_number = response.meta['page_number']
        annonce_urls = response.xpath("//ul[@class='search-results-listings-list']/li/a/@href").getall()
        category = response.xpath("//div[@class='box-result-unit-type']/p/text()").get()
        for url in annonce_urls:
            yield scrapy.Request(url=url, callback=self.parse_summary_page, meta={'category': category})

        next_page_number = page_number + 1
        next_page_url = self.start_url.format(next_page_number)
        yield scrapy.Request(url=next_page_url, meta={'page_number': next_page_number}, callback=self.parse)

    def parse_summary_page(self, response):
        
        script_content_1 = response.xpath("//script[contains(text(), 'SingleFamilyResidence')]/text()").get()
        data_1 = json.loads(script_content_1)
        script_content_2 = response.xpath("//script[contains(text(), 'Product')]/text()").get()
        data_2 = json.loads(script_content_2)


        title = response.xpath("//h3[@class='listing-location__title']/a/text()").get()
        category = title.rsplit(' à vendre', 1)[0].strip()
        number_of_rooms = data_1.get('numberOfRooms')
        address = data_1.get('address', {})
        street_address = address.get('streetAddress')
        locality = address.get('addressLocality')
        postal_code = address.get('postalCode')
        geo = data_1.get('geo', {})
        latitude = geo.get('latitude')
        longitude = geo.get('longitude')
        telephone = data_1.get('telephone')
        url = data_1.get('url')

        description = data_2.get('description')
        image = data_2.get('image')
        offers = data_2.get('offers', {})
        price = offers.get('price')
        price_currency = offers.get('priceCurrency')
        url = offers.get('url')
        sku = data_2.get('sku')

        annonce = {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'source': self.name,
            'category': category,
            'prix': price,
            'address': {
                'street_address': street_address,
                'locality': locality,
                'region': "",
                'postal_code': postal_code,
            },
            'telephone': telephone,
            'latitude': latitude,
            'longitude': longitude,
            'description': description,
            'url': url,
            'sku': f"{self.name}-{sku}"
        }

        yield annonce
