import streamlit as st

from dashboard.utils import (
    format_price,
    format_percent,
)


# =================================
# Trend Formatting
# =================================

def format_trend(value):

    try:

        value = float(value)

        if value > 0:

            return (
                f'<span style="'
                f'color: blue; '
                f'font-weight: 600; '
                f'font-size: 28px;'
                f'">'
                f'▲ {value:+.1f}%'
                f'</span>'
            )

        if value < 0:

            return (
                f'<span style="'
                f'color: red; '
                f'font-weight: 600; '
                f'font-size: 28px;'
                f'">'
                f'▼ {value:+.1f}%'
                f'</span>'
            )

        return (
            '<span style="'
            'color: green; '
            'font-weight: 600; '
            'font-size: 28px;'
            '">'
            '+0.0%'
            '</span>'
        )

    except (TypeError, ValueError):

        return (
            '<span style="'
            'color: green; '
            'font-weight: 600; '
            'font-size: 28px;'
            '">'
            '-'
            '</span>'
        )


# =================================
# Advanced Price Analysis
# =================================

def render_price_analysis(
    price_df,
    currency="USD",
):

    st.divider()

    st.subheader(
        "🔎 Advanced Price Analysis"
    )

    if (
        price_df is None
        or price_df.empty
    ):

        st.info(
            "No price data."
        )

        return

    # =================================
    # Price Data
    # =================================

    prices = (
        price_df["price"]
        .astype(float)
        .tolist()
    )

    if not prices:

        st.info(
            "No price data."
        )

        return

    # =================================
    # Current
    # =================================

    current = prices[-1]

    # =================================
    # Average
    # =================================

    average = (
        sum(prices)
        /
        len(prices)
    )

    # =================================
    # Trend
    # =================================

    trend = 0.0

    if len(prices) > 1:

        previous = prices[-2]

        if previous != 0:

            trend = (
                (
                    current
                    -
                    previous
                )
                /
                previous
                *
                100
            )

    # =================================
    # Layout
    # =================================

    c1, c2, c3 = st.columns(3)

    # =================================
    # Current
    # =================================

    with c1:

        st.metric(
            "Current",
            format_price(
                current,
                currency,
            ),
        )

    # =================================
    # Average
    # =================================

    with c2:

        st.metric(
            "Average",
            format_price(
                average,
                currency,
            ),
        )

    # =================================
    # Trend
    # =================================

    with c3:

        st.markdown(
            "#### Trend"
        )

        st.markdown(
            format_trend(trend),
            unsafe_allow_html=True,
        )