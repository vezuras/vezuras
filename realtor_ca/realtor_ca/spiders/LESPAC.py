import scrapy
import json

class LESPACSpider(scrapy.Spider):
    name = 'lespac'
    start_url = 'https://immoapi.lespac.com/v1/buildings/list'

    query = {
        "adType":0,
        "advertiserType":0,
        "bathRooms":0,
        "bedRooms":0,
        "constructionType":0,
        "listingBuildingTypeIds":[0],
        "listingCategoryId":0,
        "listingFeatureIds":[],
        "listingFurnitureIds":[],
        "listingTagIds":[],
        "listingTypeIds":[],
        "maximumPrice":-1,
        "maximumYear":-1,
        "minimumPrice":0,
        "minimumYear":0,
        "operationType":0,
        "petsAllowed":"false",
        "publishedSince":0,
        "rooms":0,
        "sellerType":0,
        "description":"true",
        "offset":0,
        "limit":20,
        "visitDate":"null",
        "sortType":"recent"
        }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url,
            method='POST',
            headers={
                'content-type': 'application/json;charset=UTF-8'
            },
            body=json.dumps(self.query),
            callback=self.parse,
        )

    def parse(self, response):
        jsonresponse = json.loads(response.body)
        buildings = jsonresponse.get("buildings")
        if buildings:
            for building in buildings:
                url = building.get("url")
                if url:
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse_building
                    )

            total_buildings = jsonresponse.get("total")
            current_offset = self.query["offset"]
            limit = self.query["limit"]

            if current_offset + limit < total_buildings:
                new_offset = current_offset + limit
                self.query["offset"] = new_offset
                yield scrapy.Request(
                    url=self.start_url,
                    method='POST',
                    headers={
                        'content-type': 'application/json;charset=UTF-8'
                    },
                    body=json.dumps(self.query),
                    callback=self.parse
                )

    def parse_building(self, response):
        print(f'url: {response.url}')

        # Construction de l'URL de la page de détail
        public_id = response.url.split("/")[-1].split("-")[-1]  # Extraction du publicId de l'URL
        detail_url = f'https://immoapi.lespac.com/v1/buildings/{public_id}/detail'
        print(f'Detail URL: {detail_url}')
        yield scrapy.Request(
            url=detail_url,
            callback=self.parse_detail,
            meta={'public_id': public_id}
        )

    def parse_detail(self, response):
        public_id = response.meta.get('public_id')
        print(f'Phones URL: {response.url}')

        data = json.loads(response.body)
        extracted_data = self.extract_values(data)

        # Construction de l'URL de la page 'phones'
        contacts = extracted_data.get('contacts')
        if contacts:
            contact_id = contacts[0].get('id')
            phones_url = f'https://immoapi.lespac.com/v1/buildings/{public_id}/contacts/{contact_id}/phones'
            print(f'Phones URL: {phones_url}')
            yield scrapy.Request(
                url=phones_url,
                callback=self.parse_phones,
                meta={'extracted_data': extracted_data}
            )

    def parse_phones(self, response):
        phones_data = json.loads(response.body)
        extracted_phones = []
        for phone in phones_data:
            phone_number_type = phone.get('phoneNumberType')
            phone_number = phone.get('phoneNumber')

            extracted_phones.append({
                'phoneNumberType': phone_number_type,
                'phoneNumber': phone_number
            })

        extracted_data = response.meta.get('extracted_data')
        extracted_data['phones'] = extracted_phones
        yield extracted_data

    def extract_values(self, data):
        extracted_data = {}
        if isinstance(data, dict):
            for key, value in data.items():
                extracted_data[key] = self.extract_values(value)
        elif isinstance(data, list):
            extracted_data = [self.extract_values(item) for item in data]
        else:
            extracted_data = data
        return extracted_data
