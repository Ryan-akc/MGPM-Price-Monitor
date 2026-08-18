import streamlit as st
import pandas as pd

from database import (
    Product,
    Price
)


def render_product_channel_monitor(
    session,
    filters=None
):

    st.subheader(
        "📦 Product Channel Monitor"
    )

    # =================================
    # Product / Channel 데이터
    # =================================

    products = (
        session
        .query(Product)
        .order_by(Product.product)
        .all()
    )

    if not products:

        st.info(
            "No products available."
        )

        return


    # =================================
    # Mode
    # =================================

    monitor_mode = st.radio(
        "Monitor By",
        [
            "Product",
            "Channel"
        ],
        horizontal=True,
        key="product_channel_monitor_mode"
    )


    # =================================
    # PRODUCT MONITOR
    # 선택 상품 → 채널별 가격
    # =================================

    if monitor_mode == "Product":

        product_options = {}

        for product in products:

            label = (
                f"{product.product}"
                f" | "
                f"{product.country or '-'}"
            )

            product_options[label] = (
                product.id
            )


        selected_product = st.selectbox(
            "Select Product",
            list(
                product_options.keys()
            ),
            key="channel_monitor_product"
        )


        product_id = product_options[
            selected_product
        ]


        selected_product_obj = (
            session
            .query(Product)
            .filter(
                Product.id == product_id
            )
            .first()
        )


        if not selected_product_obj:

            return


        # ---------------------------------
        # 같은 상품명의 채널별 Product 조회
        # ---------------------------------

        product_rows = (

            session
            .query(Product)
            .filter(
                Product.product
                ==
                selected_product_obj.product
            )
            .order_by(
                Product.channel
            )
            .all()

        )


        rows = []


        for product in product_rows:

            prices = (

                session
                .query(Price)
                .filter(
                    Price.product_id
                    ==
                    product.id
                )
                .order_by(
                    Price.id.desc()
                )
                .limit(2)
                .all()

            )


            if not prices:

                continue


            latest = prices[0]


            previous = (
                prices[1]
                if len(prices) > 1
                else None
            )


            change_rate = None


            if (
                previous
                and previous.price != 0
            ):

                change_rate = (

                    (
                        latest.price
                        -
                        previous.price
                    )
                    /
                    previous.price
                    *
                    100

                )


            rows.append(
                {
                    "Channel":
                        product.channel or "-",

                    "Country":
                        product.country or "-",

                    "Latest Price":
                        latest.price,

                    "Previous Price":
                        previous.price
                        if previous
                        else "-",

                    "Change %":
                        (
                            round(
                                change_rate,
                                2
                            )
                            if change_rate is not None
                            else "-"
                        ),

                    "Updated":
                        latest.date
                }
            )


        if not rows:

            st.info(
                "No price history."
            )

            return


        result = pd.DataFrame(
            rows
        )


        st.dataframe(
            result,
            hide_index=True,
            use_container_width=True
        )


    # =================================
    # CHANNEL MONITOR
    # 선택 채널 → 상품별 가격
    # =================================

    else:

        channels = sorted(
            list(
                set(
                    [
                        p.channel
                        for p in products
                        if p.channel
                    ]
                )
            )
        )


        if not channels:

            st.info(
                "No channels available."
            )

            return


        selected_channel = st.selectbox(
            "Select Channel",
            channels,
            key="channel_monitor_channel"
        )


        channel_products = (

            session
            .query(Product)
            .filter(
                Product.channel
                ==
                selected_channel
            )
            .order_by(
                Product.product
            )
            .all()

        )


        if not channel_products:

            st.info(
                "No products registered for this channel."
            )

            return


        rows = []


        for product in channel_products:

            prices = (

                session
                .query(Price)
                .filter(
                    Price.product_id
                    ==
                    product.id
                )
                .order_by(
                    Price.id.desc()
                )
                .limit(2)
                .all()

            )


            if not prices:

                rows.append(
                    {
                        "Product":
                            product.product,

                        "Country":
                            product.country or "-",

                        "Latest Price":
                            "-",

                        "Previous Price":
                            "-",

                        "Change %":
                            "-",

                        "Updated":
                            "-"
                    }
                )

                continue


            latest = prices[0]


            previous = (
                prices[1]
                if len(prices) > 1
                else None
            )


            change_rate = None


            if (
                previous
                and previous.price != 0
            ):

                change_rate = (

                    (
                        latest.price
                        -
                        previous.price
                    )
                    /
                    previous.price
                    *
                    100

                )


            rows.append(
                {
                    "Product":
                        product.product,

                    "Country":
                        product.country or "-",

                    "Latest Price":
                        latest.price,

                    "Previous Price":
                        previous.price
                        if previous
                        else "-",

                    "Change %":
                        (
                            round(
                                change_rate,
                                2
                            )
                            if change_rate is not None
                            else "-"
                        ),

                    "Updated":
                        latest.date
                }
            )


        result = pd.DataFrame(
            rows
        )


        st.dataframe(
            result,
            hide_index=True,
            use_container_width=True
        )