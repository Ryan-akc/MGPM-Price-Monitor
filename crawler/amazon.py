import re
import time
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


# ============================================================
# Amazon CDP Settings
# ============================================================

CDP_URL = "http://127.0.0.1:9222"
AMAZON_TIMEOUT = 30000

# Amazon US 배송지
AMAZON_US_ZIP = "10001"
AMAZON_US_CITY = "New York"


# ============================================================
# Utility
# ============================================================

def extract_dollar_prices(text):

    if not text:
        return []

    matches = re.findall(
        r"\$\s*([0-9][0-9,]*\.\d{2})",
        text
    )

    prices = []

    for value in matches:

        try:
            prices.append(
                float(
                    value.replace(",", "")
                )
            )

        except Exception:
            continue

    return prices


def is_amazon_url(url):

    if not url:
        return False

    try:
        host = urlparse(url).netloc.lower()

    except Exception:
        return False

    return host in (
        "amazon.com",
        "www.amazon.com",
    )


def extract_amazon_asin(url):

    if not url:
        return None

    patterns = [
        r"/dp/([A-Z0-9]{10})",
        r"/gp/product/([A-Z0-9]{10})",
        r"/gp/aw/d/([A-Z0-9]{10})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            url,
            re.IGNORECASE
        )

        if match:

            return match.group(1).upper()

    return None


def is_blocked_page(page):

    try:

        title = (
            page.title()
            or ""
        ).lower()

    except Exception:

        title = ""

    try:

        body = (
            page.locator("body")
            .inner_text(timeout=5000)
            or ""
        ).lower()

    except Exception:

        body = ""

    blocked_keywords = [
        "captcha",
        "robot check",
        "enter the characters you see below",
        "sorry, we just need to make sure you're not a robot",
        "automated access",
        "verify you're human",
        "type the characters",
    ]

    combined = f"{title}\n{body}"

    for keyword in blocked_keywords:

        if keyword in combined:

            return True

    return False


# ============================================================
# Amazon US Delivery Location
# ============================================================

def get_amazon_delivery_text(page):

    try:

        body = (
            page.locator("body")
            .inner_text(timeout=5000)
            or ""
        )

        return body.replace(
            "\u200c",
            " "
        )

    except Exception:

        return ""


def is_amazon_us_location_correct(page):

    body = get_amazon_delivery_text(page)

    if not body:

        return False

    normalized = body.lower()

    has_deliver_to = (
        "deliver to" in normalized
    )

    has_zip = (
        AMAZON_US_ZIP in body
    )

    has_city = (
        AMAZON_US_CITY.lower()
        in normalized
    )

    return (
        has_deliver_to
        and has_zip
        and has_city
    )


def set_amazon_us_location(page):

    """
    Amazon 배송지를 New York 10001로 자동 설정

    이미 정확한 경우:
        변경하지 않음

    다른 배송지인 경우:
        Deliver to 클릭
        ZIP 10001 입력
        Done 클릭
        최종 배송지 재확인
    """

    # --------------------------------------------------------
    # 이미 정확한 배송지인지 확인
    # --------------------------------------------------------

    if is_amazon_us_location_correct(page):

        print(
            "✅ Amazon US 배송지 확인: "
            f"{AMAZON_US_CITY} {AMAZON_US_ZIP}"
        )

        return True

    print(
        "⚠️ Amazon 배송지가 "
        f"{AMAZON_US_CITY} {AMAZON_US_ZIP}가 아닙니다."
    )

    try:

        # ----------------------------------------------------
        # Deliver to 클릭
        # ----------------------------------------------------

        deliver = page.get_by_text(
            "Deliver to",
            exact=True
        )

        if deliver.count() == 0:

            print(
                "❌ Amazon Deliver to 요소를 "
                "찾지 못했습니다."
            )

            return False

        clicked = False

        for i in range(deliver.count()):

            try:

                if deliver.nth(i).is_visible():

                    deliver.nth(i).click(
                        timeout=10000
                    )

                    clicked = True

                    break

            except Exception:

                continue

        if not clicked:

            print(
                "❌ Amazon 배송지 버튼 클릭 실패"
            )

            return False

        # ----------------------------------------------------
        # 배송지 팝업 대기
        # ----------------------------------------------------

        page.wait_for_timeout(1000)

        # ----------------------------------------------------
        # ZIP 입력
        # ----------------------------------------------------

        zip_input = page.locator(
            "#GLUXZipUpdateInput"
        )

        if zip_input.count() == 0:

            print(
                "❌ Amazon ZIP 입력창을 "
                "찾지 못했습니다."
            )

            return False

        zip_input.fill(
            AMAZON_US_ZIP
        )

        print(
            "📍 Amazon 배송지 ZIP 입력: "
            f"{AMAZON_US_ZIP}"
        )

        # ----------------------------------------------------
        # Done 버튼
        # ----------------------------------------------------

        done = page.get_by_role(
            "button",
            name="Done",
            exact=True
        )

        if done.count() == 0:

            print(
                "❌ Amazon 배송지 Done 버튼을 "
                "찾지 못했습니다."
            )

            return False

        clicked_done = False

        for i in range(done.count()):

            try:

                if done.nth(i).is_visible():

                    done.nth(i).click(
                        timeout=10000
                    )

                    clicked_done = True

                    break

            except Exception:

                continue

        if not clicked_done:

            print(
                "❌ Amazon 배송지 Done 클릭 실패"
            )

            return False

        # ----------------------------------------------------
        # Amazon 배송지 적용 대기
        # ----------------------------------------------------

        page.wait_for_timeout(3000)

        # ----------------------------------------------------
        # 최종 배송지 확인
        # ----------------------------------------------------

        if is_amazon_us_location_correct(page):

            print(
                "✅ Amazon 배송지 자동 설정 완료: "
                f"{AMAZON_US_CITY} {AMAZON_US_ZIP}"
            )

            return True

        print(
            "❌ Amazon 배송지 자동 설정 후 "
            "New York 10001 확인 실패"
        )

        return False

    except Exception as e:

        print(
            f"❌ Amazon 배송지 자동 설정 오류: {e}"
        )

        return False


