# dashboard/alerts.py

import streamlit as st
import pandas as pd

from database import (
    Alert,
    Product
)



def render_alert_center(
    session,
    filters=None
):

    st.subheader(
        "🚨 Active Alert Center"
    )


    # =====================
    # Alert + Product Query
    # =====================

    query = (

        session
        .query(
            Alert,
            Product
        )

        .join(
            Product,
            Alert.product_id == Product.id
        )

        .filter(
            Alert.status == "ACTIVE"
        )

    )


    # =====================
    # Global Filter
    # =====================

    if filters:


        products = filters.get(
            "products",
            []
        )

        channels = filters.get(
            "channels",
            []
        )

        countries = filters.get(
            "countries",
            []
        )

        search = filters.get(
            "search",
            ""
        )


        if products:

            query = query.filter(
                Product.product.in_(
                    products
                )
            )


        if channels:

            query = query.filter(
                Product.channel.in_(
                    channels
                )
            )


        if countries:

            query = query.filter(
                Product.country.in_(
                    countries
                )
            )


        if search:

            query = query.filter(
                Product.product.contains(
                    search
                )
            )


    # =====================
    # Order + Limit
    # =====================

    query = (

        query

        .order_by(
            Alert.id.desc()
        )

        .limit(50)

    )


    results = query.all()



    if not results:

        st.success(
            "No active alerts."
        )

        return



    # =====================
    # DataFrame
    # =====================

    rows = []


    for alert, product in results:


        rows.append(

            {

                "Product":
                    product.product,

                "Channel":
                    product.channel,

                "Country":
                    product.country,

                "Alert":
                    alert.alert_type,

                "Old Price":
                    alert.old_price,

                "New Price":
                    alert.new_price,

                "Change %":
                    alert.change_rate,

                "Message":
                    alert.message or "-"

            }

        )



    df = pd.DataFrame(
        rows
    )


    st.dataframe(

        df,

        hide_index=True,

        use_container_width=True

    )