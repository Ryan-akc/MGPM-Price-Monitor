from playwright.sync_api import sync_playwright
import re


# =================================
# Coupang CDP Settings
# =================================

CDP_URL = "http://127.0.0.1:9222"


# =================================
# Coupang Price Crawler
# =================================

def get_coupang_price(url):

    print("Coupang 가격 수집 시작...")
    print("URL:", url)

    try:

        with sync_playwright() as p:

            # =================================
            # Chrome CDP 연결
            # =================================

            print(
                "Coupang Chrome CDP 연결 시도..."
            )

            browser = (
                p.chromium.connect_over_cdp(
                    CDP_URL
                )
            )

            print(
                "✅ Coupang Chrome CDP 연결 성공"
            )

            # =================================
            # Browser Context
            # =================================

            contexts = browser.contexts

            if not contexts:

                print(
                    "❌ Chrome Browser Context 없음"
                )

                return None

            context = contexts[0]

            # =================================
            # 기존 Page 검색
            # =================================

            page = None

            for existing_page in context.pages:

                try:

                    if (
                        "coupang.com"
                        in existing_page.url.lower()
                    ):

                        page = existing_page

                        break

                except Exception:

                    continue

            # =================================
            # 새 Page
            # =================================

            if page is None:

                page = context.new_page()

            # =================================
            # Coupang 접속
            # =================================

            print(
                "Coupang 페이지 접속..."
            )

            try:

                response = page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=30000,
                )

            except Exception as e:

                print(
                    "Coupang 페이지 이동 오류:",
                    e
                )

                # 이동 오류가 있어도
                # 현재 Chrome 페이지가
                # 정상적으로 열렸을 수 있으므로
                # 계속 확인

                response = None

            # =================================
            # 페이지 로딩
            # =================================

            page.wait_for_timeout(
                5000
            )

            # =================================
            # Page Information
            # =================================

            print(
                "Coupang Final URL:",
                page.url
            )

            try:

                print(
                    "Coupang Page Title:",
                    page.title()
                )

            except Exception:

                pass

            # =================================
            # Access Denied 확인
            # =================================

            try:

                body_text = (
                    page
                    .locator("body")
                    .inner_text()
                    .strip()
                )

            except Exception:

                body_text = ""

            body_lower = body_text.lower()

            if (
                "access denied"
                in body_lower
                or "accessdenied"
                in body_lower
            ):

                print(
                    "❌ Coupang Access Denied"
                )

                return None

            # =================================
            # Price Selectors
            # =================================

            selectors = [

                "strong.total-price",

                "strong.prod-price",

                ".prod-buy-header__price strong",

                ".prod-price .total-price strong",

                ".prod-buy-header__price",

                ".total-price",

                "[class*='total-price']",

                "[class*='prod-price']",

            ]

            price_text = None

            for selector in selectors:

                try:

                    locator = (
                        page
                        .locator(selector)
                        .first
                    )

                    if locator.count() == 0:

                        continue

                    text = locator.inner_text(
                        timeout=3000
                    ).strip()

                    if not text:

                        continue

                    print(
                        "Coupang 가격 영역 발견:",
                        selector,
                        "=>",
                        text
                    )

                    price_text = text

                    break

                except Exception:

                    continue

            # =================================
            # Body 가격 검색
            # =================================

            if not price_text:

                patterns = [

                    r"([0-9][0-9,]*)\s*원",

                    r"₩\s*([0-9][0-9,]*)",

                ]

                for pattern in patterns:

                    match = re.search(
                        pattern,
                        body_text
                    )

                    if match:

                        price_text = (
                            match.group(1)
                        )

                        print(
                            "Coupang 가격 발견:",
                            price_text
                        )

                        break

            # =================================
            # 가격 없음
            # =================================

            if not price_text:

                print(
                    "❌ Coupang 가격을 찾지 못했습니다."
                )

                return None

            # =================================
            # 숫자 추출
            # =================================

            numbers = re.findall(
                r"[0-9][0-9,]*",
                price_text
            )

            if not numbers:

                print(
                    "❌ Coupang 가격 숫자 변환 실패:",
                    price_text
                )

                return None

            price = float(
                numbers[0].replace(
                    ",",
                    ""
                )
            )

            # =================================
            # 가격 검증
            # =================================

            if price <= 0:

                print(
                    "❌ 비정상 Coupang 가격:",
                    price
                )

                return None

            # =================================
            # 완료
            # =================================

            print(
                f"✅ Coupang 현재 가격: "
                f"₩{price:,.0f}"
            )

            return price

    except Exception as e:

        print(
            "❌ Coupang CDP 수집 오류:",
            e
        )

        return None