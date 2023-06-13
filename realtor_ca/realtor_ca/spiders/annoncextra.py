import scrapy
from datetime import datetime
import re

class AnnoncextraSpider(scrapy.Spider):
    name = 'annoncextra'
    allowed_domains = ['annoncextra.com']
    sous_categories = [43, 42, 41, 40, 39]
    current_sous_categorie_index = 0

    def start_requests(self):
        yield scrapy.Request(
            url=self.get_search_url(),
            callback=self.parse_listings
        )

    def get_search_url(self):
        sous_categorie = self.sous_categories[self.current_sous_categorie_index]
        return f"https://www.annoncextra.com/ad_search.php?search=1&offset=0&ad_category=4&ad_year[]=0&ad_year[]=0&ad_price[]=0&ad_price[]=0&ad_sub_category={sous_categorie}&ad_sub_type=0&usr_account_type=&usr_region[]=0&#frmLogin"

    def parse_listings(self, response):
        sous_categorie = self.sous_categories[self.current_sous_categorie_index]
        for listing in response.xpath("//div[@class='col-lg-12 col-md-12 col-sm-12 col-xs-12 back_annonce_list3 padding-bottom-xs ']"):
            title = listing.xpath("normalize-space(.//a/@title)").get()
            representative = listing.xpath("normalize-space(.//div[@class='col-lg-6 col-md-8 col-sm-6 col-xs-9']/span[1]/text())").get()
            delay = listing.xpath("normalize-space(.//div[@class='col-lg-6 col-md-8 col-sm-6 col-xs-9']/span[3]/text())").get()
            price = listing.xpath("normalize-space(.//div[@class='prix_position col-lg-6 col-md-4 col-xs-3']//b/text())").get()
            image = listing.xpath("normalize-space(.//img[@style='max-width: 133px; max-height: 100px; position: relative;']/@src)").getall()
            description = listing.xpath("normalize-space(.//div[@class='col-lg-12 col-md-12 col-sm-12 hidden-xs description-md']/text())").get()
            region = listing.xpath("normalize-space(.//div[@class='col-lg-9 col-sm-12 hidden-xs hidden-md']/a[2]/text())").get()
            code_annoncextra = listing.xpath("normalize-space(.//div[@class='col-lg-9 col-md-8 col-sm-9 col-xs-8']/a[1]/text())").get()
            categorie = listing.xpath("normalize-space(.//div[@class='col-lg-9 col-md-8 col-sm-9 col-xs-8']/a[3]/text())").get()
            link = listing.xpath(".//div[@class='col-lg-3 col-md-4 col-sm-3 hidden-xs']/a/@href").get()
            phone_element = listing.xpath(".//a[@id='phone_button']")
            phone_number = None
            if phone_element:
                onclick_value = phone_element[0].get('onclick')
                if onclick_value:
                    match = re.search(r"\('([^']+)'", onclick_value)
                    if match:
                        phone_number = match.group(1)


            extracted_data = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'source': self.name,
                'category': categorie.replace('Vente - ', '').strip(),
                'price': price,
                'address': {
                    'region': region,
                },
                'phone': phone_number,
                'description': description,
                'url': link,
                'sku': f"{self.name}-{code_annoncextra.replace('#', '')}",
            }
            yield extracted_data

        BUTTON_NEXT = response.xpath("//*[contains(text(),'Suivante')]/@href").get()
        if BUTTON_NEXT:
            yield scrapy.Request(url=BUTTON_NEXT, callback=self.parse_listings)
        else:
            self.current_sous_categorie_index += 1
            if self.current_sous_categorie_index < len(self.sous_categories):
                yield scrapy.Request(url=self.get_search_url(), callback=self.parse_listings)
