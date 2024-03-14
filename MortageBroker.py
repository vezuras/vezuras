# import scrapy

# class PJSpider(scrapy.Spider):
#     name = 'pj'
#     start_urls = ['https://www.pagesjaunes.ca/search/si/1/courtier+hypoth%C3%A9caire/QC']
#     start_urls = ['https://www.pagesjaunes.ca/search/si/1/hypoth%C3%A9caire/QC']
#     base_url = "https://www.pagesjaunes.ca"
#     total_pages = None  # Ajout d'un attribut pour stocker le nombre total de pages


#     def parse(self, response):
#         # Initialiser la page actuelle et le nombre total de pages
#         if self.total_pages is None:
#             self.current_page = 1  # Commencer toujours à la page 1
#             total_pages = response.xpath("(//div[@class='view_more_section_noScroll']//span[@class='pageCount']/span)[2]/text()")
#             total_pages_num = total_pages.extract_first()

#             if total_pages_num:
#                 self.total_pages = int(total_pages_num)
#             else:
#                 self.logger.error('Impossible de trouver le nombre total de pages')
#                 return

#         brokers = response.xpath("//div[contains(@class, 'listing--bottomcta')]")
#         for broker in brokers:
#             partial_website_url = broker.xpath(".//li[@class='mlr__item mlr__item--website ']/a/@href").extract_first()
#             website_url = self.base_url + partial_website_url if partial_website_url else None

#             partial_listing_url = broker.xpath(".//div[@class='listing__title--wrap']/h3/a[@class='listing__name--link listing__link jsListingName']/@href").extract_first()
#             listing_url = self.base_url + partial_listing_url if partial_listing_url else None

#             yield {
#                 'title': broker.xpath(".//div[@class='listing__title--wrap']/h3/a[@class='listing__name--link listing__link jsListingName']/text()").extract_first(),
#                 # Continuer pour les autres champs d'adresse
#                 'phone': broker.xpath(".//a[@data-phone]/@data-phone").extract_first(),
#                 'street_address': broker.xpath("//span[@itemprop='address']/span[@itemprop='streetAddress']/text()").get(),
#                 'addressLocality': broker.xpath("//span[@itemprop='address']/span[@itemprop='addressLocality']/text()").get(),
#                 'addressRegion': broker.xpath("//span[@itemprop='address']/span[@itemprop='addressRegion']/text()").get(),
#                 'postalCode': broker.xpath("//span[@itemprop='address']/span[@itemprop='postalCode']/text()").get(),
#                 'website': website_url,
#                 'url': listing_url,
#             }

#         # Gestion de la pagination
#         if self.current_page < self.total_pages:
#             self.current_page += 1  # Passer à la page suivante
#             next_page_links = response.xpath("//div[@class='view_more_section_noScroll']//a/@href")
#             if next_page_links:
#                 next_page_url = next_page_links[-1].extract()
#                 if next_page_url:
#                     next_page_url = response.urljoin(next_page_url)
#                     yield scrapy.Request(next_page_url, callback=self.parse)

import scrapy

class PJSpider(scrapy.Spider):
    name = 'pj'
    start_urls = ['https://www.pagesjaunes.ca/search/si/1/hypoth%C3%A9caire/QC']
    base_url = "https://www.pagesjaunes.ca"
    total_pages = None
    seen_contacts = set()

    def parse(self, response):
        if self.total_pages is None:
            self.current_page = 1
            total_pages = response.xpath("(//div[@class='view_more_section_noScroll']//span[@class='pageCount']/span)[2]/text()")
            total_pages_num = total_pages.extract_first()
            if total_pages_num:
                self.total_pages = int(total_pages_num)
            else:
                self.logger.error('Impossible de trouver le nombre total de pages')
                return

        brokers = response.xpath("//div[contains(@class, 'listing--bottomcta')]")
        for broker in brokers:
            title = broker.xpath(".//div[@class='listing__title--wrap']/h3/a[@class='listing__name--link listing__link jsListingName']/text()").extract_first()
            phone = broker.xpath(".//a[@data-phone]/@data-phone").extract_first()
            addressLocality = broker.xpath(".//span[@itemprop='address']/span[@itemprop='addressLocality']/text()").extract_first()
            
            contact_id = (title, phone, addressLocality)
            if contact_id not in self.seen_contacts:
                self.seen_contacts.add(contact_id)
                partial_website_url = broker.xpath(".//li[@class='mlr__item mlr__item--website ']/a/@href").extract_first()
                website_url = self.base_url + partial_website_url if partial_website_url else None

                partial_listing_url = broker.xpath(".//div[@class='listing__title--wrap']/h3/a[@class='listing__name--link listing__link jsListingName']/@href").extract_first()
                listing_url = self.base_url + partial_listing_url if partial_listing_url else None

                yield {
                    'title': title,
                    'phone': phone,
                    'street_address': addressLocality,
                    'website': website_url,
                    'url': listing_url,
                    # Ajoutez d'autres champs si nécessaire
                }

        if self.current_page < self.total_pages:
            self.current_page += 1
            next_page_links = response.xpath("//div[@class='view_more_section_noScroll']//a/@href")
            if next_page_links:
                next_page_url = next_page_links[-1].extract()
                if next_page_url:
                    next_page_url = response.urljoin(next_page_url)
                    yield scrapy.Request(next_page_url, callback=self.parse)

