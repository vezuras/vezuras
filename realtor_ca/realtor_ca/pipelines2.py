from itemadapter import ItemAdapter
import json
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

        self.file_name_avpp = f'avpp_{self.start_time}.json'
        self.file_name_spider = f'{self.spider_name}_{self.start_time}.json'

        if os.path.exists(self.file_name_avpp):
            with open(self.file_name_avpp, 'r', encoding='utf-8') as file:
                data = file.read()
                if data:
                    self.items = json.loads(data)
        else:
            self.items = {}

        atexit.register(self.close_json)

    def close_json(self):
        with open(self.file_name_avpp, 'w', encoding='utf-8') as file_avpp:
            json.dump(self.items, file_avpp, ensure_ascii=False)

        with open(self.file_name_spider, 'w', encoding='utf-8') as file_spider:
            spider_data = self.items.get(self.spider_name, [])
            json.dump(spider_data, file_spider, ensure_ascii=False)

    def close_spider(self, spider):
        atexit.unregister(self.close_json)

    def process_item(self, item, spider):
        item_data = dict(item)

        if self.spider_name not in self.items:
            self.items[self.spider_name] = []  # Créez une liste vide avec le nom du spider comme clé

        self.items[self.spider_name].append(item_data)

        return item
