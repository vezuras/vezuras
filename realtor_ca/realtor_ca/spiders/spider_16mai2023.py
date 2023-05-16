import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
import os
from concurrent.futures import ThreadPoolExecutor


class Bot2Spider(scrapy.Spider):
    name = 'bot2'
    allowed_domains = ['www.centris.ca']
    webstite_url = ['https://www.centris.ca']
    position = {"startPosition": 0}
    annonce_count = 0
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)


    def start_requests(self):
        yield scrapy.Request(
            url='https://www.centris.ca/UserContext/Lock',
            method='POST',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/json'
            },
            body=json.dumps({'uc': 0}),
            callback=self.generate_uck_SingleFamilyHome,
            dont_filter=True) # ajout de l'option dont_filter pour ne pas filtrer les requêtes
        

    def generate_uck_SingleFamilyHome(self, response):
            uck = response.body
            query = {
                "query":{
                    "UseGeographyShapes":0,
                    "Filters":[],
                    "FieldsValues":[
                        {
                            "fieldId":"PropertyType",
                            "value":"SingleFamilyHome",
                            "fieldConditionId":"",
                            "valueConditionId":"IsResidential"
                        },
                        {
                            "fieldId":"Category",
                            "value":"Residential",
                            "fieldConditionId":"",
                            "valueConditionId":""
                        },
                        {
                            "fieldId":"SellingType",
                            "value":"Sale",
                            "fieldConditionId":"",
                            "valueConditionId":""
                        },
                        {
                            "fieldId":"LandArea",
                            "value":"SquareFeet",
                            "fieldConditionId":"IsLandArea",
                            "valueConditionId":""
                        },
                        {
                            "fieldId":"SalePrice",
                            "value":0,
                            "fieldConditionId":"ForSale",
                            "valueConditionId":""
                        },
                        {
                            "fieldId":"SalePrice",
                            "value":999999999999,
                            "fieldConditionId":"ForSale",
                            "valueConditionId":""
                        }
                    ]
                },
                "isHomePage":True
            }
            yield scrapy.Request(
                url="https://www.centris.ca/property/UpdateQuery",
                method="POST",
                body=json.dumps(query),
                headers={
                    'Content-Type': 'application/json',
                    'x-requested-with': 'XMLHttpRequest',
                    'x-centris-uc': 0,
                    'x-centris-uck': uck
                },
                callback=self.update_query_SingleFamilyHome,
                dont_filter=True) # ajout de l'option dont_filter pour ne pas filtrer les requêtes
            

    def update_query_SingleFamilyHome(self,response):
        yield scrapy.Request(
            url="https://www.centris.ca/Property/GetInscriptions",
            method="POST",
            body=json.dumps(self.position),
            headers={'Content-Type': 'application/json'},
            callback=self.parse_SingleFamilyHome,
            dont_filter=True) # ajout de l'option dont_filter pour ne pas filtrer les requêtes


    def parse_SingleFamilyHome(self, response):
        resp_dict = json.loads(response.body)
        html = resp_dict.get('d').get('Result').get('html')
        parse_html = Selector(text=html)
        listings = parse_html.xpath("//div[@itemtype='http://schema.org/Product']")

        # Utilisation du multi-threading pour exécuter les requêtes en parallèle
        with ThreadPoolExecutor() as executor:
            futures = []
            for listing in listings:
                future = executor.submit(self.parse_listing, self.webstite_url, listing)
                futures.append(future)

            for future in futures:
                results = future.result()
                for result in results:
                    yield result

        count = resp_dict.get('d').get('Result').get('count')
        increment_number = resp_dict.get('d').get('Result').get('inscNumberPerPage')
        if self.position['startPosition'] <= count:
            self.position['startPosition'] += increment_number
            yield scrapy.Request(
                url='https://www.centris.ca/Property/GetInscriptions',
                method='POST',
                body=json.dumps(self.position),
                headers={
                    'Content-Type': 'application/json'
                },
                callback=self.parse_SingleFamilyHome,
                dont_filter=True
            )

            count = resp_dict.get('d').get('Result').get('count')
            increment_number = resp_dict.get('d').get('Result').get('inscNumberPerPage')
            if self.position['startPosition'] <= count:
                self.position['startPosition'] += increment_number
                yield scrapy.Request(
                    url='https://www.centris.ca/Property/GetInscriptions',
                    method='POST',
                    body=json.dumps(self.position),
                    headers={
                        'Content-Type': 'application/json'
                    },
                    callback=self.parse_SingleFamilyHome,
                    # dont_filter=True # ajout de l'option dont_filter pour ne pas filtrer les requêtes
                )


    def parse_listing(self, base_url, listing):
        results = []
        price = listing.xpath(".//div[@class='price']/span/text()").get()
        price = price.strip()
        category = listing.xpath(".//span[@itemprop='category']/div/text()").get()
        category = category.strip()
        address = listing.xpath(".//span[@class='address']/div/text()").getall()
        url = listing.xpath(".//a[@class='a-more-detail']/@href").get()
        url_en = listing.xpath(".//a[@class='a-more-detail']/@href").get()
        url_fr = url.replace("/en", "/fr")
        absolute_url = base_url[0] + url_en
        absolute_url_fr = base_url[0] + url_fr

        response = yield scrapy.Request(
            url=absolute_url_fr,
            callback=self.parse_summary,
            meta={
                'category': category,
                'price': price,
                'address': address,
                'url': absolute_url_fr
            },
        )

        results.append(response)
        return results


    def parse_summary(self, response):
        url = response.meta.get('url')
        self.annonce_count += 1
        category = response.xpath("//span[@data-id='PageTitle']/text()").get()
        price = response.xpath("//span[@id='BuyPrice']/text()").get()
        address = response.xpath("//h2[@itemprop='address']/text()").get()
        latitude = response.xpath("//meta[@itemprop='latitude']/@content").get()
        longitude = response.xpath("//meta[@itemprop='longitude']/@content").get()
        yield {
            # 'id': self.annonce_count,
            # 'category': "",
            'title': category,
            'price': price,
            'address': address,
            'latitude': latitude,
            'longitude': longitude,
            'url': url
        }


    def closed(self, reason):
        self.driver.quit()
        print('Spider closed: ', reason)