def ensure_amazon_us_location(page):

    """
    기존 함수명 유지.

    자동으로 New York 10001 배송지를 보장합니다.
    """

    return set_amazon_us_location(page)


# ============================================================
# Price Extraction
# ============================================================

def extract_current_amazon_price(page):

    """
    Amazon 현재 판매가격 추출

    우선순위:

    1. Buy Box
    2. Apex Desktop
    3. One-time purchase
    4. 기타 current price 영역

    단위 가격 제외
    Subscribe & Save 제외
    """

    # --------------------------------------------------------
    # 1. Buy Box
    # --------------------------------------------------------

    buybox_selectors = [
        "#buybox",
        "#buybox_feature_div",
        "#desktop_buybox",
    ]

    for selector in buybox_selectors:

        try:

            locator = page.locator(
                selector
            )

            if locator.count() == 0:
                continue

            text = locator.inner_text(
                timeout=3000
            )

            if not text:
                continue

            # ------------------------------------------------
            # One-time purchase 우선
            # ------------------------------------------------

            one_time_match = re.search(
                r"One-time purchase.*?\$?\s*"
                r"([0-9][0-9,]*\.\d{2})",
                text,
                re.IGNORECASE | re.DOTALL
            )

            if one_time_match:

                price = float(
                    one_time_match.group(1)
                    .replace(",", "")
                )

                print(
                    f"Amazon Buy Box 현재 판매가: "
                    f"${price:.2f}"
                )

                return price

            # ------------------------------------------------
            # Buy Box 가격
            # ------------------------------------------------

            lines = text.splitlines()

            for line in lines:

                line = line.strip()

                if not line:
                    continue

                lower = line.lower()

                if "per ounce" in lower:
                    continue

                if "/ ounce" in lower:
                    continue

                if "subscribe" in lower:
                    continue

                match = re.fullmatch(
                    r"\$\s*"
                    r"([0-9][0-9,]*\.\d{2})",
                    line
                )

                if match:

                    price = float(
                        match.group(1)
                        .replace(",", "")
                    )

                    print(
                        f"Amazon Buy Box 현재 판매가: "
                        f"${price:.2f}"
                    )

                    return price

        except Exception:

            continue

    # --------------------------------------------------------
    # 2. Apex Desktop
    # --------------------------------------------------------

    apex_selectors = [
        "#apex_desktop",
        "#apex_desktop_new",
        "#apex_mobile",
    ]

    for selector in apex_selectors:

        try:

            locator = page.locator(
                selector
            )

            if locator.count() == 0:
                continue

            text = locator.inner_text(
                timeout=3000
            )

            if not text:
                continue

            lines = text.splitlines()

            for line in lines:

                line = line.strip()

                if not line:
                    continue

                lower = line.lower()

                if "per ounce" in lower:
                    continue

                if "/ ounce" in lower:
                    continue

                if "per count" in lower:
                    continue

                if "per unit" in lower:
                    continue

                if "upon approval" in lower:
                    continue

                match = re.fullmatch(
                    r"\$\s*"
                    r"([0-9][0-9,]*\.\d{2})",
                    line
                )

                if match:

                    price = float(
                        match.group(1)
                        .replace(",", "")
                    )

                    print(
                        f"Amazon Apex 현재 판매가: "
                        f"${price:.2f}"
                    )

                    return price

        except Exception:

            continue

    # --------------------------------------------------------
    # 3. Price block
    # --------------------------------------------------------

    selectors = [
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#priceblock_saleprice",
        "#price_inside_buybox",
        ".a-price.aok-align-center .a-offscreen",
        ".a-price .a-offscreen",
    ]

    for selector in selectors:

        try:

            elements = page.locator(
                selector
            )

            count = elements.count()

            for i in range(
                min(count, 10)
            ):

                text = elements.nth(i).inner_text(
                    timeout=3000
                )

                if not text:
                    continue

                lower = text.lower()

                if "per ounce" in lower:
                    continue

                if "/ ounce" in lower:
                    continue

                prices = extract_dollar_prices(
                    text
                )

                if prices:

                    price = prices[0]

                    print(
                        f"Amazon 가격 selector 추출: "
                        f"${price:.2f}"
                    )

                    return price

        except Exception:

            continue

    return None


