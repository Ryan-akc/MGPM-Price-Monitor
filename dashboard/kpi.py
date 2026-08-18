import streamlit as st


def render_collection_kpi(
    total_count,
    success_count,
    fail_count,
    status,
    end_time,
    changed_today=0
):

    st.subheader(
        "📡 Collection Monitoring"
    )


    c1, c2, c3, c4, c5 = st.columns(5)


    with c1:
        st.metric(
            "Total Collection",
            total_count
        )


    with c2:
        st.metric(
            "Success",
            success_count
        )


    with c3:
        st.metric(
            "Fail",
            fail_count
        )


    with c4:
        st.metric(
            "Changed Today",
            changed_today
        )


    with c5:
        st.metric(
            "Status",
            status
        )


    if end_time:

        st.caption(
            f"🕒 Last Run : {end_time}"
        )

# 기존 호환용
def render_kpi(session):

    render_collection_kpi(session)