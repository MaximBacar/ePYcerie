from    connectors.connector    import  Connector
from    bs4                     import  BeautifulSoup
import  pandas                  as      pd
import  concurrent.futures
import  requests
import  json
import  re



class IGA(Connector):
    """epycerie.connectors.iga_connector
        ~~~~~~~~~~~~

        This module implements the connector for IGA.

        :copyright: (c) 2023 by Maxim Bacar.
        :license: Apache2, see LICENSE for more details.
    """

    __BASE_URL      = "www.iga.net"
    __FLYER_URL     = "https://www.iga.net/fr/epicerie_en_ligne/parcourir/dans-les-circulaires?page={}&pageSize=500"
    __ALL_URL       = "https://www.iga.net/fr/search?k=&page={}&pageSize=24"
    
    __HEADERS       = {
        "User-Agent" : Connector._USER_AGENT
    }
    __THREAD_NBR    = 10

    __STORE         = "IGA"


    

    def __get_number_of_pages( url : str ) -> int:
        """Get the number of pages to scrapp

        :url:       URL Template
        :return:    Number of pages
        :rtype:     int
        """

        response        = requests.get( url.format(1), headers = IGA.__HEADERS )
        last_page_url   = BeautifulSoup(response.text, features="lxml").find("a", class_="icon--arrow-skinny-right-double").get("href")

        match           = re.search(r'(?:\?|&)page=(\d+)', last_page_url)

        page_number     = int(match.group(1))

        return page_number
        
    def __get_page_products( url : str ) -> list[dict]:
        """Get the products on a page

        :url:       URL Template
        :return:    Products
        :rtype:     list[dict]
        """

        page_data   = []
        response    = requests.get( url, headers=IGA.__HEADERS)
        products    = BeautifulSoup(response.text, features="lxml").find_all("div", class_="item-product js-product js-equalized js-addtolist-container js-ga")

        for product in products:   
            data_json               = json.loads(product.get("data-product").replace("'",'"'))
            formatted_data          = {new_key: data_json[old_key] for new_key, old_key in [("product_id", "ProductId"), ("brand", "BrandName"), ("size", "Size"), ("name", "FullDisplayName"), ("product_url", "ProductUrl"), ("image_url","ProductImageUrl"), ("regular_price", "RegularPrice"), ("sale_price", "SalesPrice")]}
            formatted_data["store"] = IGA.__STORE
        
            page_data.append(formatted_data)

        return page_data

    def __get_products( url : str ) -> list[dict]:
        """
        Get all products

        :url:       URL template to scrap
        :return:    Products
        :rtype:     list[dict] 
        """
        number_of_page      = IGA.__get_number_of_pages( url )
        pages               = [url.format(n) for n in range(1, number_of_page + 1)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=IGA.__THREAD_NBR) as executor:
            product_list    = list(executor.map(IGA.__get_page_products, pages))

        return [item for sublist in product_list for item in sublist]    


    def flyer():
        """Get all products in sale

        :return:    products
        :rtype:     list[dict]
        """
        url = IGA.__FLYER_URL
        return IGA.__get_products( url )
    
    def all():
        """Get all products

        :return:    products
        :rtype:     list[dict]
        """
        url = IGA.__ALL_URL
        return IGA.__get_products( url )
        


print(IGA.flyer())