from    connectors.connector    import  Connector
import  concurrent.futures
import  requests
import  json
import  time





class JeanCoutu(Connector):
    """epycerie.connectors.jeancoutu_connector
        ~~~~~~~~~~~~

        This module implements the connector for Jean Coutu.

        :copyright: (c) 2023 by Maxim Bacar.
        :license: Apache2, see LICENSE for more details.
    """

    
    
    __ALL_PRODUCTS_URL      = "https://www.jeancoutu.com/Rendering/fr/ShoppingProductsGridContainer/ProductsGrid?isSearchPage=true"
    __PRODUCT_DATA_URL      = "https://www.jeancoutu.com/Rendering/fr/ShoppingProductDetailMainSection/GetShortProduct?productCode={}"
    __PRODUCT_URL           = "https://www.jeancoutu.com/magasiner/produit/{}/"
    __MULTIPLE_URL          = "https://www.jeancoutu.com/rendering/fr/ShoppingProductDetailMainSection/GetMultiSkuData?code={}"

    __PRODUCTS_PER_PAGE     = 120 
    __STORE                 = "JEANCOUTU"

    __PRODUCT_REQUEST_DATA  = {
        "Brand"                 : [],
        "Sort"                  : "no-sort",
        "Price"                 : [],
        "Disponibility"         : "",
        "Selection"             : [],
        "Page"                  : "",
        "TotalDisplayedItem"    : __PRODUCTS_PER_PAGE,
        "HideBrandSort"         : False,
        "LoadAllPages"          : False,
        "NextCategory"          : None,
        "IsSearchPage"          : "True"
    }

    __HEADERS               = {

        "User-Agent": Connector._USER_AGENT
    }

    __THREAD_NBR            = 20

    def __generate_URL(product_id : int) -> str:
        r"""
        Generate the product URL from the product name and ID

        :param name: Product name.
        :param product_id: Product ID.

        :return: Product URL
        :rtype: `str`

        """
        
        return JeanCoutu.__PRODUCT_URL.format(product_id)
        
        
    

    def __get_product_info(product_id : int) -> dict:
        """
        Extract the informations of the product related to the product ID
        """
        url             = JeanCoutu.__PRODUCT_DATA_URL.format(product_id)
        response        = requests.get(url, headers=JeanCoutu.__HEADERS)

        if ( len(response.json()) == 0) :
            return {}
        
        data            = response.json()[0]
        product_data    = Connector._PRODUCT_DATA_TEMPLATE.copy()

        
        product_data["product_id"]          = data["ProductCode"]
        product_data["brand"]               = data["Brand"]
        product_data["size"]                = ""
        product_data["product_url"]         = JeanCoutu.__generate_URL(data["ProductCode"])
        product_data["name"]                = data["ProductName"]
        product_data["image_url"]           = data["Image"]
        product_data["store"]               = JeanCoutu.__STORE

        if data["Variant"]["Price"]:
            product_data["regular_price"]   = data["Variant"]["Price"]["RegularPriceValue"]
            product_data["sale_price"]      = data["Variant"]["Price"]["DiscountPriceValue"]
            

        return product_data
    
    def __get_page_number() -> int:
        """
        Get the number of pages to scrap

        :return: Number of pages
        :rtype: `int`: 
        """
        request_data            = JeanCoutu.__PRODUCT_REQUEST_DATA.copy()   # Request data to the api
        request_data["Page"]    = "0"                                       # Add page number to request data

        response                = requests.post(JeanCoutu.__ALL_PRODUCTS_URL, data=request_data, headers=JeanCoutu.__HEADERS)
        item_numbers            = response.json()["Max"]                    # Total number of items

        return round(item_numbers / JeanCoutu.__PRODUCTS_PER_PAGE)

    
    def __get_page_products( page : int ) -> list[dict]:
        r"""Get all the products on a page number.

        :param page: Page number to scrap.
        :return: Products on the page
        :rtype: `list[`dict`]`: 

        """
        page_data               = []                                                # Products on the page
        request_data            = JeanCoutu.__PRODUCT_REQUEST_DATA.copy()           # Request data to the api
        request_data["Page"]    = f"{page}"                                         # Add page number to request data

        response                = requests.post(JeanCoutu.__ALL_PRODUCTS_URL, data=request_data, headers=JeanCoutu.__HEADERS)
        products                = json.loads(response.json()["AnalyticProducts"])   # JSON response


        products_ids            = [product["id"] for product in products]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            page_data = list(executor.map(JeanCoutu.__get_product_info, products_ids))

        print(f"[{page}] Scraped")

        return page_data

    def get_products():
        """
        Get all products sold at Jean Coutu
        """

        start_time      = time.time()
        number_of_pages = JeanCoutu.__get_page_number()
        pages           = [n for n in range(0, number_of_pages)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=JeanCoutu.__THREAD_NBR) as executor:
            product_list = list(executor.map(JeanCoutu.__get_page_products, pages))

        
        total_time = time.time() - start_time
      
        print("[%.2f s]" % total_time)

        return [item for sublist in product_list for item in sublist]

