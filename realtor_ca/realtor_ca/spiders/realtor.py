import scrapy
import json

class RealtorSpider(scrapy.Spider):
    name = 'realtor'
    allowed_domains = ['api2.realtor.ca']
    api_post = "https://api2.realtor.ca/Listing.svc/PropertySearch_Post"

    ZoomLevel = 4
    LatitudeMax = 70.92654
    LongitudeMax = -41.68148
    LatitudeMin = 32.68337
    LongitudeMin = -124.38655
    CurrentPage = 1
    Sort = "6-D"
    PropertyTypeGroupID = 1
    PropertySearchTypeId = 0
    TransactionTypeId = 2
    Currency = "CAD"
    RecordsPerPage = 200
    ApplicationId = 1
    CultureId = 1
    Version = 7.0
    payload = f"ZoomLevel={ZoomLevel}&LatitudeMax={LatitudeMax}&LongitudeMax={LongitudeMax}&LatitudeMin={LatitudeMin}&LongitudeMin={LongitudeMin}&CurrentPage={CurrentPage}&Sort={Sort}&PropertyTypeGroupID={PropertyTypeGroupID}&PropertySearchTypeId={PropertySearchTypeId}&TransactionTypeId={TransactionTypeId}&Currency={Currency}&RecordsPerPage={RecordsPerPage}&ApplicationId={ApplicationId}&CultureId={CultureId}&Version={Version}"
    
    headers = {
        "authority": "api2.realtor.ca",
        "method": "POST",
        "path": "/Listing.svc/PropertySearch_Post",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "fr-FR,fr;q=0.7",
        # "content-length": "259",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": "visid_incap_2271082=RbfvE80dShq9glknuR1rqFffLmQAAAAAQUIPAAAAAABYR9JKD1IHn4dcrjUU/54e; gig_bootstrap_3_mrQiIl6ov44s2X3j6NGWVZ9SDDtplqV7WgdcyEpGYnYxl7ygDWPQHqQqtpSiUfko=gigya-pr_ver4; ProfileTS=1681327208924; visid_incap_2269415=H0VRjq0nTHC3zOWbapx02j/eJmQAAAAAQkIPAAAAAACAMparAcBjJd7Ml9bcxcpKhc1phYs3fYJg; nlbi_2269415=YXAJXqvL+TLa00jL+/Ys1gAAAAAxGMPli2cvGLcz4Vq8u4jA; ASP.NET_SessionId=f0vscgdwar0otqankd3x5ev3; nlbi_2271082=919MDx49lSRMvn7wVPrQ3QAAAACLZdqIGcTcdz0Gec9x0oGg; visid_incap_2653241=IsMY9WJsQT27TQzKnYErvlcpOGQAAAAAQUIPAAAAAABlecN6xKMq0Tt80rJwyBAC; nlbi_2653241=ggNlVIPxozU3gUgwQ2mJPQAAAABXoQyHbCtKo0aaTlu6aUuP; incap_ses_304_2653241=ck6tPHrMQysj9rx24QY4BGQpOGQAAAAA/VKMabD+hlTBj9xD1PsIuw==; nlbi_2653241_2147483392=brbyDFqEYTA54y44Q2mJPQAAAABUIrq1ELXVyJjfCO4ZZOdR; incap_ses_304_2271082=mrqzGY3PZGOdHsJ24QY4BIItOGQAAAAAZYyxkHnnEyREMRu81Ot1jw==; incap_ses_304_2269415=OrK5fuZuNSsWdsd24QY4BJ0xOGQAAAAAKj+eOvSPuVWEDpHq+QsyXg==; reese84=3:YnYuY5knFFxhIWYzxGxnpg==:3tuaYSvEL1oTljSohgsKIApxeE4mEMmNYDD+ygvWog3H93d5dgjaGI7MkC5RRG7K3vy/PSetm4jlk+Z4lu/mQapryFPVPoEkD170JtDp1WTIDmhKCdDwXswsYPMSctzBJO2V0phBWPgyGiz1trPPdP7+132f4MMaFxAbOlsCtyFDIyY1/L4VqRS+bMieLIJHtyDGAzpxaPKW8A0cVD7RaZ7nEKm7VLhAdi0DI9n4Ou3SzOIlva5iaRN0jWtIpqEL4bZXnJQp1a5k9ZoNlEuEFEChov9t3M05cGMFXcUbGLtDwCB6lXIoQ3k84mNgae3LwgSM2P/hih0af27KpAdz/zWeVFOT8bDi0sDvq/wGB6aMqqnRPrJjdeXFT8aW9Yw6GM3kZ5LTuL9cQCPNEspKS78usJ8U1krGZW9DTfIQHrhzmWYwhKpVLfPYlHno9Xhn1JXfTKafSP/3XUQSoK2+Ig==:Sh3rqrHhMAWgVUIHtHqnNQjO1nHPg4Q5SvFykGzboSY=; nlbi_2269415_2147483392=+e35RSipYlNnn14++/Ys1gAAAAAygXGVGcPMSHPufqM/XSUM",
        "origin": "https://www.realtor.ca",
        "referer": "https://www.realtor.ca/",
        "sec-ch-ua": '"Chromium";v="112", "Brave";v="112", "Not:A-Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        # "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        }

    def start_requests(self):
        yield scrapy.Request(url=self.api_post,
                        callback=self.parse,
                        method='POST', 
                        headers=self.headers,
                        body=self.payload,
                        meta={'CurrentPage': 1},
                        )

    def parse(self, response):
        CurrentPage = response.meta['CurrentPage']
        response_json = json.loads(response.body)
        ErrorCode = response_json['ErrorCode']
        Paging = response_json['Paging']
        TotalRecords = Paging['TotalRecords']
        TotalPages = Paging['TotalPages']
        Results = response_json['Results']
        for result in Results:
            yield {
                'Id': result['Id'],
                "MlsNumber": result['MlsNumber'],
                "PublicRemarks": result['PublicRemarks'],
                "Building": result['Building'],
                "Individual": result['Individual'],
                "Property": result['Property'],
                "Business": result['Business'],
                "Land": result['Land'],
                # "AlternateURL": result['DetailsLink'],
                "PostalCode": result['PostalCode'],
                "ProvinceName": result['ProvinceName'],
                "RelativeDetailsURL": result['RelativeDetailsURL'],
                "StatusId": result['StatusId'],
                # "PhotoChangeDateUTC": result['PhotoChangeDateUTC'],
                "Distance": result['Distance'], 
                "RelativeURLEn": result['RelativeURLEn'],
                "RelativeURLFr": result['RelativeURLFr'],
                "Media": result['Media'],
                "InsertedDateUTC": result['InsertedDateUTC'],
                "TimeOnRealtor": result['TimeOnRealtor'],
                "Tags": result['Tags'],
            }


        Pins = response_json['Pins']
        if CurrentPage <= 50:
            CurrentPage += 1
            new_payload = f"ZoomLevel={self.ZoomLevel}&LatitudeMax={self.LatitudeMax}&LongitudeMax={self.LongitudeMax}&LatitudeMin={self.LatitudeMin}&LongitudeMin={self.LongitudeMin}&CurrentPage={CurrentPage}&Sort={self.Sort}&PropertyTypeGroupID={self.PropertyTypeGroupID}&PropertySearchTypeId={self.PropertySearchTypeId}&TransactionTypeId={self.TransactionTypeId}&Currency={self.Currency}&RecordsPerPage={self.RecordsPerPage}&ApplicationId={self.ApplicationId}&CultureId={self.CultureId}&Version={self.Version}"
            yield scrapy.Request(url=self.api_post,
                        callback=self.parse,
                        method='POST', 
                        headers=self.headers,
                        body=new_payload,
                        meta={'CurrentPage': CurrentPage}
                        )

            print(f"=================={CurrentPage}==================")
            print(f"=================={TotalRecords}==================")





















        # for result in Results:
        #     result_Id = result['Id']
        #     result_MlsNumber = result['MlsNumber']
        #     result_PublicRemarks = result['PublicRemarks']
        # # |==========================BUILDING==========================|
        #     result_Building = result['Building']
        #     result_building_BathroomTotal = result['Building']['BathroomTotal']
        #     result_building_Bedrooms = result['Building']['Bedrooms']
        #     # result_building_SizeInterior = result['Building']['SizeInterior']
        #     result_building_StoriesTotal = result['Building']['StoriesTotal']
        #     result_building_Type = result['Building']['Type']
        # # # |==========================INDIVIDUAL==========================|
        #     result_Individual = result['Individual']
            # result_Individual_IndividualID = result['Individual'][0]
            # result_Individual_Name = result['Individual'][1]
            # result_Individual_Organization = result['Individual']['Organization']
            # result_Individual_Phones = result['Individual']['Phones']
            # result_Individual_Websites = result['Individual']['Websites']
            # result_Individual_Emails = result['Individual']['Emails']
            # result_Individual_Photo = result['Individual']['Photo']
            # result_Individual_Position = result['Individual']['Position']
            # result_Individual_PermitFreetextEmail = result['Individual']['PermitFreetextEmail']
            # result_Individual_FirstName = result['Individual']['FirstName']
            # result_Individual_LastName = result['Individual']['LastName']
            # result_Individual_CorporationName = result['Individual']['CorporationName']
            # result_Individual_CorporationDisplayTypeId = result['Individual']['CorporationDisplayTypeId']
            # result_Individual_CorporationType = result['Individual']['CorporationType']
            # result_Individual_PermitShowListingLink = result['Individual']['PermitShowListingLink']
            # result_Individual_RelativeDetailsURL = result['Individual']['RelativeDetailsURL']
            # result_Individual_AgentPhotoLastUpdated = result['Individual']['AgentPhotoLastUpdated']
            # result_Individual_PhotoHighRes = result['Individual']['PhotoHighRes']
            # result_Individual_RankMyAgentKey = result['Individual']['RankMyAgentKey']
            # result_Individual_RealSatisfiedKey = result['Individual']['RealSatisfiedKey']
        # # |==========================PROPERTY==========================|
        #     result_Property = result['Property']
        #     result_Property_Price = result['Property']['Price']
        #     result_Property_Type = result['Property']['Type']
        #     result_Property_Address = result['Property']['Address']
        #     result_Property_Photo = result['Property']['Photo']
        #     result_Property_Parking = result['Property']['Parking']
        #     result_Property_ParkingSpaceTotal = result['Property']['ParkingSpaceTotal']
        #     result_Property_TypeId = result['Property']['TypeId']
        #     result_Property_FarmType = result['Property']['FarmType']
        #     result_Property_ZoningType = result['Property']['ZoningType']
        #     result_Property_AmmenitiesNearBy = result['Property']['AmmenitiesNearBy']
        #     result_Property_ConvertedPrice = result['Property']['ConvertedPrice']
        #     result_Property_ParkingType = result['Property']['ParkingType']
        #     result_Property_PriceUnformattedValue = result['Property']['PriceUnformattedValue']
        # # |==========================BUSINESS==========================|
        #     result_Business = result['Business']
        # # |==========================LAND==========================|
        #     result_Land = result['Land']
        #     result_Land_SizeTotal = result['Land']['SizeTotal']
        #     result_Land_SizeFrontage = result['Land']['SizeFrontage']
        #     result_AlternateURL_DetailsLink = result['AlternateURL']['DetailsLink']
        #     result_PostalCode = result['PostalCode']
        #     result_ProvinceName = result['ProvinceName']
        #     result_RelativeDetailsURL = result['RelativeDetailsURL']
        #     result_StatusId = result['StatusId']
        #     result_PhotoChangeDateUTC = result['PhotoChangeDateUTC']
        #     result_Distance = result['Distance']
        #     result_RelativeURLEn = result['RelativeURLEn']
        #     result_RelativeURLFr = result['RelativeURLFr']
        # # |==========================MEDIA==========================|
        #     result_Media = result['Media']
        #     result_Media_MediaCategoryId = result['Media']['MediaCategoryId']
        #     result_Media_MediaCategoryURL = result['Media']['MediaCategoryURL']
        #     result_Media_Description = result['Media']['Description']
        #     result_Media_Order = result['Media']['Order']
        #     result_InsertedDateUTC = result['InsertedDateUTC']
        #     result_TimeOnRealtor = result['TimeOnRealtor']
        # # |==========================MEDIA==========================|
        #     result_Tags = result['Tags']
        #     result_Tags_Label = result['Tags']['Label']
        #     result_Tags_HTMLColorCode = result['Tags']['HTMLColorCode']
        #     result_Tags_ListingTagTypeID = result['Tags']['ListingTagTypeID']
            # yield {
            #     "result_Id": result_Id,
            #     "result_MlsNumber": result_MlsNumber,
            #     "result_PublicRemarks": result_PublicRemarks,
            # # |==========================BUILDING==========================|
            #     "result_Building": result_Building,
            #     "result_building_BathroomTotal": result_building_BathroomTotal,
            #     "result_building_Bedrooms": result_building_Bedrooms,
            #     # "result_building_SizeInterior": result_building_SizeInterior,
            #     "result_building_StoriesTotal": result_building_StoriesTotal,
            #     "result_building_Type": result_building_Type,
            # # |==========================INDIVIDUAL==========================|
            #     "result_Individual": result_Individual,
                # "result_Individual_IndividualID": result_Individual_IndividualID,
                # "result_Individual_Name": result_Individual_Name,
                # "result_Individual_Organization": result_Individual_Organization,
                # "result_Individual_Phones": result_Individual_Phones,
                # "result_Individual_Websites": result_Individual_Websites,
                # "result_Individual_Emails": result_Individual_Emails,
                # "result_Individual_Photo": result_Individual_Photo,
                # "result_Individual_Position": result_Individual_Position,
                # "result_Individual_PermitFreetextEmail": result_Individual_PermitFreetextEmail,
                # "result_Individual_FirstName": result_Individual_FirstName,
                # "result_Individual_LastName": result_Individual_LastName,
                # "result_Individual_CorporationName": result_Individual_CorporationName,
                # "result_Individual_CorporationDisplayTypeId": result_Individual_CorporationDisplayTypeId,
                # "result_Individual_CorporationType": result_Individual_CorporationType,
                # "result_Individual_PermitShowListingLink": result_Individual_PermitShowListingLink,
                # "result_Individual_RelativeDetailsURL": result_Individual_RelativeDetailsURL,
                # "result_Individual_AgentPhotoLastUpdated": result_Individual_AgentPhotoLastUpdated,
                # "result_Individual_PhotoHighRes": result_Individual_PhotoHighRes,
                # "result_Individual_RankMyAgentKey": result_Individual_RankMyAgentKey,
                # "result_Individual_RealSatisfiedKey": result_Individual_RealSatisfiedKey,
            # # |==========================PROPERTY==========================|
            #     "result_Property": result_Property,
            #     "result_Property_Price": result_Property_Price,
            #     "result_Property_Type": result_Property_Type,
            #     "result_Property_Address": result_Property_Address,
            #     "result_Property_Photo": result_Property_Photo,
            #     "result_Property_Parking": result_Property_Parking,
            #     "result_Property_ParkingSpaceTotal": result_Property_ParkingSpaceTotal,
            #     "result_Property_TypeId": result_Property_TypeId,
            #     "result_Property_FarmType": result_Property_FarmType,
            #     "result_Property_ZoningType": result_Property_ZoningType,
            #     "result_Property_AmmenitiesNearBy": result_Property_AmmenitiesNearBy,
            #     "result_Property_ConvertedPrice": result_Property_ConvertedPrice,
            #     "result_Property_ParkingType": result_Property_ParkingType,
            #     "result_Property_PriceUnformattedValue": result_Property_PriceUnformattedValue,
            # # |==========================BUSINESS==========================|
            #     "result_Business": result_Business,
            # # |==========================LAND==========================|
            #     "result_Land": result_Land,
            #     "result_Land_SizeTotal": result_Land_SizeTotal,
            #     "result_Land_SizeFrontage": result_Land_SizeFrontage,
            #     "result_AlternateURL_DetailsLink": result_AlternateURL_DetailsLink,
            #     "result_PostalCode": result_PostalCode,
            #     "result_ProvinceName": result_ProvinceName,
            #     "result_RelativeDetailsURL": result_RelativeDetailsURL,
            #     "result_StatusId": result_StatusId,
            #     "result_PhotoChangeDateUTC": result_PhotoChangeDateUTC,
            #     "result_Distance": result_Distance,
            #     "result_RelativeURLEn": result_RelativeURLEn,
            #     "result_RelativeURLFr": result_RelativeURLFr,
            # # |==========================MEDIA==========================|
            #     "result_Media": result_Media,
            #     "result_Media_MediaCategoryId": result_Media_MediaCategoryId,
            #     "result_Media_MediaCategoryURL": result_Media_MediaCategoryURL,
            #     "result_Media_Description": result_Media_Description,
            #     "result_Media_Order": result_Media_Order,
            #     "result_InsertedDateUTC": result_InsertedDateUTC,
            #     "result_TimeOnRealtor": result_TimeOnRealtor,
            # # |==========================MEDIA==========================|
            #     "result_Tags": result_Tags,
            #     "result_Tags_Label": result_Tags_Label,
            #     "result_Tags_HTMLColorCode": result_Tags_HTMLColorCode,
            #     "result_Tags_ListingTagTypeID": result_Tags_ListingTagTypeID,
                # }

        # print(result_building_BathroomTotal)
        # print(f"=================================={result_Individual_IndividualID}==================================")



