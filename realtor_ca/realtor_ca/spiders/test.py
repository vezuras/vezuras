import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
import os


class Bot2Spider(scrapy.Spider):
    name = 'bot2'
    allowed_domains = ['www.centris.ca']

    position = {"startPosition": 0}
    annonce_count = 0
    increment_numer = 12
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)


    def start_requests(self):
        query = {
            "query":{
                "UseGeographyShapes":0,
                "Filters":[
                    
                ],
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
        #     "query": {
        #         "UseGeographyShapes": 0,
        #         "Filters": [],
        #         "FieldsValues": [
        #             {
        #                 "fieldId": "Category",
        #                 "value": "Residential",
        #                 "fieldConditionId": "",
        #                 "valueConditionId": ""
        #             },
        #             {
        #                 "fieldId": "SellingType",
        #                 "value": "Sale",
        #                 "fieldConditionId": "",
        #                 "valueConditionId": ""
        #             },
        #             {
        #                 "fieldId": "LandArea",
        #                 "value": "SquareFeet",
        #                 "fieldConditionId": "IsLandArea",
        #                 "valueConditionId": ""
        #             },
        #             {
        #                 "fieldId": "SalePrice",
        #                 "value": 0,
        #                 "fieldConditionId": "ForSale",
        #                 "valueConditionId": ""
        #             },
        #             {
        #                 "fieldId": "SalePrice",
        #                 "value": 999999999999,
        #                 "fieldConditionId": "ForSale",
        #                 "valueConditionId": ""
        #             }
        #         ]
        #     },
        #     "isHomePage": True
        # }
        yield scrapy.Request(
            url='https://www.centris.ca/property/UpdateQuery',
            method='POST',
            body=json.dumps(query),
            headers={'Content-Type': 'application/json'},
            callback=self.update_query
        )


    def update_query(self, response):
        yield scrapy.Request(
            url='https://www.centris.ca/Property/GetInscriptions',
            method='POST',
            body=json.dumps(self.position),
            headers={
                'Content-Type': 'application/json'
            },
            callback=self.parse
        )


    def parse(self, response):
        resp_dict = json.loads(response.body)
        html = resp_dict.get('d').get('Result').get('html')
        parse_html = Selector(text=html)
        listings = parse_html.xpath("//div[@itemtype='http://schema.org/Product']")
        for listing in listings:
            price = listing.xpath(".//div[@class='price']/span/text()").get()
            price = price.strip()
            category = listing.xpath(".//span[@itemprop='category']/div/text()").get()
            category = category.strip()
            address = listing.xpath(".//span[@class='address']/div/text()").getall()
            url = listing.xpath(".//a[@class='a-more-detail']/@href").get()
            url_en = listing.xpath(".//a[@class='a-more-detail']/@href").get()
            url_fr = url.replace("/en", "/fr")

            yield scrapy.Request(
                url=response.urljoin(url),
                callback=self.parse_summary,
                meta={
                    'category': category,
                    'price': price,
                    'address': address,
                    'url': response.urljoin(url_en)
                }
            )

        # count = resp_dict.get('d').get('Result').get('count')

        # if self.position['startPosition'] <= count:
        #     self.position['startPosition'] += self.increment_numer
        #     yield scrapy.Request(
        #         url='https://www.centris.ca/Property/GetInscriptions',
        #         method='POST',
        #         body=json.dumps(self.position),
        #         headers={
        #             'Content-Type': 'application/json'
        #         },
        #         callback=self.parse
        #     )


    def parse_summary(self, response):
        url = response.meta.get('url')
        self.annonce_count += 1
        category = response.xpath("//span[@data-id='PageTitle']/text()").get()
        price = response.xpath("//span[@id='BuyPrice']/text()").get()
        address = response.xpath("//h2[@itemprop='address']/text()").get()
        latitude = response.xpath("//meta[@itemprop='latitude']/@content").get()
        longitude = response.xpath("//meta[@itemprop='longitude']/@content").get()
        yield {
            'id': self.annonce_count,
            'category':"",
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
