import streamlit as st

from scheduler import start_scheduler
from database import Session
from product import product_page
from dashboard_v2 import dashboard_page


st.set_page_config(
    page_title="Price Monitor",
    page_icon="📊",
    layout="wide"
)

# 자동 가격 수집 시작
start_scheduler()


session = Session()


st.sidebar.title(
    "Price Monitor"
)


menu = st.sidebar.radio(
    "메뉴",
    [
        "📊 Dashboard",
        "📦 상품 관리"
    ]
)


if menu == "📊 Dashboard":

    dashboard_page(session)


elif menu == "📦 상품 관리":

    product_page(session)