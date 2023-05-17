# j'aimerais que tu m'explique comment structurer mon code python en scrapy avec selenium pour gratter le site (www.centris.ca) en requetant les page ajax dans l'ordre naturel d'un utilsateur régulier souhaitant gratter des catégories spécifiques. commences par aller sur le site et tester en temps réel le processus et qu'ensuite tu me partage un dbut de code qui requete les différentes pages ajax

# Voici les pages Fetch/XHR en ordre d'affichage
# 1. https://www.centris.ca/UserContext/UnLock
# ({"uc":0,"uck":"3518f693-6568-4488-9517-a43bdd6e88a8"})

# 2.  https://www.centris.ca/UserContext/Lock
# ({"uc":0})

# 3. https://www.centris.ca/property/GetPropertyCount
# ({"UseGeographyShapes":0,"Filters":[],"FieldsValues":[{"fieldId":"PropertyType","value":"SingleFamilyHome","fieldConditionId":"","valueConditionId":"IsResidential"},{"fieldId":"Category","value":"Residential","fieldConditionId":"","valueConditionId":""},{"fieldId":"SellingType","value":"Sale","fieldConditionId":"","valueConditionId":""},{"fieldId":"LandArea","value":"SquareFeet","fieldConditionId":"IsLandArea","valueConditionId":""},{"fieldId":"SalePrice","value":0,"fieldConditionId":"ForSale","valueConditionId":""},{"fieldId":"SalePrice","value":999999999999,"fieldConditionId":"ForSale","valueConditionId":""}]})

# 4. https://www.centris.ca/property/GetFilters
# ({"UseGeographyShapes":0,"Filters":[],"FieldsValues":[{"fieldId":"PropertyType","value":"SingleFamilyHome","fieldConditionId":"","valueConditionId":"IsResidential"},{"fieldId":"Category","value":"Residential","fieldConditionId":"","valueConditionId":""},{"fieldId":"SellingType","value":"Sale","fieldConditionId":"","valueConditionId":""},{"fieldId":"LandArea","value":"SquareFeet","fieldConditionId":"IsLandArea","valueConditionId":""},{"fieldId":"SalePrice","value":0,"fieldConditionId":"ForSale","valueConditionId":""},{"fieldId":"SalePrice","value":999999999999,"fieldConditionId":"ForSale","valueConditionId":""}]})

# 5. https://www.centris.ca/UserContext/UnLock
# ({"uc":0,"uck":"4303b72e-11c4-47ce-b569-740e4b7c8043"})

# 6. https://www.centris.ca/property/GetPropertyCount
# ({"UseGeographyShapes":0,"Filters":[],"FieldsValues":[{"fieldId":"PropertyType","value":"SingleFamilyHome","fieldConditionId":"","valueConditionId":"IsResidential"},{"fieldId":"Category","value":"Residential","fieldConditionId":"","valueConditionId":""},{"fieldId":"SellingType","value":"Sale","fieldConditionId":"","valueConditionId":""},{"fieldId":"LandArea","value":"SquareFeet","fieldConditionId":"IsLandArea","valueConditionId":""},{"fieldId":"SalePrice","value":0,"fieldConditionId":"ForSale","valueConditionId":""},{"fieldId":"SalePrice","value":999999999999,"fieldConditionId":"ForSale","valueConditionId":""}]})

# 7. https://www.centris.ca/property/UpdateQuery
# ({"query":{"UseGeographyShapes":0,"Filters":[],"FieldsValues":[{"fieldId":"PropertyType","value":"SingleFamilyHome","fieldConditionId":"","valueConditionId":"IsResidential"},{"fieldId":"Category","value":"Residential","fieldConditionId":"","valueConditionId":""},{"fieldId":"SellingType","value":"Sale","fieldConditionId":"","valueConditionId":""},{"fieldId":"LandArea","value":"SquareFeet","fieldConditionId":"IsLandArea","valueConditionId":""},{"fieldId":"SalePrice","value":0,"fieldConditionId":"ForSale","valueConditionId":""},{"fieldId":"SalePrice","value":999999999999,"fieldConditionId":"ForSale","valueConditionId":""}]},"isHomePage":true})

