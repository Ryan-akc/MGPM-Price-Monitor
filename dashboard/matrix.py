import streamlit as st
import pandas as pd

from database import (
    Product,
    Price,
    PricePolicy,
)


# =================================
# Formatting
# =================================

def format_datetime(value):

    if not value:
        return "-"

    try:
        return value.strftime(
            "%Y-%m-%d %H:%M"
        )

    except AttributeError:
        return str(value)[:16]


def currency_symbol(currency):

    currency = (
        currency or ""
    ).upper()

    if currency == "USD":
        return "$"

    if currency == "KRW":
        return "₩"

    if currency == "EUR":
        return "€"

    if currency == "GBP":
        return "£"

    if currency == "JPY":
        return "¥"

    return ""


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

        return (
            f"{value:.1f} "
            f"{currency}"
        ).strip()

    except (
        TypeError,
        ValueError
    ):

        return str(value)


def format_change(
    value,
    currency=None,
):

    if value is None:
        return "-"

    try:

        value = float(value)

        symbol = currency_symbol(
            currency
        )

        if value > 0:

            return (
                f"▲ {symbol}"
                f"{abs(value):,.1f}"
            )

        if value < 0:

            return (
                f"▼ {symbol}"
                f"{abs(value):,.1f}"
            )

        return "0.0"

    except (
        TypeError,
        ValueError
    ):

        return str(value)


# =================================
# Price Change
# =================================

def get_price_change(
    current_price,
    previous_price,
):

    if current_price is None:
        return 0, 0

    if previous_price is None:
        return 0, 0

    current_price = float(
        current_price
    )

    previous_price = float(
        previous_price
    )

    change = (
        current_price
        -
        previous_price
    )

    if previous_price == 0:

        return (
            change,
            0,
        )

    change_percent = (
        change
        /
        previous_price
        *
        100
    )

    return (
        change,
        change_percent,
    )


# =================================
# Market Status
# =================================

def get_market_status(
    change,
):

    if change <= -5:
        return "🔴 DROP"

    if change >= 5:
        return "🔵 UP"

    return "🟢 Stable"


# =================================
# Policy Status
# =================================

def get_policy_status(
    session,
    product_id,
    country,
    channel,
    current_price,
):

    policy = (
        session
        .query(PricePolicy)
        .filter(
            PricePolicy.product_id
            ==
            product_id,

            PricePolicy.country
            ==
            country,

            PricePolicy.channel
            ==
            channel,
        )
        .first()
    )

    if not policy:
        return "Normal"

    if (
        current_price is None
        or policy.target_price is None
    ):
        return "Normal"

    target = float(
        policy.target_price
    )

    tolerance = (
        float(policy.tolerance)
        if policy.tolerance is not None
        else 0
    )

    lower_limit = (
        target
        *
        (
            1
            -
            tolerance / 100
        )
    )

    upper_limit = (
        target
        *
        (
            1
            +
            tolerance / 100
        )
    )

    current_price = float(
        current_price
    )

    if current_price < lower_limit:
        return "Below Target"

    if current_price > upper_limit:
        return "Above Target"

    return "Normal"


# =================================
# Colors
# =================================

def color_change(
    value,
):

    if value is None:
        return ""

    text = str(
        value
    ).strip()

    # -----------------------------
    # DOWN = RED
    # -----------------------------

    if text.startswith("▼"):

        return (
            "color: red; "
            "font-weight: 600;"
        )

    # -----------------------------
    # UP = BLUE
    # -----------------------------

    if text.startswith("▲"):

        return (
            "color: blue; "
            "font-weight: 600;"
        )

    # -----------------------------
    # Numeric fallback
    # -----------------------------

    try:

        number = float(
            text
            .replace("%", "")
            .replace("▲", "")
            .replace("▼", "")
            .strip()
        )

        if number < 0:

            return (
                "color: red; "
                "font-weight: 600;"
            )

        if number > 0:

            return (
                "color: blue; "
                "font-weight: 600;"
            )

        return (
            "color: green; "
            "font-weight: 600;"
        )

    except (
        TypeError,
        ValueError
    ):

        return ""


def color_market_status(
    value,
):

    text = str(
        value
    ).upper()

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

    return (
        "color: green; "
        "font-weight: 600;"
    )


def color_policy_status(
    value,
):

    text = str(
        value
    )

    if "Above" in text:

        return (
            "color: red; "
            "font-weight: 600;"
        )

    if "Below" in text:

        return (
            "color: green; "
            "font-weight: 600;"
        )

    return "color: black;"


