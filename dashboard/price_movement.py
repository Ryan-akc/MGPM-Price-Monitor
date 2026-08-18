import streamlit as st
import pandas as pd

from database import (
    Product,
    Price,
)


# =================================
# Currency Formatting
# =================================

def format_currency_price(
    value,
    currency,
):

    if value is None:
        return "-"

    try:

        value = float(value)

        currency = (
            currency or ""
        ).upper()

        if currency == "USD":
            return f"${value:.1f}"

        if currency == "KRW":
            return f"₩{value:,.0f}"

        if currency == "EUR":
            return f"€{value:.1f}"

        if currency == "GBP":
            return f"£{value:.1f}"

        if currency == "JPY":
            return f"¥{value:,.0f}"

        return f"{value:.1f} {currency}".strip()

    except (TypeError, ValueError):

        return str(value)


# =================================
# Color Helpers
# Price Monitor와 동일
# =================================

def color_change(
    value,
):

    text = str(value).strip()

    if text.startswith("▼"):

        return (
            "color: red; "
            "font-weight: 600;"
        )

    if text.startswith("▲"):

        return (
            "color: blue; "
            "font-weight: 600;"
        )

    return "color: green;"


def color_status(
    value,
):

    text = str(value).strip()

    if "DROP" in text:

        return (
            "color: red; "
            "font-weight: 600;"
        )

    if "UP" in text:

        return (
            "color: blue; "
            "font-weight: 600;"
        )

    return "color: green;"


# =================================
# Price Movement
# =================================

