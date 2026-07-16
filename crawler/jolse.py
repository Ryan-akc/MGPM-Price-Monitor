import requests
from bs4 import BeautifulSoup
import re


def get_jolse_price(url):

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }


    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )


        print("상태코드:", response.status_code)


        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        # 페이지 내 가격 관련 태그 탐색
        for tag in soup.find_all(
            string=re.compile(r"\$|USD|price", re.I)
        ):

            text = tag.strip()

            print(
                "찾은 문자열:",
                text[:100]
            )


        # 숫자 패턴 전체 검색
        prices = re.findall(
            r"(?:\$|USD\s?)\s?([0-9]+\.[0-9]{2})",
            response.text
        )


        if prices:

            return float(
                prices[0]
            )


        return None


    except Exception as e:

        print(
            "오류:",
            e
        )

        return None