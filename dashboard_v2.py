import streamlit as st

from database import Product

from dashboard.filters import render_filters
from dashboard.matrix import render_price_matrix
from dashboard.history import render_price_history
from dashboard.collection_monitor import render_collection_monitor
from dashboard.scheduler_status import render_scheduler_status
from dashboard.price_movement import render_price_movement
from dashboard.alert_center import render_alert_center


# =================================
# Dashboard UI / UX Style
# =================================

def apply_dashboard_style():

    st.markdown(
        """
        <style>

        /* =================================
           Main Container
           ================================= */

        .block-container {
            max-width: 1600px;
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }


        /* =================================
           Main Title
           ================================= */

        h1 {
            font-size: 2rem !important;
            margin-top: 0 !important;
            margin-bottom: 0.15rem !important;
        }


        /* =================================
           Section Title
           ================================= */

        h2 {
            font-size: 1.45rem !important;
            margin-top: 0.6rem !important;
            margin-bottom: 0.5rem !important;
        }

        h3 {
            font-size: 1.15rem !important;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
        }


        /* =================================
           Caption
           ================================= */

        [data-testid="stCaptionContainer"] {
            font-size: 0.82rem;
        }


        /* =================================
           Divider
           ================================= */

        hr {
            margin-top: 1.1rem !important;
            margin-bottom: 1.1rem !important;
        }


        /* =================================
           Metrics
           ================================= */

        [data-testid="stMetricLabel"] {
            font-size: 0.8rem;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.55rem;
        }


        /* =================================
           Alert / Status
           ================================= */

        [data-testid="stAlert"] {
            padding-top: 0.45rem;
            padding-bottom: 0.45rem;
        }


        /* =================================
           Expander
           ================================= */

        [data-testid="stExpander"] {
            margin-top: 0.35rem;
            margin-bottom: 0.7rem;
        }

        [data-testid="stExpander"] details {
            border-radius: 0.5rem;
        }


        /* =================================
           Expander Header
           ================================= */

        [data-testid="stExpander"] summary {
            font-size: 1.05rem;
            font-weight: 600;
        }


        </style>
        """,
        unsafe_allow_html=True
    )


# =================================
# Main Dashboard
# =================================

def dashboard_page(session):

    # =================================
    # Common Style
    # =================================

    apply_dashboard_style()


    # =================================
    # Header
    # =================================

    st.title(
        "📊 MGPM Price Monitor"
    )

    st.caption(
        "Global Market Price Monitoring Dashboard"
    )


    # =================================
    # Product Data
    # =================================

    products_db = (
        session
        .query(Product)
        .all()
    )

    products = sorted(
        {
            p.product
            for p in products_db
            if p.product
        }
    )

    countries = sorted(
        {
            p.country
            for p in products_db
            if p.country
        }
    )

    channels = sorted(
        {
            p.channel
            for p in products_db
            if p.channel
        }
    )


    # =================================
    # Filters
    # =================================

    filters = render_filters(
        products=products,
        countries=countries,
        channels=channels
    )


    # =================================
    # 1. Product × Channel Matrix
    # =================================

    render_price_matrix(
        session,
        filters
    )


    # =================================
    # Separator
    # =================================

    st.divider()


    # =================================
    # 2. Price History
    # =================================

    with st.expander(
        "📈 Price History",
        expanded=False
    ):

        st.caption(
            "Product / Channel별 과거 가격 흐름을 확인합니다."
        )

        render_price_history(
            session,
            filters
        )


    # =================================
    # 3. Advanced Price Analysis
    # =================================

    with st.expander(
        "🔎 Advanced Price Analysis",
        expanded=False
    ):

        st.caption(
            "가격 변동을 상세하게 분석합니다."
        )

        render_price_movement(
            session,
            filters
        )


    # =================================
    # Separator
    # =================================

    st.divider()


    # =================================
    # 4. Alert Center
    # =================================

    render_alert_center(
        session,
        filters
    )


    # =================================
    # Separator
    # =================================

    st.divider()


    # =================================
    # 5. Collection Monitoring
    # =================================

    render_collection_monitor(
        session
    )


    # =================================
    # Separator
    # =================================

    st.divider()


    # =================================
    # 6. System Status
    # =================================

    render_scheduler_status(
        session
    )


# =================================
# Alert Management Page
# =================================

def alert_management_page(session):

    apply_dashboard_style()

    st.title(
        "🚨 Price Alert Management"
    )

    render_alert_center(
        session,
        None
    )