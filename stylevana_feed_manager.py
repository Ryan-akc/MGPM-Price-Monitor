import csv
import os

from database import Session, Product


# =================================
# 설정
# =================================

FEED_FILE = "stylevana_feed.csv"


# =================================
# URL Normalize
# =================================

def normalize_url(url):

    if not url:
        return ""

    return (
        str(url)
        .strip()
        .split("?")[0]
        .rstrip("/")
        .lower()
    )


# =================================
# CSV 읽기
# =================================

def load_feed():

    feed = {}

    if not os.path.exists(FEED_FILE):
        return feed

    with open(
        FEED_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            url = normalize_url(
                row.get("url")
            )

            if not url:
                continue

            feed[url] = {
                "url": url,
                "product": str(
                    row.get("product", "")
                ).strip(),
                "currency": str(
                    row.get("currency", "")
                ).strip().upper(),
                "price": str(
                    row.get("price", "")
                ).strip()
            }

    return feed


# =================================
# DB 상품
# =================================

def load_products():

    session = Session()

    try:

        return (
            session.query(Product)
            .filter(
                Product.shop_type == "stylevana"
            )
            .order_by(Product.id)
            .all()
        )

    finally:

        session.close()


# =================================
# CSV 누락 상품 자동 추가
# =================================

def add_missing_products(
    feed,
    products
):

    missing = []

    for product in products:

        url = normalize_url(
            product.url
        )

        if not url:
            continue

        if url not in feed:

            missing.append(
                product
            )

    if not missing:

        print()
        print("[ CSV 자동 추가 ]")
        print("추가할 상품이 없습니다.")
        return 0

    file_exists = os.path.exists(
        FEED_FILE
    )

    with open(
        FEED_FILE,
        "a",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "url",
                "product",
                "currency",
                "price"
            ]
        )

        if not file_exists or os.path.getsize(FEED_FILE) == 0:

            writer.writeheader()

        for product in missing:

            writer.writerow({
                "url": normalize_url(
                    product.url
                ),
                "product": product.product,
                "currency": (
                    product.currency
                    or "USD"
                ),
                "price": ""
            })

            print(
                f"추가 완료 | "
                f"ID {product.id} | "
                f"{product.product}"
            )

    return len(missing)


# =================================
# Feed 검사
# =================================

def check_feed():

    print()
    print("=" * 70)
    print("Stylevana Feed 관리")
    print("=" * 70)
    print()

    feed = load_feed()
    products = load_products()

    print(
        f"DB Stylevana 상품 수 : {len(products)}"
    )

    print(
        f"CSV 등록 상품 수     : {len(feed)}"
    )

    print()

    # =================================
    # 누락 확인
    # =================================

    missing = []

    for product in products:

        url = normalize_url(
            product.url
        )

        if url not in feed:

            missing.append(product)

    # =================================
    # 누락 자동 추가
    # =================================

    print("-" * 70)
    print("[ CSV 누락 상품 자동 등록 ]")
    print("-" * 70)

    added = add_missing_products(
        feed,
        products
    )

    # =================================
    # 다시 읽기
    # =================================

    feed = load_feed()

    print()

    print(
        f"자동 추가 : {added}개"
    )

    # =================================
    # 최종 상태
    # =================================

    print()
    print("=" * 70)
    print("최종 Feed 상태")
    print("=" * 70)

    print(
        f"DB Stylevana 상품 : {len(products)}"
    )

    print(
        f"CSV 등록 상품     : {len(feed)}"
    )

    # =================================
    # 가격 상태
    # =================================

    print()
    print("-" * 70)
    print("[ 가격 상태 ]")
    print("-" * 70)

    for product in products:

        url = normalize_url(
            product.url
        )

        row = feed.get(url)

        if row is None:

            continue

        price = row.get(
            "price",
            ""
        ).strip()

        if price:

            print(
                f"ID {product.id:<4} "
                f"{product.product:<30} "
                f"→ {price} USD"
            )

        else:

            print(
                f"ID {product.id:<4} "
                f"{product.product:<30} "
                f"→ [가격 입력 필요]"
            )

    print()
    print("=" * 70)
    print("완료")
    print("=" * 70)


# =================================
# 실행
# =================================

if __name__ == "__main__":

    check_feed()