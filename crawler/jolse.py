import requests
import re


# =================================
# Jolse Price
# =================================

def get_jolse_price(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        )
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        # =================================
        # Price Extraction
        # =================================

        prices = re.findall(
            r"(?:\$|USD\s?)\s?([0-9]+\.[0-9]{2})",
            response.text
        )

        if prices:

            return float(
                prices[0]
            )

        print(
            "Jolse 가격 추출 실패"
        )

        return None

    except requests.RequestException as e:

        print(
            f"Jolse 요청 오류: {e}"
        )

        return None

    except Exception as e:

        print(
            f"Jolse 오류: {e}"
        )

        return None