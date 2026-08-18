import csv
import re


# =================================
# Stylevana Feed
# =================================

FEED_FILE = "stylevana_feed.csv"


# =================================
# URL Normalize
# =================================

def normalize_url(url):

    if not url:
        return ""

    url = str(url).strip()

    url = url.split("?")[0]

    url = url.rstrip("/")

    return url.lower()


# =================================
# Price Parse
# =================================

def _parse_price(value):

    if value is None:
        return None

    try:

        text = str(value)

        text = text.replace(",", "")

        text = re.sub(
            r"[^0-9.]",
            "",
            text
        )

        if not text:
            return None

        price = float(text)

        if price <= 0:
            return None

        return price

    except (
        TypeError,
        ValueError
    ):

        return None


# =================================
# Get Stylevana Feed Price
# =================================

def get_stylevana_feed_price(
    url,
    feed_file=FEED_FILE
):

    # =================================
    # Feed File Check
    # =================================

    if not feed_file:

        print(
            "Stylevana Feed 파일 경로가 없습니다."
        )

        return None

    try:

        with open(
            feed_file,
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as f:

            reader = csv.DictReader(f)

            # =================================
            # Target URL
            # =================================

            target_url = normalize_url(url)

            if not target_url:

                print(
                    "Stylevana 상품 URL이 비어 있습니다."
                )

                return None

            # =================================
            # Find Product
            # =================================

            for row in reader:

                feed_url = normalize_url(
                    row.get("url")
                )

                if feed_url != target_url:
                    continue

                # =================================
                # Currency
                # =================================

                currency = str(
                    row.get(
                        "currency",
                        ""
                    )
                ).upper().strip()

                if currency != "USD":

                    print(
                        f"Stylevana 통화 오류: {currency}"
                    )

                    return None

                # =================================
                # Price
                # =================================

                raw_price = row.get(
                    "price"
                )

                price = _parse_price(
                    raw_price
                )

                if price is None:

                    print(
                        "Stylevana 가격 변환 실패"
                    )

                    return None

                return price

            # =================================
            # URL Not Found
            # =================================

            print(
                "Stylevana 상품 URL을 찾지 못했습니다."
            )

            return None

    except FileNotFoundError:

        print(
            f"Stylevana Feed 파일을 찾을 수 없습니다: "
            f"{feed_file}"
        )

        return None

    except Exception as e:

        print(
            f"Stylevana Feed 오류: {e}"
        )

        return None