# ============================================================
# Main Collector
# ============================================================

def get_amazon_price(url, asin=None):

    """
    Amazon US 현재 판매가격 수집

    수집 순서:

    1. Amazon US URL 확인
    2. ASIN 확인
    3. CDP 연결
    4. Amazon 탭 재사용
    5. 상품 URL 이동
    6. CAPTCHA 확인
    7. 배송지 New York 10001 자동 설정
    8. 현재 판매가격 추출
    """

    print(
        "Amazon 가격 수집 시작..."
    )

    if not url:

        print(
            "⚠️ Amazon URL이 없습니다."
        )

        return None

    # --------------------------------------------------------
    # Amazon US URL 확인
    # --------------------------------------------------------

    if not is_amazon_url(url):

        print(
            f"⚠️ Amazon US URL이 아닙니다: {url}"
        )

        return None

    # --------------------------------------------------------
    # ASIN 확인
    # --------------------------------------------------------

    url_asin = extract_amazon_asin(
        url
    )

    if url_asin:

        print(
            f"Amazon ASIN: {url_asin}"
        )

    if asin:

        requested_asin = str(
            asin
        ).strip().upper()

        if url_asin and url_asin != requested_asin:

            print(
                "⚠️ Amazon ASIN 불일치: "
                f"URL={url_asin} / "
                f"요청={requested_asin}"
            )

            return None

    with sync_playwright() as p:

        browser = None

        try:

            # ------------------------------------------------
            # CDP 연결
            # ------------------------------------------------

            print(
                "Amazon CDP 연결 시도..."
            )

            browser = p.chromium.connect_over_cdp(
                CDP_URL,
                timeout=10000
            )

            print(
                "✅ Amazon CDP 연결 성공"
            )

            # ------------------------------------------------
            # Context
            # ------------------------------------------------

            contexts = browser.contexts

            if not contexts:

                print(
                    "⚠️ Chrome Browser Context를 "
                    "찾지 못했습니다."
                )

                return None

            context = contexts[0]

            # ------------------------------------------------
            # Amazon 기존 탭 재사용
            # ------------------------------------------------

            page = None

            for existing_page in context.pages:

                try:

                    existing_url = (
                        existing_page.url
                        or ""
                    )

                    if "amazon.com" in existing_url:

                        page = existing_page

                        break

                except Exception:

                    continue

            # ------------------------------------------------
            # Amazon 탭이 없으면 새 탭
            # ------------------------------------------------

            if page is None:

                page = context.new_page()

                print(
                    "Amazon 새 탭 생성"
                )

            # ------------------------------------------------
            # 지정된 상품 URL 이동
            # ------------------------------------------------

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=AMAZON_TIMEOUT
            )

            time.sleep(3)

            print(
                f"Amazon 상품 페이지: {page.url}"
            )

            # ------------------------------------------------
            # CAPTCHA 확인
            # ------------------------------------------------

            if is_blocked_page(page):

                print(
                    "🚫 Amazon CAPTCHA/Bot Check 감지"
                )

                return None

            # ------------------------------------------------
            # 배송지 자동 설정
            # ------------------------------------------------

            if not ensure_amazon_us_location(
                page
            ):

                print(
                    "🚫 Amazon US 배송지 검증 실패"
                )

                print(
                    "필요 배송지: "
                    f"{AMAZON_US_CITY} "
                    f"{AMAZON_US_ZIP}"
                )

                return None

            # ------------------------------------------------
            # 가격 추출
            # ------------------------------------------------

            price = extract_current_amazon_price(
                page
            )

            if price is not None:

                print(
                    f"✅ Amazon 현재 판매가격: "
                    f"${price:.2f}"
                )

                return price

            # ------------------------------------------------
            # 한 번 더 대기 후 재시도
            # ------------------------------------------------

            time.sleep(2)

            if is_blocked_page(page):

                print(
                    "🚫 Amazon CAPTCHA/Bot Check 감지"
                )

                return None

            if not ensure_amazon_us_location(
                page
            ):

                print(
                    "🚫 Amazon US 배송지 "
                    "재검증 실패"
                )

                return None

            price = extract_current_amazon_price(
                page
            )

            if price is not None:

                print(
                    f"✅ Amazon 현재 판매가격: "
                    f"${price:.2f}"
                )

                return price

            print(
                "⚠️ Amazon 페이지에서 "
                "현재 판매가격을 찾지 못했습니다."
            )

            return None

        except Exception as e:

            print(
                f"❌ Amazon CDP 수집 오류: {e}"
            )

            return None

        finally:

            # ------------------------------------------------
            # CDP 연결만 종료
            # 실제 Chrome은 종료하지 않음
            # ------------------------------------------------

            try:

                if browser:
                    browser.close()

            except Exception:

                pass