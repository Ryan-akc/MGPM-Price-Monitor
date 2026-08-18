import streamlit as st



def format_price(price, currency="USD"):

    if price is None:
        return "-"

    symbols = {
        "USD": "$",
        "EUR": "€",
        "KRW": "₩"
    }

    symbol = symbols.get(
        currency,
        currency
    )

    if currency == "KRW":
        return f"{symbol}{price:,.0f}"

    return f"{symbol}{price:,.2f}"



def format_percent(value):

    if value is None:
        return "-"

    if value > 0:
        return f"▲ {value:.2f}%"

    elif value < 0:
        return f"▼ {abs(value):.2f}%"

    return "0.00%"



def price_direction(value):

    """
    가격 변화 방향 반환
    """

    if value is None:
        return "neutral"

    if value > 0:
        return "up"

    elif value < 0:
        return "down"

    return "stable"



def price_status(value):

    if value is None:
        return "No Data"

    if value > 0:
        return "Price Rise"

    elif value < 0:
        return "Price Drop"

    return "Stable"



def metric_card(
    title,
    value,
    delta=None
):

    with st.container():

        st.metric(
            label=title,
            value=value,
            delta=delta
        )



def status_badge(status):

    if status == "SUCCESS":

        st.success(
            f"🟢 {status}"
        )

    elif status == "FAIL":

        st.error(
            f"🔴 {status}"
        )

    else:

        st.warning(
            f"🟡 {status}"
        )



def alert_color(alert_type):

    """
    Alert UI Color
    """

    colors = {

        "DROP":
            "green",

        "RISE":
            "red",

        "STABLE":
            "gray"

    }

    return colors.get(
        alert_type,
        "gray"
    )



def empty_message(message):

    st.info(
        f"ℹ️ {message}"
    )