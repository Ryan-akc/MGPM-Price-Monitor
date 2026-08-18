from datetime import datetime

from database import (
    Session,
    Product,
    Price
)

from crawler.jolse import (
    get_jolse_price
)

from crawler.yesstyle import (
    get_yesstyle_price
)

from crawler.stylevana import (
    get_stylevana_price
)

from crawler.amazon import (
    get_amazon_price
)

from crawler.stylekorean import (
    get_stylekorean_price
)

from crawler.coupang import (
    get_coupang_price
)

from alert_engine import (
    check_price_alert
)


# =================================
# Price Collection
# =================================

def collect_price(product_id):

    session = Session()

    try:

        # =================================
        # Product 조회
        # =================================

        product = (
            session.query(Product)
            .filter(
                Product.id == product_id
            )
            .first()
        )

        if not product:

            print(
                "상품 없음:",
                product_id
            )

            return None

        # =================================
        # 쇼핑몰별 가격 조회
        # =================================

        shop_type = (
            str(
                product.shop_type or ""
            )
            .strip()
            .lower()
        )

        if shop_type == "jolse":

            price = get_jolse_price(
                product.url
            )

        elif shop_type == "yesstyle":

            price = get_yesstyle_price(
                product.url
            )

        elif shop_type == "stylevana":

            price = get_stylevana_price(
                product.url
            )

        elif shop_type == "amazon":

            price = get_amazon_price(
                product.url
            )

        elif shop_type == "stylekorean":

            price = get_stylekorean_price(
                product.url
            )

        elif shop_type == "coupang":

            price = get_coupang_price(
                product.url
            )

        else:

            print(
                "지원하지 않는 쇼핑몰:",
                product.shop_type
            )

            return None

        # =================================
        # 가격 추출 실패
        #
        # 실패한 가격은 DB에 저장하지 않음
        # 기존 마지막 정상 가격 유지
        # =================================

        if price is None:

            print(
                f"가격 추출 실패: "
                f"{product.product}"
            )

            return None

        # =================================
        # 가격 형식 정리
        # =================================

        try:

            price = float(price)

        except (
            TypeError,
            ValueError
        ):

            print(
                "가격 형식 오류:",
                product.product,
                price
            )

            return None

        # =================================
        # 비정상 가격 방지
        # =================================

        if price <= 0:

            print(
                f"비정상 가격 - 저장하지 않음: "
                f"{product.product} / {price}"
            )

            return None

        # =================================
        # 마지막 정상 가격 확인
        # =================================

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

        # =================================
        # 가격 변화 없음
        #
        # 동일 가격이면 중복 저장 안 함
        # =================================

        if (
            last_price
            and float(last_price.price) == price
        ):

            print(
                f"가격 변화 없음: "
                f"{product.product} / "
                f"{price}"
            )

            return price

        # =================================
        # 신규 가격 저장
        # =================================

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
            f"가격 저장 완료: "
            f"{product.product} / "
            f"{price}"
        )

        # =================================
        # Alert Engine
        # =================================

        try:

            check_price_alert(
                session,
                product.id
            )

        except Exception as e:

            print(
                "Alert Engine 오류:",
                e
            )

        # =================================
        # 완료
        # =================================

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