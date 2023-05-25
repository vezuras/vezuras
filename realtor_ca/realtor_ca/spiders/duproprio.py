import scrapy
import json
from urllib.parse import urljoin, urlparse, parse_qs
from scrapy.exceptions import CloseSpider

class DupSpider(scrapy.Spider):
    name = 'dup'
    start_urls = ['https://duproprio.com/fr/rechercher/liste?search=true&is_for_sale=1&with_builders=1&parent=1&pageNumber=1&sort=-published_at']
    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 4,  # Limite le nombre de pages analysées à 4
    }

    def clean_text(self, text):
        if text is not None:
            cleaned_text = text.strip()
            return cleaned_text
        return ''

    def parse(self, response):
        # Extraire le contenu du script JSON
        script_content = response.xpath("//div[@class='search-results-listings ']/script/text()").get()

        # Extraire les coordonnées des annonces
        data = json.loads(script_content)
        if 'mainEntity' in data:
            main_entity = data['mainEntity']
            if isinstance(main_entity, list) and len(main_entity) > 0:
                items = main_entity[0].get('itemListElement', [])
                for index, item in enumerate(items, start=1):
                    if 'item' in item and 'geo' in item['item']:
                        latitude = item['item']['geo'].get('latitude', '')
                        longitude = item['item']['geo'].get('longitude', '')

                        # Extraire l'URL de l'annonce correspondante
                        url = item['item'].get('url', '')

                        # Extraire les autres éléments de l'annonce
                        row = response.xpath("//ul[@class='search-results-listings-list']/li[a/@href='{}']"
                                             .format(url))
                        if row:
                            link = self.clean_text(row.xpath(".//a[2]/@href").get())
                            price = self.clean_text(row.xpath("normalize-space(.//div[@class='search-results-listings-list__item-description__price']//h2/text())").get())
                            city = self.clean_text(row.xpath("normalize-space(.//div[@class='search-results-listings-list__item-description__city-wrap']//h3/span/text())").get())
                            address = self.clean_text(row.xpath("normalize-space(.//div[@class='search-results-listings-list__item-description__item search-results-listings-list__item-description__address']/text())").get())
                            tags = self.clean_text(row.xpath("normalize-space(.//div[@class='search-results-listings-list__tags']/div/text())").get())
                            description = self.clean_text(row.xpath("normalize-space(.//div[@class='search-results-listings-list__item-description__item search-results-listings-list__item-description__type-and-intro']/text())").get())

                            # Extraire la catégorie
                            category = ''
                            if description and 'à vendre' in description:
                                category = self.clean_text(description.split('à vendre')[0])

                            # Ajouter les coordonnées, l'URL, les autres éléments et la catégorie aux informations de l'annonce
                            yield {
                                'category': category,
                                'price': price,
                                'address': address,
                                'city': city,
                                'tags': tags,
                                'latitude': latitude,
                                'longitude': longitude,
                                'description': description,
                                'url': url,
                            }

                # Extraire le numéro de page actuel
                parsed_url = urlparse(response.url)
                query_params = parse_qs(parsed_url.query)
                page_number = int(query_params.get('pageNumber', [1])[0])

                # Construire l'URL de la page suivante
                next_page_number = page_number + 1
                next_page_url = urljoin(response.url, f'?search=true&is_for_sale=1&with_builders=1&parent=1&pageNumber={next_page_number}&sort=-published_at')

                # Suivre la page suivante si le nombre de pages analysées est inférieur à la limite
                if next_page_number <= self.settings['CLOSESPIDER_PAGECOUNT']:
                    yield response.follow(next_page_url, callback=self.parse)
                else:
                    raise CloseSpider('Reached the maximum page count')
