from itemadapter import ItemAdapter
from pymongo import MongoClient
import json
import os
import atexit
from datetime import datetime

class JsonWriterPipeline:
    def __init__(self):
        self.items = {}
        self.avpp_items = {}
        self.centris_items = {}
        self.start_time = None

    def open_spider(self, spider):
        self.spider_name = spider.name
        self.start_time = datetime.now()  # Initialise self.start_time

        self.file_name = f'{self.spider_name}_{self.start_time.strftime("%Y-%m-%d_%H-%M")}.json'

        if self.spider_name in ["duproprio", "kijiji", "lespac", "publimaison", "logisqc", "annoncextra"]:
            self.file_name_avpp = f'avpp_{self.start_time.strftime("%Y-%m-%d")}.json'
        else:
            self.file_name_avpp = None
            self.file_name = f'centris_{self.start_time.strftime("%Y-%m-%d")}.json'
        
        self.file_name_centris = f'centris_{self.start_time.strftime("%Y-%m-%d")}.json'
        
        self.load_data()

        atexit.register(self.close_json)

    def load_data(self):
        self.items = {}
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r', encoding='utf-8') as file:
                data = file.read()
                if data:
                    self.items = json.loads(data)

        if self.file_name_avpp is not None and os.path.exists(self.file_name_avpp):
            with open(self.file_name_avpp, 'r', encoding='utf-8') as file_avpp:
                data_avpp = file_avpp.read()
                if data_avpp:
                    self.avpp_items = json.loads(data_avpp)

        if os.path.exists(self.file_name_centris):
            with open(self.file_name_centris, 'r', encoding='utf-8') as file_centris:
                data_centris = file_centris.read()
                if data_centris:
                    self.centris_items = json.loads(data_centris)

    def close_json(self):
        if self.file_name_avpp is not None:
            with open(self.file_name_avpp, 'w', encoding='utf-8') as file_avpp:
                self.avpp_items[self.spider_name] = self.items.get(self.spider_name, [])
                json.dump(self.avpp_items, file_avpp, ensure_ascii=False)

        if self.file_name is not None:
            with open(self.file_name, 'w', encoding='utf-8') as file:
                json.dump(self.items, file, ensure_ascii=False)

    def close_spider(self, spider):
        atexit.unregister(self.close_json)
        self.flush_json()

    def flush_json(self):
        if self.file_name_avpp is not None:
            with open(self.file_name_avpp, 'w', encoding='utf-8') as file_avpp:
                self.avpp_items[self.spider_name] = self.items.get(self.spider_name, [])
                json.dump(self.avpp_items, file_avpp, ensure_ascii=False)

        if self.file_name is not None:
            with open(self.file_name, 'w', encoding='utf-8') as file:
                json.dump(self.items, file, ensure_ascii=False)

    def process_item(self, item, spider):
        item_data = dict(item)

        if self.spider_name not in self.items:
            self.items[self.spider_name] = []

        if not self.is_duplicate(item_data):
            if not self.is_centris_duplicate(item_data):
                if 'phone' in item_data:
                    item_data['phone'] = self.format_phone(item_data['phone'])
                if 'price' in item_data:
                    item_data['price'] = PriceFormatter.normalize_price(item_data['price'])
                self.items[self.spider_name].append(item_data)

        return item

    def is_duplicate(self, item_data):
        for spider_name, items in self.items.items():
            if spider_name != self.spider_name:
                for item in items:
                    if item.get('url') == item_data.get('url'):
                        return True
            else:
                for existing_item in items:
                    if existing_item.get('url') == item_data.get('url'):
                        return True
        return False

    def is_centris_duplicate(self, item_data):
        for centris_items in self.centris_items.values():
            for centris_item in centris_items:
                centris_latitude = centris_item.get('latitude')[:7] if centris_item.get('latitude') else None
                centris_longitude = centris_item.get('longitude')[:7] if centris_item.get('longitude') else None
                item_latitude = item_data.get('latitude')[:7] if item_data.get('latitude') else None
                item_longitude = item_data.get('longitude')[:7] if item_data.get('longitude') else None

                if (
                    centris_latitude == item_latitude and
                    centris_longitude == item_longitude
                ):
                    return True

        return False

    def format_phone(self, phone):
        formatted_phones = []
        if phone is not None:
            for phone_number in phone:
                cleaned_phone_number = ''.join(filter(str.isdigit, phone_number))
                if len(cleaned_phone_number) == 11:
                    formatted_phone = f"{cleaned_phone_number[1:4]}-{cleaned_phone_number[4:7]}-{cleaned_phone_number[7:]}"
                else:
                    formatted_phone = f"{cleaned_phone_number[:3]}-{cleaned_phone_number[3:6]}-{cleaned_phone_number[6:]}"
                formatted_phones.append(f'+1-{formatted_phone}')
        return formatted_phones


