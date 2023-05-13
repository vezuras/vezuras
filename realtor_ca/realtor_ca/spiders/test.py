import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import json
from joblib import dump, load
import os


class CentrisSpider(scrapy.Spider):
    name = 'test'
    allowed_domains = ['www.centris.ca']

    position = {"startPosition": 0}
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    def save_state(self):
           dump(self.position, "position.joblib")


    def start_requests(self):
        try:
            self.position = load("position.joblib")
        except FileNotFoundError:
            pass

        query = {
            "query": {
                "UseGeographyShapes": 0,
                "Filters": [],
                "FieldsValues": [
                    {
                        "fieldId": "Category",
                        "value": "Residential",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "SellingType",
                        "value": "Sale",
                        "fieldConditionId": "",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "LandArea",
                        "value": "SquareFeet",
                        "fieldConditionId": "IsLandArea",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "SalePrice",
                        "value": 0,
                        "fieldConditionId": "ForSale",
                        "valueConditionId": ""
                    },
                    {
                        "fieldId": "SalePrice",
                        "value": 999999999999,
                        "fieldConditionId": "ForSale",
                        "valueConditionId": ""
                    }
                ]
            },
            "isHomePage": True
        }
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

            yield scrapy.Request(
                url=response.urljoin(url),
                callback=self.parse_summary,
                meta={
                    'category': category,
                    'price': price,
                    'address': address,
                    'url': response.urljoin(url)
                }
            )

        count = resp_dict.get('d').get('Result').get('count')
        increment_numer = resp_dict.get('d').get('Result').get('inscNumberPerPage')

        if self.position['startPosition'] <= count:
            self.position['startPosition'] += increment_numer
            self.save_state()
            yield scrapy.Request(
                url='https://www.centris.ca/Property/GetInscriptions',
                method='POST',
                body=json.dumps(self.position),
                headers={
                    'Content-Type': 'application/json'
                },
                callback=self.parse
            )


    def parse_summary(self, response):
        category = response.xpath("//span[@data-id='PageTitle']/text()").get()
        price = response.xpath("//span[@id='BuyPrice']/text()").get()
        address = response.xpath("//h2[@itemprop='address']/text()").get()
        latitude = response.xpath("//meta[@itemprop='latitude']/@content").get()
        longitude = response.xpath("//meta[@itemprop='longitude']/@content").get()
        yield {
            'category': category,
            'price': price,
            'address': address,
            'latitude': latitude,
            'longitude': longitude,
            }
        self.save_state()

    def closed(self, reason):
        self.driver.quit()
        try:
           os.remove("position.joblib")
        except FileNotFoundError:
            pass

