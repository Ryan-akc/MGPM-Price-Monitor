from datetime import datetime

from database import Session, Product, Price
from crawler.jolse import get_jolse_price



def collect_price(product_id):

    session = Session()

    try:

        product = (
            session.query(Product)
            .filter(
                Product.id == product_id
            )
            .first()
        )


        if not product:

            print("상품 없음")

            return None



        # ==========================
        # 쇼핑몰별 가격 조회
        # ==========================

        if product.shop_type == "jolse":

            price = get_jolse_price(
                product.url
            )

        else:

            print(
                "지원하지 않는 쇼핑몰:",
                product.shop_type
            )

            return None



        if price is None:

            print(
                "가격 추출 실패"
            )

            return None



        # ==========================
        # 마지막 가격 확인
        # ==========================

        last_price = (

            session.query(Price)

            .filter(
                Price.product_id == product.id
            )

            .order_by(
                Price.id.desc()
            )

            .first()

        )



        # ==========================
        # 가격 동일하면 저장 안 함
        # ==========================

        if last_price and last_price.price == price:

            print(
                "가격 변화 없음:",
                product.product,
                price
            )

            return price



        # ==========================
        # 신규 가격 저장
        # ==========================

        item = Price(

            product_id=product.id,

            price=price,

            date=datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )

        )


        session.add(item)

        session.commit()



        print(
            "새 가격 저장:",
            product.product,
            price
        )


        return price



    except Exception as e:

        session.rollback()

        print(
            "가격 수집 오류:",
            e
        )

        return None



    finally:

        session.close()