# C:\PriceMonitor\app.py

import streamlit as st

from scheduler import start_scheduler
from database import Session

from product import product_page

from dashboard_v2 import (
    dashboard_page,
    alert_management_page
)

from auth import (
    check_login,
    logout,
    show_user_info,
    is_editor,
    is_admin,
)

from user_management import (
    user_management_page,
)


# =================================
# Page Config
# =================================

st.set_page_config(

    page_title="MGPM Price Monitor",

    page_icon="📊",

    layout="wide"

)


# =================================
# Authentication
# =================================

if not check_login():

    st.stop()


# =================================
# Scheduler
# =================================

start_scheduler()


# =================================
# Database
# =================================

session = Session()


# =================================
# Sidebar
# =================================

st.sidebar.title(
    "📊 MGPM Price Monitor"
)

show_user_info()

st.sidebar.divider()


# =================================
# Menu
# =================================

if is_admin():

    menu = st.sidebar.radio(

        "Menu",

        [

            "📊 Dashboard",

            "🚨 Alert Management",

            "📦 Product Management",

            "👥 User Management",

        ]

    )

elif is_editor():

    menu = st.sidebar.radio(

        "Menu",

        [

            "📊 Dashboard",

            "🚨 Alert Management",

            "📦 Product Management",

        ]

    )

else:

    menu = st.sidebar.radio(

        "Menu",

        [

            "📊 Dashboard"

        ]

    )


# =================================
# Page
# =================================

if menu == "📊 Dashboard":

    dashboard_page(session)


elif menu == "🚨 Alert Management":

    if is_editor():

        alert_management_page(session)

    else:

        st.error(
            "You do not have permission "
            "to access this page."
        )


elif menu == "📦 Product Management":

    if is_editor():

        product_page(session)

    else:

        st.error(
            "You do not have permission "
            "to access this page."
        )


elif menu == "👥 User Management":

    if is_admin():

        user_management_page()

    else:

        st.error(
            "Admin permission required."
        )


# =================================
# Logout
# =================================

st.sidebar.divider()

logout()