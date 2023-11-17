import scrapy
import json
from datetime import datetime

class DUPROPRIO_FRSpider(scrapy.Spider):
    name = 'duproprio_fr'
    start_url = 'https://duproprio.com/fr/rechercher/liste?search=true&is_for_sale=1&with_builders=1&parent=1&pageNumber={}&sort=-published_at'
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {"Accept-Language": "fr"},
    }

    def start_requests(self):
        """ Initialiser les requêtes en commençant par la première page. """
        page_number = 1
        yield scrapy.Request(url=self.start_url.format(page_number), meta={'page_number': page_number}, callback=self.parse)

    def parse(self, response):
        """ Traiter chaque page de l'index pour extraire les URLs des annonces. """
        page_number = response.meta['page_number']
        annonce_urls = response.xpath("//ul[@class='search-results-listings-list']/li/a/@href").getall()
        for url in annonce_urls:
            yield scrapy.Request(url=url, callback=self.parse_summary_page)

        # Gérer la pagination
        next_page_number = page_number + 1
        next_page_url = self.start_url.format(next_page_number)
        yield scrapy.Request(url=next_page_url, meta={'page_number': next_page_number}, callback=self.parse)

    def parse_summary_page(self, response):
        """ Extraire les données de chaque annonce individuelle. """
        data_1, data_2 = self.extract_json_data(response)
        if data_1 and data_2:
            annonce = self.extract_annonce_data(data_1, data_2, response)
            yield annonce

    def extract_json_data(self, response):
        """ Extraire les données JSON des scripts de la page. """
        script_content_1 = response.xpath("//script[contains(text(), 'SingleFamilyResidence')]/text()").get()
        script_content_2 = response.xpath("//script[contains(text(), 'Product')]/text()").get()
        
        try:
            data_1 = json.loads(script_content_1) if script_content_1 else {}
            data_2 = json.loads(script_content_2) if script_content_2 else {}
        except json.JSONDecodeError:
            # Gérer les erreurs de décodage JSON
            data_1, data_2 = {}, {}

        return data_1, data_2

    def extract_annonce_data(self, data_1, data_2, response):
        """ Extrait et formate les données de l'annonce. """
        title = response.xpath("//h3[@class='listing-location__title']/a/text()").get()
        category = title.rsplit(' à vendre', 1)[0].strip() if title else 'N/A'
        number_of_rooms = data_1.get('numberOfRooms', 'N/A')
        address = data_1.get('address', {})
        street_address = address.get('streetAddress', 'N/A')
        locality = address.get('addressLocality', 'N/A')
        postal_code = address.get('postalCode', 'N/A')
        geo = data_1.get('geo', {})
        latitude = geo.get('latitude', 'N/A')
        longitude = geo.get('longitude', 'N/A')
        phone = data_1.get('telephone', 'N/A')
        url = data_1.get('url', 'N/A')

        description = data_2.get('description', 'N/A')
        image = data_2.get('image', 'N/A')
        offers = data_2.get('offers', {})
        price = offers.get('price', 'N/A')
        price_currency = offers.get('priceCurrency', 'N/A')
        url = offers.get('url', 'N/A')
        sku = data_2.get('sku', 'N/A')

        return {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'source': self.name[:-3],
            'category': category,
            'price': price,
            'address': {
                'street_address': street_address,
                'locality': locality,
                'region': "",
                'postal_code': postal_code,
            },
            'latitude': latitude,
            'longitude': longitude,
            'phone': phone,
            'description': description,
            'url': url,
            'sku': f"{self.name}-{sku}"
        }
