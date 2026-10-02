import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup

from crawler.stylevana_feed import (
    get_stylevana_feed_price
)


# =================================
# Bright Data
# =================================

BRIGHTDATA_API_KEY = os.getenv(
    "BRIGHTDATA_API_KEY"
)

BRIGHTDATA_DATASET_ID = (
    "gd_mq6qxqvi15yc8m41df"
)

BRIGHTDATA_SCRAPE_URL = (
    "https://api.brightdata.com/"
    "datasets/v3/scrape"
)

BRIGHTDATA_SNAPSHOT_URL = (
    "https://api.brightdata.com/"
    "datasets/v3/snapshot/"
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
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.stylevana.com/en_US/",
    "Connection": "keep-alive",
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
# Bright Data Result Price
# =================================

def get_brightdata_price_from_result(
    data
):

    if not data:
        return None

    # Bright Data가 list로 반환하는 경우
    if isinstance(data, list):

        for item in data:

            price = get_brightdata_price_from_result(
                item
            )

            if price is not None:
                return price

        return None

    # Bright Data가 dict로 반환하는 경우
    if not isinstance(data, dict):
        return None

    # ---------------------------------
    # sale_price 우선
    # ---------------------------------

    sale_price = parse_price(
        data.get("sale_price")
    )

    if sale_price is not None:

        print(
            "Bright Data 판매가:",
            sale_price
        )

        return sale_price

    # ---------------------------------
    # price fallback
    # ---------------------------------

    price = parse_price(
        data.get("price")
    )

    if price is not None:

        print(
            "Bright Data 정가:",
            price
        )

        return price

    return None


# =================================
# Bright Data Stylevana
# =================================

def get_stylevana_brightdata_price(
    url
):

    if not BRIGHTDATA_API_KEY:

        print(
            "Bright Data API Key가 없습니다."
        )

        return None

    try:

        print(
            "Bright Data Stylevana 수집:"
        )

        print(
            url
        )

        headers = {
            "Authorization":
                f"Bearer {BRIGHTDATA_API_KEY}",
            "Content-Type":
                "application/json",
        }

        payload = {
            "input": [
                {
                    "url": url
                }
            ],
            "limit_per_input": None
        }

        # =================================
        # Scrape Request
        # =================================

        response = requests.post(
            BRIGHTDATA_SCRAPE_URL,
            params={
                "dataset_id":
                    BRIGHTDATA_DATASET_ID,
                "notify":
                    "false",
                "include_errors":
                    "true",
            },
            headers=headers,
            json=payload,
            timeout=60
        )

        print(
            "Bright Data HTTP:",
            response.status_code
        )

        # =================================
        # Immediate Result
        # =================================

        if response.status_code == 200:

            try:

                data = response.json()

            except Exception:

                print(
                    "Bright Data JSON 변환 실패"
                )

                return None

            price = get_brightdata_price_from_result(
                data
            )

            if price is not None:

                print(
                    "Bright Data 수집 성공:",
                    price
                )

                return price

            print(
                "Bright Data 결과에서 "
                "가격을 찾지 못했습니다."
            )

            return None

        # =================================
        # Async Snapshot
        # =================================

        if response.status_code == 202:

            try:

                result = response.json()

            except Exception:

                print(
                    "Bright Data 202 응답 JSON 실패"
                )

                return None

            snapshot_id = (
                result.get("snapshot_id")
                or result.get("id")
            )

            if not snapshot_id:

                print(
                    "Bright Data snapshot ID 없음"
                )

                return None

            print(
                "Bright Data Snapshot:",
                snapshot_id
            )

            # 최대 약 60초
            for attempt in range(12):

                time.sleep(5)

                snapshot_response = requests.get(
                    f"{BRIGHTDATA_SNAPSHOT_URL}"
                    f"{snapshot_id}",
                    headers=headers,
                    timeout=30
                )

                print(
                    f"Bright Data Snapshot "
                    f"{attempt + 1}/12:",
                    snapshot_response.status_code
                )

                if snapshot_response.status_code != 200:

                    continue

                try:

                    snapshot_data = (
                        snapshot_response.json()
                    )

                except Exception:

                    continue

                price = (
                    get_brightdata_price_from_result(
                        snapshot_data
                    )
                )

                if price is not None:

                    print(
                        "Bright Data 수집 성공:",
                        price
                    )

                    return price

                # 데이터가 아직 처리 중인 경우
                if isinstance(
                    snapshot_data,
                    dict
                ):

                    status = str(
                        snapshot_data.get(
                            "status",
                            ""
                        )
                    ).lower()

                    if status in (
                        "failed",
                        "error",
                        "cancelled"
                    ):

                        print(
                            "Bright Data Snapshot 실패:",
                            status
                        )

                        return None

            print(
                "Bright Data Snapshot "
                "시간 초과"
            )

            return None

        # =================================
        # Other HTTP Error
        # =================================

        print(
            "Bright Data 오류:",
            response.text[:500]
        )

        return None

    except requests.RequestException as e:

        print(
            "Bright Data 요청 오류:",
            e
        )

        return None

    except Exception as e:

        print(
            "Bright Data 수집 오류:",
            e
        )

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

            items = []

            if isinstance(data, list):

                items = data

            elif isinstance(data, dict):

                items = [data]

                graph = data.get("@graph")

                if isinstance(graph, list):

                    items.extend(graph)

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
                    offers.get(
                        "price"
                    )
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
# Stylevana Listing Fallback
# =================================

def get_stylevana_listing_price(url):

    url_lower = str(url).lower()

    if not (
        "celimax" in url_lower
        and "retinal" in url_lower
        and "tightening" in url_lower
        and "booster" in url_lower
    ):

        return None

    target_regex = re.compile(
        r"CELIMAX\s*-\s*The\s+Vita-A\s+Retinal\s+Shot\s+"
        r"Tightening\s+Booster\s*-\s*15ml",
        re.IGNORECASE
    )

    listing_urls = [
        (
            "https://www.stylevana.com/en_US/"
            "skincare/face-care/spot-treatment.html"
        ),
        "https://www.stylevana.com/en_US/vip-sale",
        (
            "https://www.stylevana.com/en_US/"
            "vana-award.html"
        ),
    ]

    listing_headers = dict(
        HEADERS
    )

    listing_headers["Referer"] = (
        "https://www.stylevana.com/en_US/"
    )

    for listing_url in listing_urls:

        try:

            print(
                "Stylevana 리스트 백업 확인:",
                listing_url
            )

            response = requests.get(
                listing_url,
                headers=listing_headers,
                timeout=20
            )

            print(
                "Stylevana 리스트 HTTP:",
                response.status_code
            )

            if response.status_code != 200:

                continue

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            nodes = soup.find_all(
                string=target_regex
            )

            for node in nodes:

                current = node.parent

                for _ in range(8):

                    if current is None:

                        break

                    block_text = current.get_text(
                        " ",
                        strip=True
                    )

                    if target_regex.search(
                        block_text
                    ):

                        price_match = re.search(
                            r"(?:Price|price)"
                            r"\s*[:$]?\s*\$?\s*"
                            r"(\d+(?:\.\d+)?)",
                            block_text,
                            re.IGNORECASE
                        )

                        if price_match:

                            price = parse_price(
                                price_match.group(1)
                            )

                            if price is not None:

                                print(
                                    "Stylevana 리스트 수집 성공:",
                                    price
                                )

                                return price

                    current = current.parent

        except Exception as e:

            print(
                "Stylevana 리스트 수집 오류:",
                e
            )

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

    print(
        ""
    )

    print(
        "================================="
    )

    print(
        "STYLEVANA PRICE COLLECTION"
    )

    print(
        "================================="
    )

    print(
        "URL:",
        url
    )

    # =================================
    # 1. Bright Data
    # =================================

    print(
        ""
    )

    print(
        "[1] Bright Data 확인"
    )

    price = get_stylevana_brightdata_price(
        url
    )

    if price is not None:

        print(
            "Stylevana Bright Data 가격 사용:",
            price
        )

        return price

    # =================================
    # 2. Direct
    # =================================

    print(
        ""
    )

    print(
        "[2] Stylevana 직접 수집"
    )

    price = get_stylevana_direct_price(
        url
    )

    if price is not None:

        return price

    # =================================
    # 3. Existing Feed
    # =================================

    print(
        ""
    )

    print(
        "[3] Stylevana Feed 백업 확인"
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

    # =================================
    # 4. Listing Fallback
    # =================================

    print(
        ""
    )

    print(
        "[4] Stylevana 리스트 페이지 "
        "백업 확인"
    )

    price = get_stylevana_listing_price(
        url
    )

    if price is not None:

        print(
            "Stylevana 리스트 가격 사용:",
            price
        )

        return price

    # =================================
    # Failed
    # =================================

    print(
        ""
    )

    print(
        "Stylevana 가격을 수집하지 못했습니다."
    )

    return None