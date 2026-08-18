import streamlit as st

from database import SystemStatus
from scheduler import scheduler


# =================================
# Date / Time Format
# =================================

def format_datetime(value):

    if not value:
        return "-"

    try:
        return value.strftime(
            "%Y-%m-%d %H:%M"
        )

    except AttributeError:
        return str(value)[:16]


# =================================
# Status Helpers
# =================================

def get_status(value):

    return str(
        value or ""
    ).strip().upper()


def status_icon(status):

    status = get_status(status)

    if status == "FAILED":
        return "🔴"

    if status == "PARTIAL":
        return "🟠"

    if status == "RUNNING":
        return "🔵"

    if status == "SUCCESS":
        return "🟢"

    return "⚪"


# =================================
# Scheduler Status
# =================================

def render_scheduler_status(session):

    # =================================
    # Main Section
    # =================================

    st.subheader("⚙️ System Status")

    # =================================
    # Load System Status
    # =================================

    statuses = (
        session
        .query(SystemStatus)
        .order_by(
            SystemStatus.id.desc()
        )
        .all()
    )

    # =================================
    # No Data
    # =================================

    if not statuses:

        with st.container(border=True):

            st.markdown(
                "**Overall Status**"
            )

            st.caption(
                "현재 시스템 상태 데이터가 없습니다."
            )

            st.info(
                "No system status data"
            )

        return

    # =================================
    # Collector 제외
    # Collection Monitoring에서 관리
    # =================================

    system_statuses = [
        item
        for item in statuses
        if "collector"
        not in str(
            item.service or ""
        ).lower()
    ]

    # =================================
    # No System Service
    # =================================

    if not system_statuses:

        with st.container(border=True):

            st.markdown(
                "**Overall Status**"
            )

            st.caption(
                "현재 모니터링 중인 "
                "System Service가 없습니다."
            )

            st.success(
                "🟢 System operating normally"
            )

        return

    # =================================
    # Service별 최신 상태
    # =================================

    latest = {}

    for item in system_statuses:

        service = (
            item.service
            or "System"
        )

        if service not in latest:

            latest[service] = item

    latest_statuses = list(
        latest.values()
    )

    # =================================
    # Status Groups
    # =================================

    failed = [
        item
        for item in latest_statuses
        if get_status(item.status)
        == "FAILED"
    ]

    partial = [
        item
        for item in latest_statuses
        if get_status(item.status)
        == "PARTIAL"
    ]

    running = [
        item
        for item in latest_statuses
        if get_status(item.status)
        == "RUNNING"
    ]

    # =================================
    # 1. OVERALL STATUS
    # =================================

    with st.container(border=True):

        st.markdown(
            "**Overall Status**"
        )

        st.caption(
            "현재 시스템 전체 운영 상태"
        )

        if failed:

            st.error(
                f"🔴 {len(failed)} "
                f"system service(s) failed"
            )

        elif partial:

            st.warning(
                f"🟠 {len(partial)} "
                f"system service(s) "
                f"partially completed"
            )

        elif running:

            st.info(
                "🔵 System operation "
                "in progress"
            )

        else:

            st.success(
                "🟢 System operating normally"
            )

        # ---------------------------------
        # Service Summary
        # ---------------------------------

        status_cols = st.columns(4)

        with status_cols[0]:

            st.metric(
                "Services",
                len(latest_statuses),
            )

        with status_cols[1]:

            st.metric(
                "FAILED",
                len(failed),
            )

        with status_cols[2]:

            st.metric(
                "PARTIAL",
                len(partial),
            )

        with status_cols[3]:

            st.metric(
                "RUNNING",
                len(running),
            )

    st.write("")

    # =================================
    # 2. SYSTEM ISSUES
    # =================================

    issues = failed + partial

    with st.container(border=True):

        st.markdown(
            "**System Issues**"
        )

        if issues:

            st.caption(
                "확인이 필요한 "
                "System Service"
            )

            for item in issues:

                service = (
                    item.service
                    or "System"
                )

                status = (
                    get_status(
                        item.status
                    )
                    or "UNKNOWN"
                )

                message = getattr(
                    item,
                    "message",
                    None,
                )

                icon = status_icon(
                    status
                )

                if message:

                    st.markdown(
                        f"{icon} **{service}**"
                    )

                    st.caption(
                        message
                    )

                else:

                    st.markdown(
                        f"{icon} **{service}**"
                    )

                    st.caption(
                        f"Status: {status}"
                    )

        else:

            st.caption(
                "현재 확인이 필요한 "
                "시스템 장애가 없습니다."
            )

            st.success(
                "✅ No system issues"
            )

    st.write("")

    # =================================
    # Last Run
    # =================================

    latest_run = next(
        (
            item
            for item in system_statuses
            if getattr(
                item,
                "last_run",
                None,
            )
        ),
        None,
    )

    # =================================
    # Next Run
    # =================================

    next_run = None

    try:

        job = scheduler.get_job(
            "price_monitor"
        )

        if job:

            next_run = (
                job.next_run_time
            )

    except Exception:

        next_run = None

    # =================================
    # Format Run Times
    # =================================

    last_run_text = "-"

    if latest_run:

        last_run_text = format_datetime(
            latest_run.last_run
        )

    next_run_text = format_datetime(
        next_run
    )

    # =================================
    # 3. SCHEDULER TIMING
    # =================================

    with st.container(border=True):

        st.markdown(
            "**Scheduler Timing**"
        )

        st.caption(
            "Price Monitor Scheduler "
            "실행 시간"
        )

        run_cols = st.columns(2)

        with run_cols[0]:

            st.caption(
                "Last Run"
            )

            st.markdown(
                f"### {last_run_text}"
            )

        with run_cols[1]:

            st.caption(
                "Next Run"
            )

            st.markdown(
                f"### {next_run_text}"
            )


# =================================
# Main Entry
# =================================

def render(session):

    render_scheduler_status(
        session
    )