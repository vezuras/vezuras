from itemadapter import ItemAdapter
import json
import csv
from datetime import datetime
import atexit
import os

class VlivePipeline:
    def process_item(self, item, spider):
        return item

class JsonWriterPipeline:
    def __init__(self):
        self.items = {}
        self.start_time = None

    def open_spider(self, spider):
        self.spider_name = spider.name
        self.start_time = datetime.now().strftime("%Y-%m-%d")  # Initialiser self.start_time

        if self.spider_name in ["duproprio", "kijiji", "lespac", "publimaison", "logisqc", "annoncextra"]:
            file_name = f'avpp_{self.start_time}.json'
        elif self.spider_name == "centris":
            file_name = f'centris_{self.start_time}.json'
        else:
            file_name = f'{self.spider_name}_{self.start_time}.json'

        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as file:
                data = file.read()
                if data:
                    self.items = json.loads(data)
        else:
            self.items = {}

        atexit.register(self.close_json, file_name)

    def close_json(self, file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            json.dump(self.items, file, ensure_ascii=False)

    def close_spider(self, spider):
        atexit.unregister(self.close_json)

    def process_item(self, item, spider):
        item_data = dict(item)

        if self.spider_name in ["duproprio", "kijiji", "lespac", "publimaison", "logisqc", "annoncextra"]:
            if self.spider_name not in self.items:
                self.items[self.spider_name] = []  # Créez une liste vide avec le nom du spider comme clé
            self.items[self.spider_name].append(item_data)
        elif self.spider_name == "centris":
            if not any(item_data['full_address'] == json_item['full_address'] for json_item in self.items.get(self.spider_name, [])):
                if self.spider_name not in self.items:
                    self.items[self.spider_name] = []  # Créez une liste vide avec le nom du spider comme clé
                self.items[self.spider_name].append(item_data)
        else:
            if self.spider_name not in self.items:
                self.items[self.spider_name] = []  # Créez une liste vide avec le nom du spider comme clé
            self.items[self.spider_name].append(item_data)

        return item

class CsvWriterPipeline:
    def open_spider(self, spider):
        self.spider_name = spider.name
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f'{self.spider_name}_{current_time}.csv'
        self.file = open(file_name, 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=['source', 'category', 'price', 'street_address', 'locality', 'postal_code', 'latitude', 'longitude', 'telephone', 'description', 'image', 'url', 'sku', 'date', 'number_of_rooms', 'price_currency', 'address', 'title', 'site_name', 'country-name', 'image', 'type', 'latitude', 'longitude', 'locality', 'region', 'listingCategory', 'listingType', 'listingTag', 'city', 'advertiserType', 'adType', 'sellerType', 'constructionType', 'operationType', 'bedRooms', 'bathRooms', 'rooms', 'publicId', 'priceNote', 'year', 'publicationDate', 'publishedSinceMessage', 'condition', 'advertiserCommunicationCaptchaNeeded', 'zipCode', 'provinceState', 'country', 'geographicAreaLabel', 'detailUrl', 'printUrl', 'reportAdUrl', 'facebookShareUrl', 'twitterShareUrl', 'googleShareUrl', 'shareByEmailUrl', 'showWatermarkOnImages', 'roomInfo', 'visits', 'financialInfo', 'pictures', 'attributes', 'contacts', 'bellFibeFiberType', 'cogecoServiceable', 'rentalAccommodationInfoLink', 'hsbcCalculatorInfo', 'sold', 'phones'])

        self.writer.writeheader()

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        adapted_item = ItemAdapter(item)
        self.writer.writerow(adapted_item.asdict())
        return item