class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.items = {}
        self.avpp_items = {}
        self.centris_items = {}
        self.start_time = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        mongo_uri = crawler.settings.get('MONGO_URI')
        mongo_db = crawler.settings.get('MONGO_DATABASE')
        print(f"MONGO_URI: {mongo_uri}")
        print(f"MONGO_DATABASE: {mongo_db}")
        return cls(mongo_uri=mongo_uri, mongo_db=mongo_db)

    def open_spider(self, spider):
        self.spider_name = spider.name
        self.start_time = datetime.now()

        self.collection_name = f'{self.spider_name}_{self.start_time.strftime("%Y-%m-%d_%H-%M")}'
        self.avpp_collection_name = f'avpp_{self.start_time.strftime("%Y-%m-%d")}'
        self.centris_collection_name = f'centris_{self.start_time.strftime("%Y-%m-%d")}'

        self.load_data()

        atexit.register(self.close_mongodb)

        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def load_data(self):
        if self.db is not None:
            if self.collection_name in self.db.list_collection_names():
                self.items = self.db[self.collection_name].find_one() or {}

            if self.avpp_collection_name in self.db.list_collection_names():
                self.avpp_items = self.db[self.avpp_collection_name].find_one() or {}

            if self.centris_collection_name in self.db.list_collection_names():
                self.centris_items = self.db[self.centris_collection_name].find_one() or {}

    def close_mongodb(self):
        self.save_data()
        self.client.close()

    def save_data(self):
        if self.avpp_collection_name:
            old_items = self.db[self.avpp_collection_name].find_one() or {}
            old_spider_items = old_items.get(self.spider_name, [])
            new_spider_items = self.items.get(self.spider_name, [])
            updated_spider_items = old_spider_items + new_spider_items
            updated_spider_items = list({item['url']: item for item in updated_spider_items}.values())
            old_items[self.spider_name] = updated_spider_items
            self.db[self.avpp_collection_name].replace_one({}, old_items, upsert=True)

    def close_spider(self, spider):
        atexit.unregister(self.close_mongodb)
        if self.db is not None:
            self.save_data()

    def process_item(self, item, spider):
        item_data = ItemAdapter(item).asdict()

        if self.spider_name not in self.items:
            self.items[self.spider_name] = []

        if not self.is_duplicate(item_data):
            if not self.is_centris_duplicate(item_data):
                if 'phone' in item_data:
                    item_data['phone'] = self.format_phone(item_data['phone'])
                if 'price' in item_data:
                    item_data['price'] = self.normalize_price(item_data['price'])
                self.items[self.spider_name].append(item_data)

        return item

    def is_duplicate(self, item_data):
        for spider_name, items in self.items.items():
            if spider_name != self.spider_name:
                for item in items:
                    if item.get('url') == item_data.get('url'):
                        return True
            else:
                for existing_item in items:
                    if existing_item.get('url') == item_data.get('url'):
                        return True
        return False

    def is_centris_duplicate(self, item_data):
        for centris_items in self.centris_items.values():
            for centris_item in centris_items:
                centris_latitude = centris_item.get('latitude')[:7] if centris_item.get('latitude') else None
                centris_longitude = centris_item.get('longitude')[:7] if centris_item.get('longitude') else None
                item_latitude = item_data.get('latitude')[:7] if item_data.get('latitude') else None
                item_longitude = item_data.get('longitude')[:7] if item_data.get('longitude') else None

                if (
                    centris_latitude == item_latitude and
                    centris_longitude == item_longitude
                ):
                    return True

        return False

    def format_phone(self, phone):
        formatted_phones = []
        if phone is not None:
            for phone_number in phone:
                cleaned_phone_number = ''.join(filter(str.isdigit, phone_number))
                if len(cleaned_phone_number) == 11:
                    formatted_phone = f"{cleaned_phone_number[1:4]}-{cleaned_phone_number[4:7]}-{cleaned_phone_number[7:]}"
                else:
                    formatted_phone = f"{cleaned_phone_number[:3]}-{cleaned_phone_number[3:6]}-{cleaned_phone_number[6:]}"
                formatted_phones.append(f'+1-{formatted_phone}')
        return formatted_phones

    @staticmethod
    def normalize_price(price):
        numeric_part = ''.join(filter(str.isdigit, price))
        formatted_price = '{:,}'.format(int(numeric_part))
        formatted_price = formatted_price.replace(',', ' ')
        formatted_price += ' $'
        return formatted_price


class PriceFormatter:
    @staticmethod
    def normalize_price(price):
        # Supprimer tous les caractères non numériques
        numeric_part = ''.join(filter(str.isdigit, price))

        # Formater le prix avec des espaces
        formatted_price = '{:,}'.format(int(numeric_part))

        # Remplacer la virgule par un espace
        formatted_price = formatted_price.replace(',', ' ')

        # Ajouter le symbole du dollar canadien
        formatted_price += ' $'

        return formatted_price
