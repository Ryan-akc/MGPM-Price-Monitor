import streamlit as st
import pandas as pd

from database import (
    Product,
    Price
)


def format_price(value):
    """
    Dashboard 가격 표시
    소수점 1자리
    """

    if value is None:
        return "-"

    try:
        return f"{float(value):.1f}"
    except (TypeError, ValueError):
        return str(value)


def format_datetime(value):
    """
    Dashboard 날짜/시간 표시
    YYYY-MM-DD HH:MM
    """

    if not value:
        return "-"

    try:
        return value.strftime("%Y-%m-%d %H:%M")
    except AttributeError:
        return str(value)[:16]


def render_product_channel_monitor(
    session,
    filters=None
):

    st.subheader(
        "📦 Product Channel Monitor"
    )

    # =============================
    # Load Products
    # =============================

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

    # =============================
    # Read Filters
    # =============================

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

    # =============================
    # Normalize Filters
    # =============================

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

    # =============================
    # Filter Products
    # =============================

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

            text = (
                f"{product.product} "
                f"{product.channel} "
                f"{product.country}"
            ).lower()

            if search.lower() not in text:
                continue

        filtered_products.append(
            product
        )

    if not filtered_products:

        st.info(
            "No matching products."
        )

        return

    # =============================
    # Monitoring Summary
    # =============================

    total_products = len(
        filtered_products
    )

    monitored_products = 0
    changed_products = 0

    # =============================
    # Build Monitoring Rows
    # =============================

    rows = []

    for product in filtered_products:

        # -------------------------
        # Latest Price
        # -------------------------

        latest = (
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
            .first()
        )

        # -------------------------
        # Previous Price
        # -------------------------

        previous = (
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
            .offset(1)
            .first()
        )

        # -------------------------
        # No Price History
        # -------------------------

        if not latest:

            rows.append(
                {
                    "Product":
                        product.product,

                    "Channel":
                        product.channel,

                    "Country":
                        product.country,

                    "Latest Price":
                        "-",

                    "Previous Price":
                        "-",

                    "Change":
                        "-",

                    "Updated":
                        "-"
                }
            )

            continue

        monitored_products += 1

        # -------------------------
        # Price Change
        # -------------------------

        change = 0
        change_amount = 0

        if (
            previous
            and previous.price is not None
            and previous.price != 0
            and latest.price is not None
        ):

            change_amount = latest.price - previous.price

            change = (
                (
                    latest.price
                    -
                    previous.price
                )
                /
                previous.price
            ) * 100

        # -------------------------
        # Change Display
        # -------------------------

        if change > 0:

            change_text = (
                f"▲ {change_amount:.1f}"
            )

            if change >= 5:
                changed_products += 1

        elif change < 0:

            change_text = (
                f"▼ {abs(change_amount):.1f}"
            )

            if change <= -5:
                changed_products += 1

        else:

            change_text = "0.0"

        # -------------------------
        # Updated
        # -------------------------

        updated = getattr(
            latest,
            "date",
            None
        )

        if updated is None:

            updated = getattr(
                latest,
                "created_at",
                None
            )

        # -------------------------
        # Row
        # -------------------------

        rows.append(
            {
                "Product":
                    product.product,

                "Channel":
                    product.channel,

                "Country":
                    product.country,

                "Latest Price":
                    format_price(
                        latest.price
                    ),

                "Previous Price":
                    format_price(
                        previous.price
                    )
                    if previous
                    else "-",

                "Change":
                    change_text,

                "Change %":
                    f"{change:.1f}%",

                "Updated":
                    format_datetime(
                        updated
                    )
            }
        )

    # =============================
    # Monitoring KPI
    # =============================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Products",
            total_products
        )

    with col2:

        st.metric(
            "Monitoring",
            monitored_products
        )

    with col3:

        st.metric(
            "Changed",
            changed_products
        )

    # =============================
    # Display
    # =============================

    if not rows:

        st.info(
            "No price history."
        )

        return

    df = pd.DataFrame(
        rows
    )

    # =============================
    # Product / Channel Mode
    # =============================

    if (
        not product_all
        and channel_all
    ):

        st.caption(
            "📦 Selected Product → Channel Prices"
        )

    elif (
        product_all
        and not channel_all
    ):

        st.caption(
            "🏪 Selected Channel → Product Prices"
        )

    elif (
        not product_all
        and not channel_all
    ):

        st.caption(
            "🔎 Selected Product × Channel"
        )

    else:

        st.caption(
            "📊 All Product × Channel Prices"
        )

    # =============================
    # Price Table
    # =============================

    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True
    )