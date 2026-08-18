# dashboard/changed_today.py

import streamlit as st
from datetime import datetime

from database import (
    Price,
    Product
)


def render_changed_today(
    session,
    filters=None
):

    st.subheader(
        "📡 Changed Today"
    )


    today = (
        datetime.now()
        .strftime("%Y-%m-%d")
    )


    # =====================
    # Price + Product Query
    # =====================

    query = (

        session
        .query(
            Price,
            Product
        )

        .join(
            Product,
            Price.product_id == Product.id
        )

        .filter(
            Price.date.like(
                f"{today}%"
            )
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


        # Product Filter

        if products:

            query = query.filter(
                Product.product.in_(
                    products
                )
            )


        # Channel Filter

        if channels:

            query = query.filter(
                Product.channel.in_(
                    channels
                )
            )


        # Country Filter

        if countries:

            query = query.filter(
                Product.country.in_(
                    countries
                )
            )


        # Search Filter

        if search:

            query = query.filter(
                Product.product.contains(
                    search
                )
            )


    results = query.all()



    if not results:

        st.info(
            "No price changes today."
        )

        return



    # =====================
    # KPI
    # =====================

    changed_products = set()


    for price, product in results:

        changed_products.add(
            product.id
        )


    st.metric(
        "Changed Product Count",
        len(changed_products)
    )



    # =====================
    # Table
    # =====================

    rows = []


    for price, product in results:


        rows.append(

            {

                "Product":
                    product.product,

                "Channel":
                    product.channel,

                "Country":
                    product.country,

                "Price":
                    price.price,

                "Updated":
                    price.date

            }

        )



    st.dataframe(

        rows,

        hide_index=True,

        use_container_width=True

    )