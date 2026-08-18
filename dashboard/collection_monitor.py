import streamlit as st

from database import (
    CollectionLog,
    CollectionResult,
)


# =================================
# Status Helpers
# =================================

def get_status(obj):
    return str(
        getattr(obj, "status", "")
    ).strip().upper()


def status_icon(status):
    status = str(status).upper()

    if status == "SUCCESS":
        return "🟢"

    if status == "PARTIAL":
        return "🟠"

    if status in ("FAILED", "BLOCKED"):
        return "🔴"

    return "⚪"


def status_text(status):
    status = str(status).upper()

    if status in (
        "SUCCESS",
        "PARTIAL",
        "FAILED",
        "BLOCKED",
    ):
        return status

    return status or "-"


# =================================
# Format Helpers
# =================================

def format_price(price):

    if price is None:
        return "-"

    try:
        return f"{float(price):,.2f}"

    except Exception:
        return str(price)


def format_datetime(value):

    if value is None:
        return "-"

    if hasattr(value, "strftime"):
        return value.strftime(
            "%Y-%m-%d %H:%M"
        )

    return str(value).replace("T", " ")[:16]


# =================================
# Collection Monitor
# =================================

def render_collection_monitor(session):

    # =================================
    # Main Section
    # =================================

    st.divider()

    st.subheader("📡 Collection Monitoring")

    # =================================
    # Collection Logs
    # =================================

    logs = (
        session.query(CollectionLog)
        .order_by(CollectionLog.id.desc())
        .limit(30)
        .all()
    )

    if not logs:
        st.info("No collection history found.")
        return

    latest_log = logs[0]

    # =================================
    # Status Count
    # =================================

    total_runs = len(logs)

    success_runs = sum(
        1
        for log in logs
        if get_status(log) == "SUCCESS"
    )

    partial_runs = sum(
        1
        for log in logs
        if get_status(log) == "PARTIAL"
    )

    failed_runs = sum(
        1
        for log in logs
        if get_status(log) == "FAILED"
    )

    blocked_runs = sum(
        1
        for log in logs
        if get_status(log) == "BLOCKED"
    )

    # =================================
    # 1. COLLECTION STATUS
    # =================================

    with st.container(border=True):

        st.markdown("**Collection Status**")

        st.caption(
            "최근 30회 수집 실행 상태"
        )

        status_cols = st.columns(5)

        with status_cols[0]:
            st.metric(
                "Runs",
                total_runs,
            )

        with status_cols[1]:
            st.metric(
                "SUCCESS",
                success_runs,
            )

        with status_cols[2]:
            st.metric(
                "PARTIAL",
                partial_runs,
            )

        with status_cols[3]:
            st.metric(
                "FAILED",
                failed_runs,
            )

        with status_cols[4]:
            st.metric(
                "BLOCKED",
                blocked_runs,
            )

    # =================================
    # Section Spacing
    # =================================

    st.write("")

    # =================================
    # Latest Collection Information
    # =================================

    latest_status = get_status(
        latest_log
    )

    latest_time = getattr(
        latest_log,
        "end_time",
        None,
    )

    if latest_time is None:

        latest_time = getattr(
            latest_log,
            "start_time",
            None,
        )

    latest_run_id = getattr(
        latest_log,
        "id",
        "-",
    )

    # =================================
    # 2. LATEST COLLECTION
    # =================================

    with st.container(border=True):

        st.markdown("**Latest Collection**")

        st.caption(
            "가장 최근 실행된 Collection 상태"
        )

        latest_cols = st.columns(
            [1.2, 1, 2.2]
        )

        with latest_cols[0]:

            st.caption("Status")

            st.markdown(
                f"### {status_icon(latest_status)} "
                f"{status_text(latest_status)}"
            )

        with latest_cols[1]:

            st.caption("Run ID")

            st.markdown(
                f"### {latest_run_id}"
            )

        with latest_cols[2]:

            st.caption("Collection Time")

            st.markdown(
                f"### {format_datetime(latest_time)}"
            )

    st.write("")

    # =================================
    # Find Collection Results
    # =================================

    collection_id = getattr(
        latest_log,
        "id",
        None,
    )

    results = []

    if collection_id is not None:

        results = (
            session.query(CollectionResult)
            .filter(
                CollectionResult.collection_id
                == collection_id
            )
            .order_by(
                CollectionResult.id.asc()
            )
            .all()
        )

    # =================================
    # Fallback
    # =================================

    if not results:

        latest_result = (
            session.query(CollectionResult)
            .order_by(
                CollectionResult.id.desc()
            )
            .first()
        )

        if latest_result is not None:

            collection_id = (
                latest_result.collection_id
            )

            results = (
                session.query(CollectionResult)
                .filter(
                    CollectionResult.collection_id
                    == collection_id
                )
                .order_by(
                    CollectionResult.id.asc()
                )
                .all()
            )

    if not results:

        with st.container(border=True):

            st.markdown(
                "**Collection Results**"
            )

            st.info(
                "No CollectionResult records found."
            )

        return

    # =================================
    # Result Counts
    # =================================

    result_total = len(results)

    result_success = sum(
        1
        for result in results
        if get_status(result) == "SUCCESS"
    )

    result_partial = sum(
        1
        for result in results
        if get_status(result) == "PARTIAL"
    )

    result_failed = sum(
        1
        for result in results
        if get_status(result) == "FAILED"
    )

    result_blocked = sum(
        1
        for result in results
        if get_status(result) == "BLOCKED"
    )

    # =================================
    # 3. COLLECTION RESULTS
    # =================================

    with st.container(border=True):

        st.markdown(
            "**📦 Latest Collection Results**"
        )

        st.caption(
            f"Run ID {collection_id}에서 수집된 "
            f"상품별 결과"
        )

        result_cols = st.columns(5)

        with result_cols[0]:
            st.metric(
                "Total Results",
                result_total,
            )

        with result_cols[1]:
            st.metric(
                "SUCCESS",
                result_success,
            )

        with result_cols[2]:
            st.metric(
                "PARTIAL",
                result_partial,
            )

        with result_cols[3]:
            st.metric(
                "FAILED",
                result_failed,
            )

        with result_cols[4]:
            st.metric(
                "BLOCKED",
                result_blocked,
            )

        st.divider()

        st.markdown(
            "**Product Result Detail**"
        )

        rows = []

        for result in results:

            status = get_status(result)

            rows.append(
                {
                    "상품명": (
                        result.product or "-"
                    ),

                    "수집 상태": (
                        f"{status_icon(status)} "
                        f"{status_text(status)}"
                    ),

                    "Channel": (
                        result.channel or "-"
                    ),

                    "실제 수집 가격": (
                        format_price(
                            result.price
                        )
                    ),

                    "Shop Type": (
                        result.shop_type or "-"
                    ),

                    "Message": (
                        result.message or "-"
                    ),

                    "수집 시간": (
                        format_datetime(
                            result.created_at
                        )
                    ),
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
            height=min(
                500,
                38 + (len(rows) * 35)
            ),
            column_config={

                "상품명":
                    st.column_config.TextColumn(
                        "상품명",
                        width="medium",
                    ),

                "수집 상태":
                    st.column_config.TextColumn(
                        "수집 상태",
                        width="small",
                    ),

                "Channel":
                    st.column_config.TextColumn(
                        "Channel",
                        width="small",
                    ),

                "실제 수집 가격":
                    st.column_config.TextColumn(
                        "실제 수집 가격",
                        width="small",
                    ),

                "Shop Type":
                    st.column_config.TextColumn(
                        "Shop Type",
                        width="small",
                    ),

                "Message":
                    st.column_config.TextColumn(
                        "Message",
                        width="medium",
                    ),

                "수집 시간":
                    st.column_config.TextColumn(
                        "수집 시간",
                        width="medium",
                    ),
            },
        )


# =================================
# Main Entry
# =================================

def render(session):

    render_collection_monitor(session)