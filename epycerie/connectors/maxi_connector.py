from    connectors.connector    import  Connector
import  pandas                  as      pd
import  requests
import  re



class Maxi(Connector):
    """epycerie.connectors.maxi_connector
        ~~~~~~~~~~~~

        This module implements the connector for Maxi.

        :copyright: (c) 2023 by Maxim Bacar.
        :license: Apache2, see LICENSE for more details.
    """

    #   Target API URL
    __API_URL = "https://api.pcexpress.ca/pcx-bff/api/v2/flyersPage"

    #   Request headers
    __HEADERS = {  
        "Accept"                : "*/*",
        "Accept-Encoding"       : "gzip, deflate, br",
        "Accept-Language"       : "fr",
        "Cache-Control"         : "no-cache",
        "Connection"            : "keep-alive",
        "Content-Length"        : "299",
        "Content-Type"          : "application/json",
        "Host"                  : "api.pcexpress.ca",
        "Origin"                : "https://www.maxi.ca",
        "Origin_Session_Header" : "B",
        "Pragma"                : "no-cache",
        "Referer"               : "https://www.maxi.ca/",
        "Sec-Fetch-Dest"        : "empty",
        "Sec-Fetch-Mode"        : "cors",
        "Sec-Fetch-Site"        : "cross-site",
        "User-Agent"            : Connector._USER_AGENT,
        "sec-ch-ua"             : "\"Chromium\";v=\"118\", \"Google Chrome\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
        "sec-ch-ua-mobile"      : "?1",
        "sec-ch-ua-platform"    : "\"Android\"",
        "x-apikey"              : "C1xujSegT5j3ap3yexJjqhOfELwGKYvz",
        "x-application-type"    : "Web",
        "x-channel"             : "web",
        "x-loblaw-tenant-id"    : "ONLINE_GROCERIES",
        "x-preview"             : "false"
    }

    # API request data
    __REQUEST_DATA = {
        "cart":{
            "cartId":"afc9da43-085f-477a-931c-bb9951d73dd6"
        },
        "fulfillmentInfo":{
            "storeId":"7234",
            "pickupType":"STORE",
            "offerType":"OG"
        },
        "listingInfo":{
            "filters":{
                "icta":["flyer-homepage-hero-banner-guest"]
            },
            "sort":{
                "name":"asc"
            },
            "pagination":{
                "from":0
            },
            "includeFiltersInResponse":True
        },
        "banner":"maxi"
    }

    __STORE = "MAXI"



    def __format_text(data : str) -> str:
        """
        Format text correctly
        """
        return data.replace("\xa0", ' ')

        
    def __extract_size(data : str) -> str:
        '''
        Extract and format the product size from the scrapped string
        '''
        data = Maxi.__format_text(data)
        return data.split(',')[0]
        
    

    def __fetch_api( request_data : dict ) -> dict:
        """
        Fetch store API
        """
        response = requests.post( Maxi.__API_URL, headers=Maxi.__HEADERS, json=request_data )

        return response.json()
    

    def __has_next_page(data : dict) -> bool:
        """
        Verify if there is a next page on the flyer
        """
        return data["layout"]["sections"]["productListingSection"]["components"][0]["data"]["productGrid"]["pagination"]["hasMore"]
        
    
    def __get_product_data( product : dict ) -> dict:
        """
        Get the informations from one product
        """
        data                = Maxi._PRODUCT_DATA_TEMPLATE.copy()


        data["product_id"]  = product["productId"]
        data["brand"]       = product["brand"]
        data["size"]        = Maxi.__extract_size(product["packageSizing"])
        data["product_url"] = product["link"]
        data["name"]        = product["title"]
        data["store"]       = Maxi.__STORE

        if (len(product["productImage"]) > 0):
            data["image_url"]       = product["productImage"][0]["imageUrl"]
        if product["pricing"]["wasPrice"]:
            data["regular_price"]   = Maxi._format_price(product["pricing"]["wasPrice"])
        if product["pricing"]["price"]:
            data["sale_price"]      = float(product["pricing"]["price"])
        
        return data
        
        

    def __get_page_products(data : dict) -> list[dict]:
        """
        Get all products on a page
        """
        page_product    = []
        products        = data["layout"]["sections"]["productListingSection"]["components"][0]["data"]["productGrid"]["productTiles"]

        for product in products:
            page_product.append(Maxi.__get_product_data(product))

        return page_product

    def __get_products() -> list[dict]:
        """
        Scrap Maxi Flyer
        """

        products        = []
        has_next_page   = True
        current_page    = 1

        while (has_next_page):
            request_data                                        = Maxi.__REQUEST_DATA.copy()
            request_data["listingInfo"]["pagination"]["from"]   = current_page
            
            data                                                = Maxi.__fetch_api( request_data )
            print(data)
            has_next_page                                       = Maxi.__has_next_page( data )
            products                                            = products + Maxi.__get_page_products( data ) 
            current_page                                        = current_page + 1

        return products

    def flyer():
        return Maxi.__get_products()
