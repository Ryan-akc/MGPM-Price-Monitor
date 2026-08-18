from playwright.sync_api import sync_playwright


# =================================
# YesStyle Price
# =================================

def get_yesstyle_price(url):

    print("=" * 60)
    print("YesStyle 가격 수집 시작")
    print(f"URL: {url}")

    browser = None

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True
            )

            context = browser.new_context(

                locale="en-US",

                viewport={
                    "width": 1366,
                    "height": 900
                },

                extra_http_headers={
                    "Accept-Language":
                        "en-US,en;q=0.9"
                }

            )

            page = context.new_page()

            price = None
            api_found = False
            api_count = 0

            # =================================
            # API Response Handler
            # =================================

            def handle_response(response):

                nonlocal price
                nonlocal api_found
                nonlocal api_count

                if (
                    "/api/public/gtm/pgtmdl"
                    not in response.url
                ):
                    return

                api_found = True
                api_count += 1

                print(
                    f"YesStyle API 발견 "
                    f"[{api_count}]: {response.url}"
                )

                try:

                    data = response.json()

                    if not isinstance(
                        data,
                        dict
                    ):

                        print(
                            "⚠ YesStyle API 응답이 "
                            "dict 형식이 아닙니다."
                        )

                        return

                    data_layer = data.get(
                        "dataLayerMapping",
                        {}
                    )

                    if not isinstance(
                        data_layer,
                        dict
                    ):

                        print(
                            "⚠ dataLayerMapping 형식 오류"
                        )

                        return

                    # =================================
                    # Actual Selling Price
                    #
                    # ecommerce.detail.products[].price
                    # =================================

                    ecommerce = data_layer.get(
                        "ecommerce",
                        {}
                    )

                    if isinstance(
                        ecommerce,
                        dict
                    ):

                        detail = ecommerce.get(
                            "detail",
                            {}
                        )

                        if isinstance(
                            detail,
                            dict
                        ):

                            products = detail.get(
                                "products",
                                []
                            )

                            if isinstance(
                                products,
                                list
                            ):

                                for index, product in enumerate(
                                    products
                                ):

                                    if not isinstance(
                                        product,
                                        dict
                                    ):
                                        continue

                                    value = product.get(
                                        "price"
                                    )

                                    print(
                                        f"YesStyle Actual Product "
                                        f"[{index}] | "
                                        f"Price: {value}"
                                    )

                                    if value is None:
                                        continue

                                    try:

                                        detected_price = float(
                                            str(value)
                                            .replace(",", "")
                                            .strip()
                                        )

                                        if detected_price > 0:

                                            price = (
                                                detected_price
                                            )

                                            print(
                                                f"✅ YesStyle 실제 판매가 발견: "
                                                f"{price} USD"
                                            )

                                            return

                                    except (
                                        TypeError,
                                        ValueError
                                    ):

                                        print(
                                            "⚠ YesStyle 실제 판매가 "
                                            "변환 실패: "
                                            f"{value}"
                                        )

                    # =================================
                    # Fallback
                    #
                    # ga4_value
                    # =================================

                    fallback_value = data_layer.get(
                        "ga4_value"
                    )

                    if fallback_value is not None:

                        print(
                            "YesStyle Fallback "
                            f"ga4_value: {fallback_value}"
                        )

                        try:

                            detected_price = float(
                                str(fallback_value)
                                .replace(",", "")
                                .strip()
                            )

                            if detected_price > 0:

                                price = detected_price

                                print(
                                    f"⚠ YesStyle fallback 가격 사용: "
                                    f"{price} USD"
                                )

                                return

                        except (
                            TypeError,
                            ValueError
                        ):

                            print(
                                "⚠ YesStyle ga4_value "
                                f"변환 실패: {fallback_value}"
                            )

                    print(
                        "⚠ YesStyle 실제 판매가를 "
                        "찾지 못했습니다."
                    )

                except Exception as e:

                    print(
                        f"❌ YesStyle API 응답 분석 오류: {e}"
                    )

            # =================================
            # Response Event
            # =================================

            page.on(
                "response",
                handle_response
            )

            # =================================
            # Page Access
            # =================================

            print(
                "YesStyle 페이지 접속 중..."
            )

            response = page.goto(

                url,

                wait_until="domcontentloaded",

                timeout=30000

            )

            if response:

                print(
                    f"YesStyle HTTP Status: "
                    f"{response.status}"
                )

            else:

                print(
                    "⚠ YesStyle HTTP Response 없음"
                )

            # =================================
            # Page Wait
            # =================================

            page.wait_for_timeout(
                7000
            )

            # =================================
            # Page Information
            # =================================

            try:

                print(
                    f"YesStyle Final URL: {page.url}"
                )

                print(
                    f"YesStyle Page Title: "
                    f"{page.title()}"
                )

            except Exception as e:

                print(
                    f"YesStyle Page 정보 확인 오류: {e}"
                )

            # =================================
            # Scroll for Lazy API
            # =================================

            try:

                page.evaluate(
                    "window.scrollTo(0, document.body.scrollHeight)"
                )

                page.wait_for_timeout(
                    3000
                )

            except Exception as e:

                print(
                    f"YesStyle Scroll 오류: {e}"
                )

            # =================================
            # Success
            # =================================

            if price is not None:

                print(
                    f"✅ YesStyle 가격 수집 성공: "
                    f"{price} USD"
                )

                print("=" * 60)

                return price

            # =================================
            # Failure Diagnosis
            # =================================

            if not api_found:

                print(
                    "❌ YesStyle 가격 추출 실패"
                )

                print(
                    "Reason: pgtmdl API 응답을 "
                    "찾지 못했습니다."
                )

            else:

                print(
                    "❌ YesStyle 가격 추출 실패"
                )

                print(
                    f"Reason: API {api_count}건을 "
                    "확인했으나 실제 판매가를 "
                    "찾지 못했습니다."
                )

            print("=" * 60)

            return None

    except Exception as e:

        print(
            f"❌ YesStyle 크롤링 오류: {e}"
        )

        print("=" * 60)

        return None

    finally:

        if browser is not None:

            try:

                browser.close()

            except Exception:
                pass