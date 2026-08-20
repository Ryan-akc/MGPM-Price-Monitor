from crawler.stylevana import get_stylevana_feed_price
from database import SessionLocal, Product


db = SessionLocal()

try:

    products = (
        db.query(Product)
        .filter(Product.id.in_([34, 35]))
        .order_by(Product.id)
        .all()
    )

    print("\n==============================")
    print("Stylevana Feed 가격 테스트")
    print("==============================\n")

    for p in products:

        price = get_stylevana_feed_price(p.url)

        print(f"ID       : {p.id}")
        print(f"상품명    : {p.product}")
        print(f"URL      : {p.url}")
        print(f"가격     : {price}")
        print("-" * 60)

finally:

    db.close()