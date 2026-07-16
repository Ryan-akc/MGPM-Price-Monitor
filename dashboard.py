import streamlit as st
import pandas as pd
import plotly.express as px

from database import Product, Price, CollectionLog, Session


def format_datetime(value):

    if not value:
        return "-"

    try:

        dt = pd.to_datetime(
            value,
            format="mixed"
        )

        return (
            dt.strftime("%m-%d")
            +
            "\n"
            +
            dt.strftime("%H:%M")
        )

    except:

        return "-"





def dashboard_page(session):

    # ==========================
    # Dashboard Style
    # ==========================

    st.markdown(
        """
        <style>

        html, body, [class*="css"] {
            font-size: 14px;
        }

        h1 {
            font-size: 28px !important;
        }

        h2 {
            font-size: 20px !important;
        }

        h3 {
            font-size: 17px !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 20px !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 12px !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    # 최신 DB 반영
    session.close()
    session = Session()


    st.title(
    "📊 Price Monitor Dashboard"
)

    st.caption(
    "MGPM v0.2 Price Intelligence"
)
    # ==========================
    # 자동 수집 상태
    # ==========================

    st.subheader("⚙ 자동 수집 상태")

    latest_log = (
        session.query(CollectionLog)
        .order_by(CollectionLog.id.desc())
        .first()
    )

    if latest_log:

        st.markdown("")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "🕒 마지막 자동수집",
                format_datetime(
                    latest_log.end_time
                )
            )

        with c2:
            st.metric(
                "📦 수집 상품",
                latest_log.total_count
            )

        with c3:
            st.metric(
                "✅ 성공",
                latest_log.success_count
            )

        with c4:
            st.metric(
                "❌ 실패",
                latest_log.fail_count
            )

        st.markdown("")

        if latest_log.status == "SUCCESS":

            st.success(
                "🟢 Collection Status : SUCCESS"
            )

        else:

            st.error(
                f"🔴 Collection Status : {latest_log.status}"
            )
    

    # ==========================
    # Filter
    # ==========================

    st.subheader("🔎 Filter")


    all_products = (
        session.query(Product)
        .all()
    )


    countries = sorted(
        list(
            set(
                p.country
                for p in all_products
                if p.country
            )
        )
    )


    channels = sorted(
        list(
            set(
                p.channel
                for p in all_products
                if p.channel
            )
        )
    )


    names = sorted(
        list(
            set(
                p.product
                for p in all_products
                if p.product
            )
        )
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        selected_country = st.selectbox(
            "국가",
            ["전체"] + countries
        )


    with c2:

        selected_channel = st.selectbox(
            "채널",
            ["전체"] + channels
        )


    with c3:

        selected_product = st.selectbox(
            "제품",
            ["전체"] + names
        )



    products = all_products


    if selected_country != "전체":

        products = [
            p for p in products
            if p.country == selected_country
        ]


    if selected_channel != "전체":

        products = [
            p for p in products
            if p.channel == selected_channel
        ]


    if selected_product != "전체":

        products = [
            p for p in products
            if p.product == selected_product
        ]



    st.divider()



    # ==========================
    # Price Movement
    # ==========================

    st.subheader("📉 Price Movement")


    changes = []


    for product in products:


        history = (
            session.query(Price)
            .filter(
                Price.product_id == product.id
            )
            .order_by(
                Price.id.desc()
            )
            .limit(2)
            .all()
        )


        if len(history) >= 2:


            current = float(
                history[0].price
            )

            previous = float(
                history[1].price
            )


            if previous != 0:


                rate = (
                    (current - previous)
                    /
                    previous
                    *
                    100
                )


                if rate != 0:

                    changes.append(
                        {
                            "상품": product.product,
                            "이전": previous,
                            "현재": current,
                            "변동률": rate
                        }
                    )



    if changes:


        df_change = pd.DataFrame(
            changes
        )


        df_change["상태"] = (
            df_change["변동률"]
            .apply(
                lambda x:
                "🔻 Price Drop"
                if x < 0
                else "🔺 Price Increase"
            )
        )


        df_change["이전"] = (
            df_change["이전"]
            .apply(
                lambda x:
                f"${x:.2f}"
            )
        )


        df_change["현재"] = (
            df_change["현재"]
            .apply(
                lambda x:
                f"${x:.2f}"
            )
        )


        df_change["변동률"] = (
            df_change["변동률"]
            .apply(
                lambda x:
                f"{x:+.1f}%"
            )
        )


        st.dataframe(
            df_change[
                [
                    "상태",
                    "상품",
                    "이전",
                    "현재",
                    "변동률"
                ]
            ],
            hide_index=True,
            use_container_width=True
        )


    else:


        st.info(
            "최근 가격 변동 상품이 없습니다."
        )


    st.divider()



    # ==========================
    # 상품 정보 Card
    # ==========================

    st.subheader("📦 Product Monitor")

    if not products:

        st.warning(
            "조건에 맞는 상품이 없습니다."
        )

    else:

        for product in products:

            latest_price = (
                session.query(Price)
                .filter(
                    Price.product_id == product.id
                )
                .order_by(
                    Price.date.desc()
                )
                .first()
            )

            previous_price = (
                session.query(Price)
                .filter(
                    Price.product_id == product.id
                )
                .order_by(
                    Price.date.desc()
                )
                .offset(1)
                .first()
            )

            if latest_price and previous_price:

                rate = (
                    (
                        latest_price.price
                        -
                        previous_price.price
                    )
                    /
                    previous_price.price
                    *
                    100
                )

            else:

                rate = 0


            if rate > 0:

                change = f"🔺 +{rate:.1f}%"

            elif rate < 0:

                change = f"🔻 {rate:.1f}%"

            else:

                change = "➖ 0.0%"


            with st.container(border=True):

                st.markdown(
                    f"#### 🛍️ {product.product}"
                )

                st.caption(
                    f"{product.country} | {product.channel}"
                )

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.markdown("**Current**")

                    if latest_price:

                        st.write(
                            f"${latest_price.price:.2f}"
                        )

                    else:

                        st.write("-")

                with c2:

                    st.markdown("**Previous**")

                    if previous_price:

                        st.write(
                            f"${previous_price.price:.2f}"
                        )

                    else:

                        st.write("-")

                with c3:

                    st.markdown("**Change**")

                    st.write(change)

                st.divider()

                left, right = st.columns([5, 1])

                with left:

                    if latest_price:

                        st.caption(
                            "Updated : "
                            +
                            format_datetime(
                                latest_price.date
                            )
                        )

                with right:

                    if product.url:

                        st.link_button(
                            "🔗 View",
                            product.url
                        )

    st.divider()

    # ==========================
    # 가격 추이
    # ==========================

    st.subheader("📈 가격 추이")

    if products:


        selected = st.selectbox(
            "상품 선택",
            [
                p.product
                for p in products
            ]
        )


        period = st.selectbox(
            "조회 기간",
            [
                "최근 7일",
                "전체"
            ]
        )


        selected_product = (
            session.query(Product)
            .filter(
                Product.product == selected
            )
            .first()
        )


        prices = (
            session.query(Price)
            .filter(
                Price.product_id ==
                selected_product.id
            )
            .order_by(
                Price.id
            )
            .all()
        )


        if period == "최근 7일":

            prices = prices[-7:]


        if prices:


            current_price = prices[-1].price

            min_price = min(
                p.price
                for p in prices
            )

            max_price = max(
                p.price
                for p in prices
            )


            st.caption(
                f"📌 가격 변경 이력 : {len(prices)}건"
            )


            c1, c2, c3 = st.columns(3)


            with c1:

                st.metric(
                    "💰 현재 가격",
                    f"${current_price:.2f}"
                )


            with c2:

                st.metric(
                    "⬇ 최저 가격",
                    f"${min_price:.2f}"
                )


            with c3:

                st.metric(
                    "⬆ 최고 가격",
                    f"${max_price:.2f}"
                )



            if (
                current_price ==
                min_price ==
                max_price
            ):

                st.info(
                    "🟢 가격 안정 상태 - 최근 가격 변동 없음"
                )



            df = pd.DataFrame(
                [
                    {
                        "날짜": p.date,
                        "가격": p.price
                    }
                    for p in prices
                ]
            )



            df["날짜"] = pd.to_datetime(
                df["날짜"],
                format="mixed",
                errors="coerce"
            )



            df = (
                df.dropna()
                .sort_values("날짜")
            )



            df["표시"] = (
                df["날짜"]
                .dt.strftime(
                    "%m-%d %H:%M"
                )
            )



            fig = px.line(
                df,
                x="표시",
                y="가격",
                markers=True
            )


            # 가격 동일 시 Y축 확대
            if min_price == max_price:

                margin = max(
                    min_price * 0.01,
                    0.1
                )

                fig.update_yaxes(
                    range=[
                        min_price - margin,
                        max_price + margin
                    ]
                )



            fig.update_traces(
                hovertemplate=
                "날짜 : %{x}<br>"
                "가격 : $%{y:.2f}"
            )



            fig.update_layout(
                height=220,
                margin=dict(
                    l=20,
                    r=20,
                    t=10,
                    b=20
                ),
                xaxis_title="",
                yaxis_title="USD",
                hovermode="x unified"
            )



            st.plotly_chart(
                fig,
                use_container_width=True
            )


        else:

            st.info(
                "가격 데이터 없음"
            )


    else:

        st.info(
            "선택 가능한 상품이 없습니다."
        )


    session.close()
