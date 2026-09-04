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
        ValueError,
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
        ValueError,
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
        ValueError,
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
# Product Link
# =================================

def make_product_link(
    url,
    product_name,
):

    if not url:
        return ""

    url = str(url).strip()

    if not url:
        return ""

    product_name = (
        str(product_name).strip()
        if product_name
        else "-"
    )

    # =================================
    # IMPORTANT
    #
    # 실제 판매 URL은 그대로 유지합니다.
    # 기존 fragment가 있다면 제거합니다.
    #
    # 상품명은 fragment에 넣어서
    # LinkColumn의 display_text 정규식으로
    # 화면에는 상품명만 표시합니다.
    #
    # fragment는 서버로 전송되지 않으므로
    # 실제 판매페이지에는 영향을 주지 않습니다.
    # =================================

    base_url = url.split(
        "#",
        1,
    )[0]

    return (
        f"{base_url}"
        f"#MGPM_PRODUCT_"
        f"{product_name}"
    )


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
        "All"
        in
        selected_products
    )

    channel_all = (
        "All"
        in
        selected_channels
    )

    country_all = (
        "All"
        in
        selected_countries
    )

    # =================================
    # Apply Filters
    # =================================

    search_text = (
        search.strip().lower()
        if search
        else ""
    )

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

        if search_text:

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
        # Product Link
        # =================================

        product_link = make_product_link(
            product.url,
            product.product,
        )

        # =================================
        # Row
        # =================================

        rows.append(
            {
                "Product":
                    product_link,

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

        .map(
            color_change,
            subset=[
                "Change",
                "Change %",
            ],
        )

        .map(
            color_market_status,
            subset=[
                "Market Status",
            ],
        )

        .map(
            color_policy_status,
            subset=[
                "Policy Status",
            ],
        )
    )

    # =================================
    # Column Configuration
    # =================================

    column_config = {

        # 상품명 클릭 → 실제 Product.url
        # LinkColumn이 클릭 가능한 링크로 표시
        # display_text는 fragment에서 상품명만 추출
        "Product":
            st.column_config.LinkColumn(
                "Product",
                width=180,
                display_text=(
                    r"#MGPM_PRODUCT_(.*)"
                ),
            ),

        "Channel":
            st.column_config.TextColumn(
                "Channel",
                width=80,
            ),

        "Country":
            st.column_config.TextColumn(
                "Country",
                width=70,
            ),

        "Previous Price":
            st.column_config.TextColumn(
                "Previous Price",
                width=105,
            ),

        "Price":
            st.column_config.TextColumn(
                "Price",
                width=80,
            ),

        "Change":
            st.column_config.TextColumn(
                "Change",
                width=90,
            ),

        "Change %":
            st.column_config.TextColumn(
                "Change %",
                width=75,
            ),

        "Policy Status":
            st.column_config.TextColumn(
                "Policy Status",
                width=105,
            ),

        "Market Status":
            st.column_config.TextColumn(
                "Market Status",
                width=105,
            ),

        "Date":
            st.column_config.TextColumn(
                "Date",
                width=120,
            ),
    }

    # =================================
    # Matrix
    # =================================

    st.dataframe(
        styled_df,
        column_config=column_config,
        hide_index=True,
        width="stretch",
        height=650,
    )
