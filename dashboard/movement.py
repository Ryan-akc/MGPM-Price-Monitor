# dashboard/movement.py

import streamlit as st

from dashboard.utils import (
    format_price,
    format_percent
)


def render_price_movement(

    previous_price,

    current_price,

    currency="USD"

):

    st.divider()

    st.subheader(
        "📈 Price Movement"
    )


    if previous_price is None:

        st.info(
            "No previous price data."
        )

        return



    if previous_price == 0:

        st.warning(
            "Invalid previous price."
        )

        return



    change = (

        (current_price - previous_price)

        /

        previous_price

        *

        100

    )



    c1, c2, c3 = st.columns(3)



    with c1:

        st.metric(

            "Previous Price",

            format_price(

                previous_price,

                currency

            )

        )



    with c2:

        st.metric(

            "Current Price",

            format_price(

                current_price,

                currency

            )

        )



    with c3:

        st.metric(

            "Change",

            format_percent(

                change

            )

        )



    if change > 0:

        st.warning(
            "📈 Price Rise"
        )


    elif change < 0:

        st.success(
            "📉 Price Drop"
        )


    else:

        st.info(
            "Price Stable"
        )