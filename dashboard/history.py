import streamlit as st
import pandas as pd

from database import (
    Product,
    Price,
)


# =================================
# Currency Formatting
# =================================

def format_price(
    value,
    currency=None,
):

    if value is None:
        return "-"

    try:

        value = float(value)

        currency = (
            currency
            or ""
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


def format_datetime(value):

    if not value:
        return "-"

    try:

        return value.strftime(
            "%Y-%m-%d %H:%M"
        )

    except AttributeError:

        return str(value)[:16]


# =================================
# Change Color
# =================================

def color_change(value):

    if value is None:
        return ""

    try:

        value = float(value)

    except (TypeError, ValueError):

        return ""

    if value > 0:
        return "color: blue;"

    if value < 0:
        return "color: red;"

    return "color: black;"


# =================================
# Price History
# =================================

def render_price_history(
    session,
    filters=None,
):

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

        search = filters.get(
            "search",
            "",
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
            Product.channel,
            Product.product,
        )
        .all()
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
    # No Product
    # =================================

    if not filtered_products:

        st.info(
            "조건에 맞는 상품이 없습니다."
        )

        return

    # =================================
    # History Rows
    # =================================

    history_rows = []

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
            .limit(50)
            .all()
        )

        if not prices:
            continue

        currency = (
            product.currency
            or "-"
        )

        for index, price in enumerate(
            prices
        ):

            # ---------------------------------
            # Previous Price
            # ---------------------------------

            previous = None

            if index + 1 < len(prices):

                previous = prices[
                    index + 1
                ]

            # ---------------------------------
            # Change
            # ---------------------------------

            change_percent = 0.0

            if (
                previous
                and previous.price is not None
                and previous.price != 0
                and price.price is not None
            ):

                change_percent = (
                    (
                        float(price.price)
                        -
                        float(previous.price)
                    )
                    /
                    float(previous.price)
                    *
                    100
                )

            # ---------------------------------
            # Row
            # ---------------------------------

            history_rows.append(
                {
                    "Product":
                        product.product or "-",

                    "Channel":
                        product.channel or "-",

                    "Country":
                        product.country or "-",

                    "Date":
                        format_datetime(
                            price.date
                        ),

                    "Price":
                        format_price(
                            price.price,
                            currency,
                        ),

                    "Change":
                        change_percent,
                }
            )

    # =================================
    # No History
    # =================================

    if not history_rows:

        st.info(
            "가격 기록이 없습니다."
        )

        return

    # =================================
    # DataFrame
    # =================================

    df = pd.DataFrame(
        history_rows
    )

    # =================================
    # History Controls
    # =================================

    st.markdown(
        "### History View"
    )

    control_cols = st.columns(2)

    with control_cols[0]:

        group_by = st.selectbox(
            "View By",
            [
                "Channel + Product",
                "Product + Channel",
                "Channel",
                "Product",
            ],
            key="history_view_by",
        )

    with control_cols[1]:

        sort_by = st.selectbox(
            "Sort By",
            [
                "Latest",
                "Oldest",
                "Biggest Drop",
                "Biggest Rise",
            ],
            key="history_sort_by",
        )

    # =================================
    # Grouping / Primary Sorting
    # =================================

    if group_by == "Channel + Product":

        sort_columns = [
            "Channel",
            "Product",
            "Date",
        ]

    elif group_by == "Product + Channel":

        sort_columns = [
            "Product",
            "Channel",
            "Date",
        ]

    elif group_by == "Channel":

        sort_columns = [
            "Channel",
            "Date",
        ]

    else:

        sort_columns = [
            "Product",
            "Date",
        ]

    # =================================
    # Secondary Sorting
    # =================================

    if sort_by == "Latest":

        if len(sort_columns) == 3:

            ascending = [
                True,
                True,
                False,
            ]

        else:

            ascending = [
                True,
                False,
            ]

        df = df.sort_values(
            by=sort_columns,
            ascending=ascending,
        )

    elif sort_by == "Oldest":

        df = df.sort_values(
            by=sort_columns,
            ascending=True,
        )

    elif sort_by == "Biggest Drop":

        group_columns = sort_columns[:-1]

        df = df.sort_values(
            by=group_columns + ["Change"],
            ascending=(
                [True]
                * len(group_columns)
                +
                [True]
            ),
        )

    elif sort_by == "Biggest Rise":

        group_columns = sort_columns[:-1]

        df = df.sort_values(
            by=group_columns + ["Change"],
            ascending=(
                [True]
                * len(group_columns)
                +
                [False]
            ),
        )

    # =================================
    # Preserve Numeric Change
    # =================================

    change_values = df["Change"].copy()

    # =================================
    # Change Display
    # =================================

    display_df = df.copy()

    display_df["Change"] = (
        display_df["Change"]
        .apply(
            lambda value:
            f"▲ {value:+.1f}%"
            if value > 0
            else (
                f"▼ {value:+.1f}%"
                if value < 0
                else "+0.0%"
            )
        )
    )

    # =================================
    # Apply Change Colors
    # =================================

    styled_df = (
        display_df
        .style
        .apply(
            lambda row: [
                color_change(
                    change_values.loc[row.name]
                )
                if column == "Change"
                else ""
                for column in display_df.columns
            ],
            axis=1,
        )
    )

    # =================================
    # Native Table
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
                    width=130,
                ),

            "Country":
                st.column_config.TextColumn(
                    "Country",
                    width=100,
                ),

            "Date":
                st.column_config.TextColumn(
                    "Date",
                    width=145,
                ),

            "Price":
                st.column_config.TextColumn(
                    "Price",
                    width=110,
                ),

            "Change":
                st.column_config.TextColumn(
                    "Change",
                    width=110,
                ),
        },
    )