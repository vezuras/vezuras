import scrapy
import json
from urllib.parse import urljoin


class PublimaisonSpider(scrapy.Spider):
    name = 'publimaison'
    start_urls = ['https://www.publimaison.ca/fr/annonce/394535/maison-a-etages-a-vendre-quebec-rive-nord']

    def parse(self, response):
        cookie_request_verification_token = response.headers.getlist('Set-Cookie')
        cookie_request_verification_token = cookie_request_verification_token[0].decode('utf-8') if cookie_request_verification_token else ''
        cookie_publimaisonalertelang = response.headers.getlist('Set-Cookie')
        cookie_publimaisonalertelang = cookie_publimaisonalertelang[1].decode('utf-8') if len(cookie_publimaisonalertelang) > 1 else ''
        request_verification_token = response.xpath('//input[@name="__RequestVerificationToken"]/@value').get()
        hash_value = response.xpath("//span[@class='telephone']/@data-url").get()

        # Construire les données pour la requête AJAX
        data = {
            '__RequestVerificationToken': request_verification_token,
            'hash': hash_value,
        }

        # Envoyer la requête AJAX avec les cookies inclus dans les headers
        ajax_url = 'https://www.publimaison.ca/StatCounter/Telephone'
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',  # Ajouter l'en-tête Content-Type
            'Cookie': f'{cookie_request_verification_token}; {cookie_publimaisonalertelang}'  # Inclure les cookies dans les headers de la requête
        }
        yield scrapy.FormRequest(
            url=ajax_url,
            method='POST',
            formdata=data,
            headers=headers,
            callback=self.parse_telephones
        )

    def parse_telephones(self, response):
        data = json.loads(response.text)
        phone_number = data.get("value")
        
        if phone_number:
            print("Phone number:", phone_number)
        else:
            print("No phone number found")
