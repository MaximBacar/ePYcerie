from    bs4         import BeautifulSoup
import  requests
import  re



class Connector():


    _PRODUCT_DATA_TEMPLATE = {
            "product_id"    : "",
            "brand"         : "",
            "size"          : "",
            "product_url"   : "",
            "name"          : "",
            "image_url"     : "",
            "regular_price" : 0.00,
            "sale_price"    : 0.00,
            "store"         : ""
    }

    _USER_AGENT = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"

    def __init__(self) -> None:
        pass


    def _format_price( price : str) -> float:
        """
        Format a string containing a price, to a float

        :price:     Non-formatted price
        :return:    Formatted price
        :rtype:     float
        """

        PRICE_PATTERN_1 = r'(\d+,\d+)'
        PRICE_PATTERN_2 = r'(\d+.\d+)'
        if price:
            match       = re.search(PRICE_PATTERN_1, price)
            if match:
                return float(match.group(1).replace(',','.'))
            else:
                match   = re.search(PRICE_PATTERN_2, price)
                if match:
                    return float(match.group(1))
        return None