# 8. https://www.centris.ca/Property/GetInscriptions
# ({"startPosition":12})




# Voici un exemple de code pour gratter le site Centris.ca avec Selenium et Scrapy:

# import scrapy
# from selenium import webdriver


import scrapy
import json

class Bot2Spider(scrapy.Spider):
    name = "bot2"
    position = {"startPosition": 0}

    def start_requests(self):
        yield scrapy.Request(
            url='https://www.centris.ca/UserContext/Synchronize',
            method='POST',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/json'
            },
            body=json.dumps({'uc': 0}),
            callback=self.get_uck)

    def get_uck(self, response):
        synchronise = json.loads(response.body)
        yield scrapy.Request(
            url='https://www.centris.ca/UserContext/Lock',
            method='POST',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/json'
            },
            body=json.dumps({'uc': 0}),
            callback=self.get_property_count)

    def get_property_count(self, response):
        self.uck = response.body
        payload3 = {"UseGeographyShapes":0,"Filters":[],"FieldsValues":[{"fieldId":"PropertyType","value":"SingleFamilyHome","fieldConditionId":"","valueConditionId":"IsResidential"},{"fieldId":"Category","value":"Residential","fieldConditionId":"","valueConditionId":""},{"fieldId":"SellingType","value":"Sale","fieldConditionId":"","valueConditionId":""},{"fieldId":"LandArea","value":"SquareFeet","fieldConditionId":"IsLandArea","valueConditionId":""},{"fieldId":"SalePrice","value":0,"fieldConditionId":"ForSale","valueConditionId":""},{"fieldId":"SalePrice","value":999999999999,"fieldConditionId":"ForSale","valueConditionId":""}]}
        yield scrapy.Request(
            url='https://www.centris.ca/property/GetPropertyCount',
            method='GET',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/json'
            },
            body=json.dumps(payload3),
            callback=self.update_query)
        
    # def get_filters(self, response):
    #     self.GetPropertyCount = response.body
    #     payload4 = {"UseGeographyShapes":0,"Filters":[],"FieldsValues":[{"fieldId":"PropertyType","value":"SingleFamilyHome","fieldConditionId":"","valueConditionId":"IsResidential"},{"fieldId":"Category","value":"Residential","fieldConditionId":"","valueConditionId":""},{"fieldId":"SellingType","value":"Sale","fieldConditionId":"","valueConditionId":""},{"fieldId":"LandArea","value":"SquareFeet","fieldConditionId":"IsLandArea","valueConditionId":""},{"fieldId":"SalePrice","value":0,"fieldConditionId":"ForSale","valueConditionId":""},{"fieldId":"SalePrice","value":999999999999,"fieldConditionId":"ForSale","valueConditionId":""}]}
    #     yield scrapy.Request(
    #         url='https://www.centris.ca/property/GetFilters',
    #         method='POST',
    #         headers={
    #             'x-requested-with': 'XMLHttpRequest',
    #             'content-type': 'application/json'
    #         },
    #         body=json.dumps(payload4),
    #         callback=self.update_query)
    

    def update_query(self, response):
        update_query = response.body
        payload5 = {"query":{"UseGeographyShapes":0,"Filters":[],"FieldsValues":[{"fieldId":"PropertyType","value":"SingleFamilyHome","fieldConditionId":"","valueConditionId":"IsResidential"},{"fieldId":"Category","value":"Residential","fieldConditionId":"","valueConditionId":""},{"fieldId":"SellingType","value":"Sale","fieldConditionId":"","valueConditionId":""},{"fieldId":"LandArea","value":"SquareFeet","fieldConditionId":"IsLandArea","valueConditionId":""},{"fieldId":"SalePrice","value":0,"fieldConditionId":"ForSale","valueConditionId":""},{"fieldId":"SalePrice","value":999999999999,"fieldConditionId":"ForSale","valueConditionId":""}]},"isHomePage":True}
        yield scrapy.Request(
            url='https://www.centris.ca/property/UpdateQuery',
            method='POST',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/json',
                'x-centris-uck': self.uck
            },
            body=json.dumps(payload5),
            callback=self.get_inscriptions)
        
    def get_inscriptions(self, response):
        self.UpdateQuery = response.body
        payload6 = {"startPosition":12}
        yield scrapy.Request(
            url='https://www.centris.ca/Property/GetInscriptions',
            method='POST',
            headers={
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/json',
                'x-centris-uck': self.uck
            },
            body=json.dumps(self.position),
            callback=self.parse)
        
    def parse(self, response):
        resp_dict = json.loads(response.body)
        count = resp_dict['d']['Result']['count']
        print('count', count)


        # # requête 4 : obtenir les filtres
        # url4 = 'https://www.centris.ca/property/GetFilters'
        # payload4 = {"UseGeographyShapes":0,"Filters":[],"FieldsValues":[{"fieldId":"PropertyType","value":"SingleFamilyHome","fieldConditionId":"","valueConditionId":"IsResidential"},{"fieldId":"Category","value":"Residential","fieldConditionId":"","valueConditionId":""},{"fieldId":"SellingType","value":"Sale","fieldConditionId":"","valueConditionId":""},{"fieldId":"LandArea","value":"SquareFeet","fieldConditionId":"IsLandArea","valueConditionId":""},{"fieldId":"SalePrice","value":0,"fieldConditionId":"ForSale","valueConditionId":""},{"fieldId":"SalePrice","value":999999999999,"fieldConditionId":"ForSale","valueConditionId":""}]}
        # response4 = scrapy.Request.post(url4, json=payload4)

        # # requête 5 : déverrouiller
        # url5 = 'https://www.centris.ca/UserContext/UnLock'
        # payload5 = {"uc":0,"uck":"4303b72e-11c4-47ce-b569-740e4b7c8043"}
        # response5 = scrapy.Request.post(url5, json=payload5)

        # # requête 6 : obtenir le nombre de propriétés
        # url6 = 'https://www.centris.ca/property/GetPropertyCount'
        # payload6 = {"UseGeographyShapes":0,"Filters":[],"FieldsValues":[{"fieldId":"PropertyType","value":"SingleFamilyHome","fieldConditionId":"","valueConditionId":"IsResidential"},{"fieldId":"Category","value":"Residential","fieldConditionId":"","valueConditionId":""},{"fieldId":"SellingType","value":"Sale","fieldConditionId":"","valueConditionId":""},{"fieldId":"LandArea","value":"SquareFeet","fieldConditionId":"IsLandArea","valueConditionId":""},{"fieldId":"SalePrice","value":0,"fieldConditionId":"ForSale","valueConditionId":""},{"fieldId":"SalePrice","value":999999999999,"fieldConditionId":"ForSale","valueConditionId":""}]}
        # response6 = scrapy.Request.post(url6, json=payload6)

        # # requête 7 : mettre à jour la requête
        # url7 = 'https://www.centris.ca/property/UpdateQuery'
        # payload7 = {"query":{"UseGeographyShapes":0,"Filters":[],"FieldsValues":[{"fieldId":"PropertyType","value":"SingleFamilyHome","fieldConditionId":"","valueConditionId":"IsResidential"},{"fieldId":"Category","value":"Residential","fieldConditionId":"","valueConditionId":""},{"fieldId":"SellingType","value":"Sale","fieldConditionId":"","valueConditionId":""},{"fieldId":"LandArea","value":"SquareFeet","fieldConditionId":"IsLandArea","valueConditionId":""},{"fieldId":"SalePrice","value":0,"fieldConditionId":"ForSale","valueConditionId":""},{"fieldId":"SalePrice","value":999999999999,"fieldConditionId":"ForSale","valueConditionId":""}]},"isHomePage":true}
        # response7 = scrapy.Request.post(url7, json=payload7)

        # # requête 8 : obtenir les inscriptions
        # url8 = 'https://www.centris.ca/Property/GetInscriptions'
        # payload8 = {"startPosition":12}
        # response8 = scrapy.Request.post(url8, json=payload8)

        # self.driver.quit()
