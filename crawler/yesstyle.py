import re
from playwright.sync_api import sync_playwright


# =================================
# YesStyle Price - US Region
# =================================

def get_yesstyle_price(url):

    print("=" * 60)
    print("YesStyle 가격 수집 시작 (US 기준)")
    print(f"URL: {url}")

    browser = None
    price = None
    api_found = False
    api_count = 0

    # URL에서 대상 상품 ID 확인
    pid_match = re.search(r"/pid\.(\d+)", url)

    if not pid_match:
        print("❌ URL에서 YesStyle 상품 ID를 찾을 수 없습니다.")
        print("=" * 60)
        return None

    expected_pid = pid_match.group(1)
    print(f"Target Product ID: {expected_pid}")

    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                locale="en-US",
                viewport={
                    "width": 1366,
                    "height": 900
                },
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9"
                }
            )

            page = context.new_page()

            # =================================
            # API Request Interception
            # =================================

            def set_us_region(route):

                request = route.request

                try:
                    payload = request.post_data_json

                    if not isinstance(payload, dict):
                        print("⚠ YesStyle 요청 데이터 형식 오류")
                        route.continue_()
                        return

                    request_pid = str(payload.get("pid", ""))

                    if request_pid != expected_pid:
                        print(
                            "⚠ 요청 상품 ID 불일치: "
                            f"{request_pid}"
                        )
                        route.continue_()
                        return

                    payload["countryId"] = 226
                    payload["currencyCode"] = "USD"

                    print(
                        "YesStyle 요청 지역 설정: "
                        "countryId=226, currencyCode=USD"
                    )

                    route.continue_(
                        post_data=__import__("json").dumps(payload)
                    )

                except Exception as e:
                    print(f"⚠ YesStyle 요청 변경 오류: {e}")
                    route.continue_()

            page.route(
                "**/api/public/gtm/pgtmdl",
                set_us_region
            )

            # =================================
            # API Response Handler
            # =================================

            def handle_response(response):

                nonlocal price
                nonlocal api_found
                nonlocal api_count

                if "/api/public/gtm/pgtmdl" not in response.url:
                    return

                api_found = True
                api_count += 1

                print(f"YesStyle API 응답 발견 [{api_count}]")

                try:
                    if response.status != 200:
                        print(
                            "⚠ API HTTP 오류: "
                            f"{response.status}"
                        )
                        return

                    data = response.json()

                    if not isinstance(data, dict):
                        print("⚠ API 응답 형식 오류")
                        return

                    data_layer = data.get("dataLayerMapping")

                    if not isinstance(data_layer, dict):
                        print("⚠ dataLayerMapping 형식 오류")
                        return

                    # 상품 ID 검증
                    response_pid = str(
                        data_layer.get("product_sku", "")
                    )

                    if response_pid != expected_pid:
                        print(
                            "⚠ 상품 ID 불일치 - 가격 사용 중단: "
                            f"{response_pid}"
                        )
                        return

                    # 통화 검증
                    currency = str(
                        data_layer.get("site_currency", "")
                    ).upper()

                    if currency != "USD":
                        print(
                            "⚠ USD 응답이 아닙니다. "
                            f"통화: {currency}"
                        )
                        return

                    # 실제 판매가 우선
                    candidates = [
                        (
                            "product_price",
                            data_layer.get("product_price")
                        ),
                        (
                            "ga4_value",
                            data_layer.get("ga4_value")
                        )
                    ]

                    for source, value in candidates:

                        if value is None:
                            continue

                        try:
                            detected_price = float(
                                str(value)
                                .replace(",", "")
                                .strip()
                            )

                            if detected_price <= 0:
                                continue

                            price = detected_price

                            print(
                                f"✅ 가격 추출 성공 | "
                                f"{source}: {price:.2f} USD"
                            )

                            return

                        except (TypeError, ValueError):
                            print(
                                f"⚠ {source} 가격 변환 실패: "
                                f"{value}"
                            )

                    print("⚠ 유효한 USD 가격을 찾지 못했습니다.")

                except Exception as e:
                    print(f"❌ YesStyle API 응답 분석 오류: {e}")

            page.on("response", handle_response)

            # =================================
            # Page Access
            # =================================

            print("YesStyle 페이지 접속 중...")

            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            if response:
                print(
                    f"YesStyle HTTP Status: {response.status}"
                )

            else:
                print("⚠ YesStyle HTTP Response 없음")

            # API 응답 대기
            page.wait_for_timeout(7000)

            # 페이지 정보
            try:
                print(f"YesStyle Final URL: {page.url}")
                print(f"YesStyle Page Title: {page.title()}")

            except Exception as e:
                print(f"페이지 정보 확인 오류: {e}")

            # 추가 API 호출 확인
            try:
                page.evaluate(
                    "window.scrollTo(0, document.body.scrollHeight)"
                )
                page.wait_for_timeout(3000)

            except Exception as e:
                print(f"YesStyle Scroll 오류: {e}")

            # =================================
            # Result
            # =================================

            if price is not None:

                print(
                    f"✅ 최종 YesStyle 가격: {price:.2f} USD"
                )
                print("=" * 60)

                return price

            print("❌ YesStyle 가격 추출 실패")

            if not api_found:
                print("Reason: pgtmdl API 응답을 찾지 못했습니다.")
            else:
                print(
                    f"Reason: API {api_count}건을 확인했으나 "
                    "상품 ID, USD 통화 또는 가격 검증 실패"
                )

            print("=" * 60)
            return None

    except Exception as e:

        print(f"❌ YesStyle 크롤링 오류: {e}")
        print("=" * 60)
        return None

    finally:

        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass