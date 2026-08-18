import streamlit as st
import pandas as pd

from database import (
    Product,
    Price
)


# =================================
# Formatting
# =================================

def format_price(value):

    if value is None:
        return "-"

    try:
        return f"{float(value):.1f}"

    except (TypeError, ValueError):

        return str(value)


def format_change(value):

    if value is None:
        return "-"

    if value > 0:
        return f"▲ {value:+.1f}%"

    if value < 0:
        return f"▼ {value:+.1f}%"

    return "+0.0%"


# =================================
# Market Price Overview
# =================================

def render_market_overview(
    session,
    filters=None
):

    st.divider()

    st.subheader(
        "🌎 Market Price Overview"
    )

    # =================================
    # Filter Values
    # =================================

    selected_products = ["All"]
    selected_channels = ["All"]
    selected_countries = ["All"]
    search = ""

    if filters:

        selected_products = filters.get(
            "products",
            ["All"]
        )

        selected_channels = filters.get(
            "channels",
            ["All"]
        )

        selected_countries = filters.get(
            "countries",
            ["All"]
        )

        search = filters.get(
            "search",
            ""
        )

    # =================================
    # Normalize
    # =================================

    if not selected_products:
        selected_products = ["All"]

    if not selected_channels:
        selected_channels = ["All"]

    if not selected_countries:
        selected_countries = ["All"]

    product_all = (
        "All" in selected_products
    )

    channel_all = (
        "All" in selected_channels
    )

    country_all = (
        "All" in selected_countries
    )

    # =================================
    # Product Query
    # =================================

    products = (
        session
        .query(Product)
        .order_by(
            Product.product
        )
        .all()
    )

    # =================================
    # Apply Filters
    # =================================

    filtered_products = []

    for product in products:

        # Product
        if (
            not product_all
            and product.product
            not in selected_products
        ):
            continue

        # Channel
        if (
            not channel_all
            and product.channel
            not in selected_channels
        ):
            continue

        # Country
        if (
            not country_all
            and product.country
            not in selected_countries
        ):
            continue

        # Search
        if search:

            search_text = (
                search
                .strip()
                .lower()
            )

            product_text = (
                f"{product.product or ''} "
                f"{product.channel or ''} "
                f"{product.country or ''}"
            ).lower()

            if search_text not in product_text:
                continue

        filtered_products.append(
            product
        )

    # =================================
    # No Products
    # =================================

    if not filtered_products:

        st.info(
            "No products available."
        )

        return

    # =================================
    # Build Overview
    # =================================

    rows = []

    for product in filtered_products:

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
            .all()
        )

        if not prices:
            continue

        # -----------------------------
        # Current
        # -----------------------------

        current = float(
            prices[0].price
        )

        # -----------------------------
        # Previous
        # -----------------------------

        previous = None

        if len(prices) > 1:

            previous = float(
                prices[1].price
            )

        # -----------------------------
        # Change
        # -----------------------------

        change = None

        if (
            previous is not None
            and previous != 0
        ):

            change = (
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

        # -----------------------------
        # Historical Prices
        # -----------------------------

        price_list = [
            float(price.price)
            for price in prices
            if price.price is not None
        ]

        if not price_list:
            continue

        # -----------------------------
        # Row
        # -----------------------------

        rows.append(
            {
                "Product":
                    product.product,

                "Channel":
                    product.channel or "-",

                "Country":
                    product.country or "-",

                "Previous Price":
                    previous,

                "Current Price":
                    current,

                "Change":
                    format_change(
                        change
                    ),

                "Lowest":
                    min(price_list),

                "Highest":
                    max(price_list),

                "Currency":
                    product.currency or "-"
            }
        )

    # =================================
    # DataFrame
    # =================================

    if not rows:

        st.info(
            "No price data."
        )

        return

    df = pd.DataFrame(
        rows
    )

    # =================================
    # Display
    # =================================

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={

            "Previous Price":
                st.column_config.NumberColumn(
                    format="%.1f"
                ),

            "Current Price":
                st.column_config.NumberColumn(
                    format="%.1f"
                ),

            "Lowest":
                st.column_config.NumberColumn(
                    format="%.1f"
                ),

            "Highest":
                st.column_config.NumberColumn(
                    format="%.1f"
                )
        }
    )