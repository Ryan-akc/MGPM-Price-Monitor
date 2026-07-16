import streamlit as st

from database import Product, Price
from collector import collect_price


SHOPS = [
    "amazon",
    "yesstyle",
    "stylekorean",
    "jolse",
    "stylevana"
]

CURRENCIES = [
    "USD",
    "EUR",
    "KRW"
]


def product_page(session):

    st.header("📦 상품 관리")


    # ==========================
    # 상품 등록
    # ==========================

    with st.expander("➕ 새 상품 등록"):

        with st.form(
            "add_product",
            clear_on_submit=True
        ):

            channel = st.text_input(
                "채널명",
                placeholder="Amazon US"
            )

            product = st.text_input(
                "상품명"
            )

            url = st.text_input(
                "판매 URL"
            )

            shop = st.selectbox(
                "쇼핑몰",
                SHOPS
            )

            country = st.text_input(
                "국가",
                value="US"
            )

            currency = st.selectbox(
                "통화",
                CURRENCIES
            )


            if st.form_submit_button(
                "상품 등록"
            ):

                if not(channel and product and url):

                    st.error(
                        "채널명, 상품명, URL은 필수입니다."
                    )

                else:

                    session.add(
                        Product(
                            channel=channel,
                            product=product,
                            url=url,
                            shop_type=shop,
                            country=country,
                            currency=currency
                        )
                    )

                    session.commit()

                    st.success(
                        "상품 등록 완료"
                    )

                    st.rerun()



    st.divider()


    # ==========================
    # 검색
    # ==========================

    keyword = st.text_input(
        "🔍 상품 검색",
        placeholder="상품명 또는 채널명"
    )


    products = (
        session.query(Product)
        .order_by(
            Product.product.asc()
        )
        .all()
    )


    if keyword:

        k = keyword.lower()

        products = [
            p for p in products
            if k in p.product.lower()
            or k in p.channel.lower()
        ]


    st.caption(
        f"등록 상품 : {len(products)}"
    )


    if not products:

        st.info(
            "등록된 상품이 없습니다."
        )

        return



    # ==========================
    # 상품 목록
    # ==========================

    for p in products:


        with st.expander(
            f"{p.product} | {p.channel}",
            expanded=False
        ):


            st.write(
                f"**쇼핑몰** : {p.shop_type}"
            )

            st.write(
                f"**국가** : {p.country}"
            )

            st.write(
                f"**통화** : {p.currency}"
            )

            st.write(
                f"**URL** : {p.url}"
            )


            # ==========================
            # 최신 가격 표시
            # ==========================

            last_price = (
                session.query(Price)
                .filter(
                    Price.product_id == p.id
                )
                .order_by(
                    Price.id.desc()
                )
                .first()
            )


            if last_price:


                st.info(
                    f"💰 현재 가격 : "
                    f"{last_price.price:.2f} {p.currency}"
                )


                # 이전 가격 조회

                previous_price = (
                    session.query(Price)
                    .filter(
                        Price.product_id == p.id
                    )
                    .order_by(
                        Price.id.desc()
                    )
                    .offset(1)
                    .first()
                )


                if previous_price:


                    change = (
                        (
                            last_price.price
                            -
                            previous_price.price
                        )
                        /
                        previous_price.price
                        *
                        100
                    )


                    if change > 0:

                        st.warning(
                            f"📈 가격 상승 : "
                            f"+{change:.2f}% "
                            f"(이전 {previous_price.price:.2f})"
                        )


                    elif change < 0:

                        st.success(
                            f"📉 가격 하락 : "
                            f"{change:.2f}% "
                            f"(이전 {previous_price.price:.2f})"
                        )


                    else:

                        st.caption(
                            "가격 변화 없음"
                        )


                st.caption(
                    f"🕒 마지막 수집 : {last_price.date}"
                )


            else:

                st.warning(
                    "가격 데이터 없음"
                )



            st.divider()



            # ==========================
            # 버튼
            # ==========================

            c1, c2 = st.columns(2)


            if c1.button(
                "🔄 가격 확인",
                key=f"price_{p.id}"
            ):


                price = collect_price(
                    p.id
                )


                if price is not None:

                    st.success(
                        f"현재 가격 : "
                        f"{price:.2f} {p.currency}"
                    )

                    st.rerun()


                else:

                    st.error(
                        "가격 조회 실패"
                    )



            if c2.button(
                "🗑 삭제",
                key=f"del_{p.id}"
            ):


                # 가격 이력 삭제

                session.query(Price).filter(
                    Price.product_id == p.id
                ).delete()


                # 상품 삭제

                session.delete(p)

                session.commit()


                st.success(
                    "상품 및 가격 이력 삭제 완료"
                )

                st.rerun()



            st.divider()



            # ==========================
            # 상품 수정
            # ==========================

            st.markdown(
                "#### ✏️ 상품 수정"
            )


            with st.form(
                f"edit_{p.id}"
            ):


                shop_index = (
                    SHOPS.index(p.shop_type)
                    if p.shop_type in SHOPS
                    else 0
                )


                currency_index = (
                    CURRENCIES.index(p.currency)
                    if p.currency in CURRENCIES
                    else 0
                )


                new_channel = st.text_input(
                    "채널명",
                    value=p.channel
                )


                new_product = st.text_input(
                    "상품명",
                    value=p.product
                )


                new_url = st.text_input(
                    "판매 URL",
                    value=p.url
                )


                new_shop = st.selectbox(
                    "쇼핑몰",
                    SHOPS,
                    index=shop_index
                )


                new_country = st.text_input(
                    "국가",
                    value=p.country
                )


                new_currency = st.selectbox(
                    "통화",
                    CURRENCIES,
                    index=currency_index
                )



                if st.form_submit_button(
                    "💾 저장"
                ):


                    p.channel = new_channel
                    p.product = new_product
                    p.url = new_url
                    p.shop_type = new_shop
                    p.country = new_country
                    p.currency = new_currency


                    session.commit()


                    st.success(
                        "수정 완료"
                    )

                    st.rerun()