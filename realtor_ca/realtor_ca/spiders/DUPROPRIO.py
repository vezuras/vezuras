import scrapy
import json
import csv
from datetime import datetime

class DUPROPRIOSpider(scrapy.Spider):
    name = 'DUPROPRIO'
    start_url = 'https://duproprio.com/fr/rechercher/liste?search=true&is_for_sale=1&with_builders=1&parent=1&pageNumber={}&sort=-published_at'

    custom_settings = {'CLOSESPIDER_PAGECOUNT': 24}

    def start_requests(self):
        page_number = 1
        yield scrapy.Request(url=self.start_url.format(page_number), meta={'page_number': page_number}, callback=self.parse)

    def parse(self, response):
        page_number = response.meta['page_number']
        annonce_urls = response.xpath("//ul[@class='search-results-listings-list']/li/a/@href").getall()
        for url in annonce_urls:
            yield scrapy.Request(url=url, callback=self.parse_summary_page)

        next_page_number = page_number + 1
        next_page_url = self.start_url.format(next_page_number)
        yield scrapy.Request(url=next_page_url, meta={'page_number': next_page_number}, callback=self.parse)

    def parse_summary_page(self, response):
        script_content_1 = response.xpath("//script[contains(text(), 'SingleFamilyResidence')]/text()").get()
        data_1 = json.loads(script_content_1)
        script_content_2 = response.xpath("//script[contains(text(), 'Product')]/text()").get()
        data_2 = json.loads(script_content_2)


        title = response.xpath("//h3[@class='listing-location__title']/a/text()").get()
        # price = response.xpath("//div[@class='listing-price__amount']/text()").get()
        category = title.rsplit(' à vendre', 1)[0].strip()
        # price = price.strip()
        street_address = data_1.get('address', {}).get('streetAddress', '')
        locality = data_1.get('address', {}).get('addressLocality', '')
        postal_code = data_1.get('address', {}).get('postalCode', '')
        latitude = data_1.get('geo', {}).get('latitude', '')
        longitude = data_1.get('geo', {}).get('longitude', '')
        telephone = data_1.get('telephone', [])
        description = data_2.get('description', '')
        images = data_2.get('image', [])
        price = data_2.get('offers', {}).get('price', '')
        url = data_2.get('offers', {}).get('url', '')
        duproprio_id = data_2.get('sku', '')

        annonce = {
            'source': 'duproprio',
            'category': category,
            'price': price,
            'street_address': street_address,
            'locality': locality,
            'postal_code': postal_code,
            'latitude': latitude,
            'longitude': longitude,
            'telephone': telephone,
            'description': description,
            'images': images,
            'url': response.url,
            'duproprio_id': duproprio_id
        }

        yield annonce
