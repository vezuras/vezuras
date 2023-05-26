import scrapy
from bs4 import BeautifulSoup

class KIJIJISpider(scrapy.Spider):
    name = 'KIJIJI'
    start_urls = ['https://www.kijiji.ca/b-a-vendre/quebec/page-{}/c30353001l9001']
    # custom_settings = {'CLOSESPIDER_PAGECOUNT': 200}

    def __init__(self, *args, **kwargs):
        super(KIJIJISpider, self).__init__(*args, **kwargs)
        self.data = []
        self.items_processed = 0

    def start_requests(self):
        page_number = 1
        yield scrapy.Request(url=self.start_urls[0].format(page_number), callback=self.parse, meta={'page_number': page_number})

    def parse(self, response):
        page_number = response.meta['page_number']
        vip_urls = response.css('.search-item[data-vip-url]::attr(data-vip-url)').getall()
        self.items_processed = 0
        for url in vip_urls:
            full_url = 'https://www.kijiji.ca' + url
            yield scrapy.Request(url=full_url, callback=self.parse_summary_page, meta={'page_number': page_number})

        # Pagination
        next_page_number = page_number + 1
        next_page_url = self.start_urls[0].format(next_page_number)
        yield scrapy.Request(url=next_page_url, callback=self.parse, meta={'page_number': next_page_number})

    def parse_summary_page(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        meta_elements = soup.find_all('meta')
        addresses = response.xpath("//span[@itemprop='address']/text()").get()
        price = response.xpath("//span[@class='currentPrice-2842943473']/span/text()").get()
        extracted_data = {}

        for meta_element in meta_elements:
            property_name = meta_element.get('property')
            content = meta_element.get('content')
            if property_name and content:
                if property_name.startswith('og:'):
                    property_name = property_name[3:]
                extracted_data[property_name] = content

        extracted_data['address'] = addresses
        extracted_data['price'] = price

        if extracted_data.get('title') and extracted_data.get('description'):
            yield extracted_data
        else:
            self.logger.warning(f"Invalid data on page: {response.url}")

        self.items_processed += 1

        if self.items_processed == len(response.css('.search-item[data-vip-url]::attr(data-vip-url)')):
            page_number = response.meta['page_number']
            next_page_number = page_number + 1
            next_page_url = self.start_urls[0].format(next_page_number)
            yield scrapy.Request(url=next_page_url, callback=self.parse_summary_page, meta={'page_number': next_page_number})