def render_price_movement(
    session,
    filters=None,
):

    # =================================
    # Filters
    # =================================

    selected_products = ["All"]
    selected_channels = ["All"]
    selected_countries = ["All"]

    if filters:

        selected_products = filters.get(
            "products",
            ["All"],
        )

        selected_channels = filters.get(
            "channels",
            ["All"],
        )

        selected_countries = filters.get(
            "countries",
            ["All"],
        )

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
    # Products
    # =================================

    products = (
        session
        .query(Product)
        .order_by(
            Product.product
        )
        .all()
    )

    rows = []

    # =================================
    # Build Movement Data
    # =================================

    for product in products:

        if (
            not product_all
            and product.product
            not in selected_products
        ):
            continue

        if (
            not channel_all
            and product.channel
            not in selected_channels
        ):
            continue

        if (
            not country_all
            and product.country
            not in selected_countries
        ):
            continue

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

        # =================================
        # Change %
        # =================================

        change = None

        if (
            previous
            and previous.price is not None
            and previous.price != 0
            and latest.price is not None
        ):

            change = (
                (
                    float(latest.price)
                    -
                    float(previous.price)
                )
                /
                float(previous.price)
                *
                100
            )

        # =================================
        # Status
        # =================================

        if change is None:

            status = "-"

        elif change < 0:

            status = "▼ DROP"

        elif change > 0:

            status = "▲ UP"

        else:

            status = "-"

        # =================================
        # Currency
        # =================================

        currency = (
            product.currency
            or "-"
        )

        # =================================
        # Row
        # =================================

        rows.append(
            {
                "Product":
                    product.product or "-",

                "Channel":
                    product.channel or "-",

                "Country":
                    product.country or "-",

                "Current Price":
                    latest.price,

                "Previous Price":
                    (
                        previous.price
                        if previous
                        else None
                    ),

                "Currency":
                    currency,

                "Change":
                    change,

                "Status":
                    status,

                "Updated":
                    getattr(
                        latest,
                        "date",
                        None,
                    ),
            }
        )

    # =================================
    # No Data
    # =================================

    if not rows:

        st.info(
            "No price movement data."
        )

        return

    df = pd.DataFrame(
        rows
    )

    # =================================
    # Movement Only
    # =================================

    movement_df = df[
        df["Change"].notna()
        &
        (df["Change"] != 0)
    ].copy()

    drops = movement_df[
        movement_df["Change"] < 0
    ].copy()

    increases = movement_df[
        movement_df["Change"] > 0
    ].copy()

    # =================================
    # Summary
    # =================================

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Total Movement",
            len(movement_df),
        )

    with c2:

        st.metric(
            "📉 Price Drops",
            len(drops),
        )

    with c3:

        st.metric(
            "📈 Price Increase",
            len(increases),
        )

    # =================================
    # Prepare Table
    # =================================

    def prepare_table(data):

        result = data.copy()

        # -----------------------------
        # Current Price
        # -----------------------------

        result["Current Price"] = (
            result.apply(
                lambda row:
                format_currency_price(
                    row["Current Price"],
                    row["Currency"],
                ),
                axis=1,
            )
        )

        # -----------------------------
        # Previous Price
        # -----------------------------

        result["Previous Price"] = (
            result.apply(
                lambda row:
                format_currency_price(
                    row["Previous Price"],
                    row["Currency"],
                ),
                axis=1,
            )
        )

        # -----------------------------
        # Change
        # -----------------------------

        result["Change"] = (
            result["Change"]
            .apply(
                lambda value:
                "-"
                if pd.isna(value)
                else (
                    f"▼ {value:+.1f}%"
                    if value < 0
                    else f"▲ {value:+.1f}%"
                )
            )
        )

        # -----------------------------
        # Updated
        # -----------------------------

        result["Updated"] = (
            result["Updated"]
            .apply(
                lambda value:
                "-"
                if value is None
                else str(value)[:16]
            )
        )

        # -----------------------------
        # Remove Currency
        # -----------------------------

        result = result.drop(
            columns=["Currency"]
        )

        return result

    # =================================
    # Styled Table
    # =================================

    def display_table(data):

        if data.empty:
            return

        display_df = (
            prepare_table(data)
            .reset_index(drop=True)
        )

        # =================================
        # Styling
        # =================================

        styled_df = (
            display_df.style

            # -----------------------------
            # Center
            # -----------------------------

            .set_properties(
                **{
                    "text-align": "center",
                }
            )

            # -----------------------------
            # Product / Channel Left
            # -----------------------------

            .set_properties(
                subset=[
                    "Product",
                    "Channel",
                ],
                **{
                    "text-align": "left",
                }
            )

            # -----------------------------
            # Header Center
            # -----------------------------

            .set_table_styles(
                [
                    {
                        "selector": "th",
                        "props": [
                            (
                                "text-align",
                                "center",
                            ),
                        ],
                    }
                ]
            )

            # -----------------------------
            # Change Color
            # Price Monitor 동일
            # -----------------------------

            .map(
                color_change,
                subset=[
                    "Change",
                ],
            )

            # -----------------------------
            # Status Color
            # Price Monitor 동일
            # -----------------------------

            .map(
                color_status,
                subset=[
                    "Status",
                ],
            )
        )

        # =================================
        # Column Configuration
        # =================================

        column_config = {

            "Product":
                st.column_config.TextColumn(
                    "Product",
                    width="large",
                ),

            "Channel":
                st.column_config.TextColumn(
                    "Channel",
                    width="medium",
                ),

            "Country":
                st.column_config.TextColumn(
                    "Country",
                    width="small",
                ),

            "Current Price":
                st.column_config.TextColumn(
                    "Current Price",
                    width="medium",
                ),

            "Previous Price":
                st.column_config.TextColumn(
                    "Previous Price",
                    width="medium",
                ),

            "Change":
                st.column_config.TextColumn(
                    "Change",
                    width="small",
                ),

            "Status":
                st.column_config.TextColumn(
                    "Status",
                    width="small",
                ),

            "Updated":
                st.column_config.TextColumn(
                    "Updated",
                    width="medium",
                ),
        }

        # =================================
        # Display
        # =================================

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
        )

    # =================================
    # Price Drops
    # =================================

    st.markdown(
        "### 📉 Price Drops"
    )

    if not drops.empty:

        drops = drops.sort_values(
            by="Change",
            ascending=True,
        )

        display_table(
            drops
        )

    else:

        st.info(
            "No price drops."
        )

    # =================================
    # Price Increase
    # =================================

    st.markdown(
        "### 📈 Price Increase"
    )

    if not increases.empty:

        increases = increases.sort_values(
            by="Change",
            ascending=False,
        )

        display_table(
            increases
        )

    else:

        st.info(
            "No price increase."
        )