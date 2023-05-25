# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import csv
from datetime import datetime

class VlivePipeline:
    def process_item(self, item, spider):
        return item

class JsonWriterPipeline:
    def open_spider(self, spider):
        self.spider_name = spider.name
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f'{self.spider_name}_{current_time}.json'
        self.file = open(file_name, 'w', encoding='utf-8')
        self.file.write('[')

    def close_spider(self, spider):
        self.file.write(']')  # Fermer la liste JSON
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + ",\n"
        self.file.write(line)
        return item


class CsvWriterPipeline:
    def open_spider(self, spider):
        self.spider_name = spider.name
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f'{self.spider_name}_{current_time}.csv'
        self.file = open(file_name, 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames = ['source', 'category', 'price', 'street_address', 'locality', 'postal_code', 'latitude', 'longitude', 'telephone', 'description', 'images', 'url', 'duproprio_id'])
        self.writer.writeheader()

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        self.writer.writerow(item)
        return item
