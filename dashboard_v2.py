import streamlit as st

from database import Session


def inject_style():

    st.markdown("""
    <style>

    .block-container{
        padding-top:1rem;
        padding-bottom:1rem;
        max-width:1400px;
    }

    div[data-testid="stMetric"]{
        padding:0.4rem;
    }

    </style>
    """,
    unsafe_allow_html=True)


def dashboard_page(session):

    inject_style()

    st.title("📊 Price Monitor Dashboard")

    st.caption("MGPM Dashboard v2")

    st.success("Dashboard v2 Ready")