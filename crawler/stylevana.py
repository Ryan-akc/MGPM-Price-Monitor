from crawler.stylevana_feed import (
    get_stylevana_feed_price
)


# =================================
# Stylevana Price
# =================================

def get_stylevana_price(url):

    try:

        price = get_stylevana_feed_price(
            url
        )

        if price is None:

            return None

        return price

    except Exception as e:

        print(
            f"Stylevana 오류: {e}"
        )

        return None