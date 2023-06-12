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
        self.avpp_items = {}
        self.start_time = None

    def open_spider(self, spider):
        self.spider_name = spider.name
        self.start_time = datetime.now().strftime("%Y-%m-%d")  # Initialiser self.start_time

        self.file_name = f'{self.spider_name}_{self.start_time}.json'

        if self.spider_name in ["duproprio", "kijiji", "lespac", "publimaison", "logisqc", "annoncextra"]:
            self.file_name_avpp = f'avpp_{self.start_time}.json'
        else:
            self.file_name_avpp = None

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

    def process_item(self, item, spider):
        item_data = dict(item)

        if self.spider_name not in self.items:
            self.items[self.spider_name] = []

        if not self.is_duplicate(item_data):
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
