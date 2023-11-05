from    connectors.connector    import  Connector
from    bs4                     import  BeautifulSoup
import  pandas                  as      pd
import  requests
import  time

class SuperC(Connector):
    """epycerie.connectors.superc_connector
        ~~~~~~~~~~~~

        This module implements the connector for Super C.

        :copyright: (c) 2023 by Maxim Bacar.
        :license: Apache2, see LICENSE for more details.
    """

    __BASE_URL      = "https://www.superc.ca"
    __FLYER_URL     = "https://www.superc.ca/recherche-page-{}?sortOrder=name-asc&filter=%3Arelevance%3Adeal%3ACirculaire+et+promotions"
    __ALL_URL       = "https://www.superc.ca/epicerie-en-ligne/recherche-page-{}?&filter="
    
    __HEADERS       =  {
        "Cookie"        : "",
        "User-Agent"    : Connector._USER_AGENT
    }

    __STORE         = "SUPERC"


    def __get_cookies( url : str ) -> dict:
        """Generate cookies to block bot protection

        :return:    Cookies
        :rtype:     dict
        """
        response    = requests.get(url.format(0), headers=SuperC.__HEADERS)
        raw_cookies = response.cookies.get_dict()

        nsc         = [key for key in raw_cookies.keys() if ("NSC" in key)][0]

        cookies     = f"JSESSIONID={raw_cookies['JSESSIONID']}; {nsc}={raw_cookies[nsc]};"

        return cookies
    
    def __get_number_of_pages( headers : dict , url : str) -> int:
        """Get the number of pages to scrap

        :headers:   Headers to send with the request
        :url:       URL template
        :return:    Number of pages
        :rtype:     int
        """
        response        = requests.get(url.format(1), headers=headers)
        number_of_page  = BeautifulSoup(response.text, features="lxml").find_all("a", class_="ppn--element")[-2].text

        return int(number_of_page)
     
    
    def __get_page_products( page : int, headers : dict, url : str) -> list[dict]:
        """Get the products on a page

        :page:      Page number to scrap
        :header:    Request headers
        :url:       URL template
        :return:    Products on the page
        :rtype:     list[dict]
        """
        page_data   = []  
        response    = requests.get(url.format(page), headers=headers)
        products    = BeautifulSoup(response.text, features="lxml").find_all("div", "default-product-tile tile-product item-addToCart tile-product--effective-date")

        for product in products:
            product_data = Connector._PRODUCT_DATA_TEMPLATE.copy()
            
            product_data["store"]       = SuperC.__STORE
            product_data["product_id"]  = product.get("data-product-code")
            product_data["name"]        = product.get("data-product-name")
            product_data["brand"]       = product.find("span", class_="head__brand").text.strip()
            product_data["product_url"] = product.find("a", class_="product-details-link").get("href")

            if product.find("span", class_ = "price-update pi-price-promo"):
                product_data["sale_price"]      = SuperC._format_price(product.find("span", class_="price-update pi-price-promo").text)
                product_data["regular_price"]   = SuperC._format_price(product.find("div",  class_="pricing__before-price").find_all("span")[1].text)
            else:
                product_data["regular_price"]   = SuperC._format_price(product.find("span", class_="price-update").text)

            if product.find("span", class_ = "head__unit-details"):
                product_data["size"]            = product.find("span", class_="head__unit-details").text.strip()

            if product.find("img"):
                product_data["image_url"]       = product.find("img").get("src")

            page_data.append(product_data)

        return page_data

            
    def __get_products( url : str) -> list[dict]:
        """
        Get all products

        :url:       URL template to scrap
        :return:    Products
        :rtype:     list[dict] 
        """
        products            = []

        headers             = SuperC.__HEADERS.copy()
        headers["Cookie"]   = SuperC.__get_cookies( url )

       
       
        for page in range( 1, SuperC.__get_number_of_pages( headers, url ) + 1):
            
            products += SuperC.__get_page_products( page, headers, url )
            time.sleep(5)   # Increase time between request to not trigger bot protection

        return products
    

    def flyer():
        """Get all products in sale

        :return:    products
        :rtype:     list[dict]
        """
        url = SuperC.__FLYER_URL
        return SuperC.__get_products( url )
    
    def search( search : str ):
        """Search for a product

        :return:    products
        :rtype:     list[dict]
        """
        url = SuperC.__ALL_URL + search
        return SuperC.__get_products( url )
    
    def all():
        """Get all products

        :return:    products
        :rtype:     list[dict]
        """
        url = SuperC.__ALL_URL
        return SuperC.__get_products( url )
        




    
data = SuperC.flyer()

df = pd.DataFrame(data)

print(df)

df.to_excel('sup.xlsx', index=False)