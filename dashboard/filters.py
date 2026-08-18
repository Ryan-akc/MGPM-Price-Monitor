import streamlit as st



def render_filters(
    products,
    countries,
    channels
):

    st.subheader(
        "🔍 Filters"
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        selected_countries = st.multiselect(

            "Country",

            ["All"] + sorted(countries),

            default=["All"]

        )



    with c2:

        selected_channels = st.multiselect(

            "Channel",

            ["All"] + sorted(channels),

            default=["All"]

        )



    with c3:

        selected_products = st.multiselect(

            "Product",

            ["All"] + sorted(products),

            default=["All"]

        )



    c4, c5 = st.columns(2)



    with c4:

        status = st.radio(

            "Status",

            [
                "All",
                "Below Target",
                "Above Target",
                "Changed Today"
            ],

            horizontal=True

        )



    with c5:

        search = st.text_input(

            "Search"

        )



    return {

        "countries":
            selected_countries,


        "channels":
            selected_channels,


        "products":
            selected_products,


        "status":
            status,


        "search":
            search

    }