# =================================
# Product × Channel Matrix
# =================================

def render_price_matrix(
    session,
    filters=None,
):

    st.divider()

    st.subheader(
        "📊 Product × Channel Matrix"
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

    if not products:

        st.info(
            "No products available."
        )

        return

    # =================================
    # Filters
    # =================================

    selected_products = ["All"]
    selected_channels = ["All"]
    selected_countries = ["All"]

    selected_status = "All"
    search = ""

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

        selected_status = filters.get(
            "status",
            "All",
        )

        search = filters.get(
            "search",
            "",
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
    # Apply Filters
    # =================================

    filtered_products = []

    for product in products:

        if (
            not product_all
            and product.product
            not in selected_products
        ):
            continue

        if (
            not country_all
            and product.country
            not in selected_countries
        ):
            continue

        if (
            not channel_all
            and product.channel
            not in selected_channels
        ):
            continue

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
    # Build Rows
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

        previous_price = (
            previous.price
            if previous
            else None
        )

        change, change_percent = (
            get_price_change(
                latest.price,
                previous_price,
            )
        )

        currency = (
            product.currency
            or "-"
        )

        policy_status = (
            get_policy_status(
                session,
                product.id,
                product.country,
                product.channel,
                latest.price,
            )
        )

        market_status = (
            get_market_status(
                change_percent
            )
        )

        # =================================
        # Status Filter
        # =================================

        if selected_status != "All":

            if (
                selected_status
                ==
                "Below Target"
                and
                policy_status
                !=
                "Below Target"
            ):
                continue

            if (
                selected_status
                ==
                "Above Target"
                and
                policy_status
                !=
                "Above Target"
            ):
                continue

            if (
                selected_status
                ==
                "Changed Today"
                and
                abs(change_percent)
                <
                0.0001
            ):
                continue

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

                "Previous Price":
                    format_currency_price(
                        previous_price,
                        currency,
                    ),

                "Price":
                    format_currency_price(
                        latest.price,
                        currency,
                    ),

                "Change":
                    format_change(
                        change,
                        currency,
                    ),

                "Change %":
                    f"{change_percent:+.1f}%",

                "Policy Status":
                    policy_status,

                "Market Status":
                    market_status,

                "Date":
                    format_datetime(
                        latest.date
                    ),
            }
        )

    # =================================
    # No Results
    # =================================

    if not rows:

        st.info(
            "No price data."
        )

        return

    # =================================
    # DataFrame
    # =================================

    df = pd.DataFrame(
        rows
    )

    # =================================
    # Styling
    # =================================

    styled_df = (
        df.style

        .set_properties(
            **{
                "text-align": "center",
            }
        )

        .set_properties(
            subset=[
                "Product",
                "Channel",
            ],
            **{
                "text-align": "left",
            }
        )

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
        # Change / Change %
        # -----------------------------

        .map(
            color_change,
            subset=[
                "Change",
                "Change %",
            ],
        )

        # -----------------------------
        # Market Status
        # -----------------------------

        .map(
            color_market_status,
            subset=[
                "Market Status",
            ],
        )

        # -----------------------------
        # Policy Status
        # -----------------------------

        .map(
            color_policy_status,
            subset=[
                "Policy Status",
            ],
        )
    )

    # =================================
    # Display
    # =================================

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,

        column_config={

            "Product":
                st.column_config.TextColumn(
                    "Product",
                    width=300,
                ),

            "Channel":
                st.column_config.TextColumn(
                    "Channel",
                    width=120,
                ),

            "Country":
                st.column_config.TextColumn(
                    "Country",
                    width=100,
                ),

            "Previous Price":
                st.column_config.TextColumn(
                    "Previous Price",
                    width=120,
                ),

            "Price":
                st.column_config.TextColumn(
                    "Price",
                    width=100,
                ),

            "Change":
                st.column_config.TextColumn(
                    "Change",
                    width=110,
                ),

            "Change %":
                st.column_config.TextColumn(
                    "Change %",
                    width=100,
                ),

            "Policy Status":
                st.column_config.TextColumn(
                    "Policy Status",
                    width=130,
                ),

            "Market Status":
                st.column_config.TextColumn(
                    "Market Status",
                    width=130,
                ),

            "Date":
                st.column_config.TextColumn(
                    "Date",
                    width=145,
                ),
        },
    )