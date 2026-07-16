from crawler.jolse import get_jolse_price


url = "https://jolse.com/product/marymay-tranexamic-acidglutathion-eye-cream-30ml/48105/category/1022/display/1/"


price = get_jolse_price(url)


print(
    "현재 가격:",
    price
)