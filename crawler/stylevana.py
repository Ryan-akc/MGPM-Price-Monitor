import json
import re

import requests
from bs4 import BeautifulSoup

from crawler.stylevana_feed import (
    get_stylevana_feed_price
)


# =================================
# Headers
# =================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# =================================
# Price Parse
# =================================

def parse_price(value):

    if value is None:
        return None

    try:

        text = str(value).replace(",", "")

        match = re.search(
            r"(\d+(?:\.\d+)?)",
            text
        )

        if not match:
            return None

        price = float(
            match.group(1)
        )

        return price if price > 0 else None

    except (
        TypeError,
        ValueError
    ):

        return None


# =================================
# JSON-LD Price
# =================================

def get_jsonld_price(soup):

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:

            if not script.string:
                continue

            data = json.loads(
                script.string
            )

            items = (
                data
                if isinstance(data, list)
                else [data]
            )

            for item in items:

                if not isinstance(
                    item,
                    dict
                ):
                    continue

                offers = item.get(
                    "offers"
                )

                if isinstance(
                    offers,
                    list
                ):
                    offers = (
                        offers[0]
                        if offers
                        else None
                    )

                if not isinstance(
                    offers,
                    dict
                ):
                    continue

                currency = str(
                    offers.get(
                        "priceCurrency",
                        ""
                    )
                ).upper()

                price = parse_price(
                    offers.get("price")
                )

                if (
                    currency == "USD"
                    and price is not None
                ):

                    return price

        except Exception:
            continue

    return None


# =================================
# Meta Price
# =================================

def get_meta_price(soup):

    selectors = [
        (
            "meta",
            {
                "property":
                    "product:price:amount"
            }
        ),
        (
            "meta",
            {
                "itemprop":
                    "price"
            }
        ),
    ]

    for tag_name, attrs in selectors:

        tag = soup.find(
            tag_name,
            attrs=attrs
        )

        if tag:

            price = parse_price(
                tag.get("content")
            )

            if price is not None:
                return price

    return None


# =================================
# HTML Price
# =================================

def get_html_price(soup):

    selectors = [
        "[itemprop='price']",
        ".special-price .price",
        ".product-info-price .price",
        ".price-box .special-price .price",
        ".price-final_price .price",
        ".product-price .price",
    ]

    for selector in selectors:

        for element in soup.select(
            selector
        ):

            price = parse_price(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            if price is not None:
                return price

    return None


# =================================
# Direct Collection
# =================================

def get_stylevana_direct_price(url):

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        print(
            "Stylevana HTTP:",
            response.status_code
        )

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        price = get_jsonld_price(
            soup
        )

        if price is not None:

            print(
                "Stylevana 직접 수집 성공 "
                "(JSON-LD):",
                price
            )

            return price

        price = get_meta_price(
            soup
        )

        if price is not None:

            print(
                "Stylevana 직접 수집 성공 "
                "(Meta):",
                price
            )

            return price

        price = get_html_price(
            soup
        )

        if price is not None:

            print(
                "Stylevana 직접 수집 성공 "
                "(HTML):",
                price
            )

            return price

        print(
            "Stylevana 직접 페이지에서 "
            "가격을 찾지 못했습니다."
        )

        return None

    except Exception as e:

        print(
            "Stylevana 직접 수집 오류:",
            e
        )

        return None


# =================================
# Final Stylevana Price
# =================================

def get_stylevana_price(url):

    # 1. 실제 Stylevana 페이지 수집
    price = get_stylevana_direct_price(
        url
    )

    if price is not None:
        return price

    # 2. 기존 Feed 백업
    print(
        "Stylevana Feed 백업 확인 중..."
    )

    price = get_stylevana_feed_price(
        url
    )

    if price is not None:

        print(
            "Stylevana Feed 가격 사용:",
            price
        )

        return price

    print(
        "Stylevana 가격을 수집하지 못했습니다."
    )

    return None