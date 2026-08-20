from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import re


URL = "https://www.stylevana.com/en_US/mary-may-tranexamic-acid-glutathione-eye-cream-30g9268.html"


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

        if price <= 0:
            return None

        return price

    except (
        TypeError,
        ValueError
    ):

        return None


def find_jsonld_price(soup):

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:

            text = script.string

            if not text:
                continue

            data = json.loads(text)

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

                if currency != "USD":
                    continue

                price = parse_price(
                    offers.get("price")
                )

                if price is not None:
                    return price

        except Exception:
            continue

    return None


def find_html_price(page):

    selectors = [

        "[itemprop='price']",

        ".special-price .price",

        ".product-info-price .price",

        ".price-box .special-price .price",

        ".price-final_price .price",

        ".product-price .price",

        ".price-box .price",

    ]

    for selector in selectors:

        try:

            locator = page.locator(
                selector
            )

            count = locator.count()

            for i in range(count):

                element = locator.nth(i)

                text = element.inner_text(
                    timeout=3000
                )

                price = parse_price(
                    text
                )

                if price is not None:
                    return price

        except Exception:
            continue

    return None


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
        locale="en-US"
    )

    print()
    print("=" * 60)
    print("STYLEVANA PLAYWRIGHT 가격 테스트")
    print("=" * 60)

    try:

        response = page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        if response:

            print(
                "HTTP 상태:",
                response.status
            )

        print(
            "최종 URL:",
            page.url
        )

        print(
            "페이지 로딩 대기..."
        )

        page.wait_for_timeout(
            7000
        )

        soup = BeautifulSoup(
            page.content(),
            "html.parser"
        )

        # =========================
        # 1. JSON-LD
        # =========================

        price = find_jsonld_price(
            soup
        )

        if price is not None:

            print()
            print(
                "가격 추출 성공 (JSON-LD):",
                price
            )

        # =========================
        # 2. HTML
        # =========================

        if price is None:

            price = find_html_price(
                page
            )

            if price is not None:

                print()
                print(
                    "가격 추출 성공 (HTML):",
                    price
                )

        # =========================
        # Result
        # =========================

        print()
        print("-" * 60)

        if price is not None:

            print(
                "최종 가격:",
                price,
                "USD"
            )

            print(
                "RESULT: SUCCESS"
            )

        else:

            print(
                "가격을 찾지 못했습니다."
            )

            print(
                "RESULT: FAILED"
            )

        print("-" * 60)

        print()
        print(
            "브라우저를 5초 후 종료합니다."
        )

        page.wait_for_timeout(
            5000
        )

    except Exception as e:

        print()
        print(
            "Stylevana 테스트 오류:",
            e
        )

    finally:

        browser.close()