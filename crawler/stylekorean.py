import re
import requests


# =================================
# StyleKorean Headers
# =================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0.0.0 "
        "Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# =================================
# Parse StyleKorean Price
# =================================

def parse_stylekorean_price(html):

    if not html:
        return None

    # =================================
    # JSON Price
    # =================================

    patterns = [

        r'"price"\s*:\s*"([0-9]+(?:\.[0-9]+)?)"',

        r'"price"\s*:\s*([0-9]+(?:\.[0-9]+)?)',

        r'"lowPrice"\s*:\s*"([0-9]+(?:\.[0-9]+)?)"',

        r'"lowPrice"\s*:\s*([0-9]+(?:\.[0-9]+)?)',

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            re.IGNORECASE
        )

        if not match:
            continue

        try:

            price = float(
                match.group(1)
            )

            if price > 0:
                return price

        except (
            TypeError,
            ValueError
        ):

            continue

    # =================================
    # StyleKorean PRICE
    # =================================

    patterns = [

        r'PRICE\s*</?\w*[^>]*>\s*'
        r'([0-9]+(?:\.[0-9]+)?)\s*USD',

        r'PRICE\s+'
        r'([0-9]+(?:\.[0-9]+)?)\s*USD',

        r'PRICE[^0-9]{0,100}'
        r'([0-9]+(?:\.[0-9]+)?)\s*USD',

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            html,
            re.IGNORECASE
        )

        if not match:
            continue

        try:

            price = float(
                match.group(1)
            )

            if price > 0:
                return price

        except (
            TypeError,
            ValueError
        ):

            continue

    # =================================
    # USD Fallback
    # =================================

    matches = re.findall(
        r'([0-9]+(?:\.[0-9]+)?)\s*USD',
        html,
        re.IGNORECASE
    )

    for value in matches:

        try:

            price = float(value)

            if price > 0:
                return price

        except (
            TypeError,
            ValueError
        ):

            continue

    return None


# =================================
# Get StyleKorean Price
# =================================

def get_stylekorean_price(url):

    if not url:
        return None

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        price = parse_stylekorean_price(
            response.text
        )

        if price is None:

            print(
                f"StyleKorean 가격 추출 실패: "
                f"{url}"
            )

            return None

        print(
            f"StyleKorean 가격: "
            f"${price:.2f}"
        )

        return price

    except requests.RequestException as e:

        print(
            f"StyleKorean 요청 오류: {e}"
        )

        return None

    except Exception as e:

        print(
            f"StyleKorean 수집 오류: {e}"
        )

        return None