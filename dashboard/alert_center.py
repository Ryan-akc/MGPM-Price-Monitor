import streamlit as st

from datetime import datetime

from database import Alert


# =================================
# Date / Time
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
# Alert Type
# =================================

def get_alert_type(alert):

    if alert.alert_type == "SYSTEM":

        return (
            "SYSTEM",
            alert.message
            or "System failure",
        )

    if alert.alert_type == "DROP_PERCENT":

        return (
            "PRICE DROP",
            alert.message
            or "Price dropped",
        )

    if alert.alert_type == "RISE_PERCENT":

        return (
            "PRICE RISE",
            alert.message
            or "Price increased",
        )

    if alert.alert_type == "POLICY":

        return (
            "PRICE POLICY",
            alert.message
            or "Price policy violation",
        )

    return (
        alert.alert_type
        or "ALERT",
        alert.message
        or "",
    )


# =================================
# Priority Icon
# =================================

def get_priority_icon(alert):

    priority = alert.priority or "NORMAL"

    if alert.status == "NEW":
        return "🔴"

    if priority == "HIGH":
        return "🔴"

    return "🟠"


# =================================
# Alert Center
# =================================

def render_alert_center(
    session,
    filters=None,
):

    # =================================
    # Main Section
    # =================================

    st.subheader("🔔 Alert Center")

    # =================================
    # Load Alerts
    # =================================

    alerts = (
        session.query(Alert)
        .order_by(Alert.id.desc())
        .all()
    )

    # =================================
    # Empty State
    # =================================

    if not alerts:

        with st.container(border=True):

            st.markdown(
                "**Alert Summary**"
            )

            st.caption(
                "현재 등록된 Alert가 없습니다."
            )

            st.success(
                "✅ No alerts"
            )

        return

    # =================================
    # Status Count
    # =================================

    new_alerts = [
        alert
        for alert in alerts
        if alert.status == "NEW"
    ]

    active_alerts = [
        alert
        for alert in alerts
        if alert.status == "ACTIVE"
    ]

    resolved_alerts = [
        alert
        for alert in alerts
        if alert.status == "RESOLVED"
    ]

    attention_alerts = [
        alert
        for alert in alerts
        if alert.status in (
            "NEW",
            "ACTIVE",
        )
    ]

    # =================================
    # 1. ALERT SUMMARY
    # =================================

    with st.container(border=True):

        st.markdown(
            "**Alert Summary**"
        )

        st.caption(
            "현재 Alert 상태별 현황"
        )

        summary_cols = st.columns(4)

        with summary_cols[0]:

            st.metric(
                "Total",
                len(alerts),
            )

        with summary_cols[1]:

            st.metric(
                "NEW",
                len(new_alerts),
            )

        with summary_cols[2]:

            st.metric(
                "ACTIVE",
                len(active_alerts),
            )

        with summary_cols[3]:

            st.metric(
                "RESOLVED",
                len(resolved_alerts),
            )

    st.write("")

    # =================================
    # 2. ATTENTION STATUS
    # =================================

    with st.container(border=True):

        st.markdown(
            "**Attention Alerts**"
        )

        if attention_alerts:

            st.caption(
                f"⚠️ {len(attention_alerts)} "
                f"alert(s) require attention"
            )

        else:

            st.caption(
                "현재 확인이 필요한 Alert가 없습니다."
            )

            st.success(
                "✅ No active alerts"
            )

    # =================================
    # No Active Alert
    # =================================

    if not attention_alerts:

        return

    st.write("")

    # =================================
    # 3. ALERT DETAIL
    # =================================

    with st.container(border=True):

        st.markdown(
            "**Alert Detail**"
        )

        st.caption(
            "NEW 및 ACTIVE Alert 상세"
        )

        # =================================
        # Alert Cards
        # =================================

        for index, alert in enumerate(
            attention_alerts
        ):

            priority = (
                alert.priority
                or "NORMAL"
            )

            priority_icon = (
                get_priority_icon(alert)
            )

            title, message = (
                get_alert_type(alert)
            )

            # =================================
            # Individual Alert
            # =================================

            with st.container(
                border=True
            ):

                # ---------------------------------
                # Header
                # ---------------------------------

                st.markdown(
                    f"{priority_icon} "
                    f"**{alert.status} · "
                    f"{priority} · "
                    f"{title}**"
                )

                # ---------------------------------
                # Message
                # ---------------------------------

                if message:

                    st.write(message)

                # ---------------------------------
                # Price Information
                # ---------------------------------

                if (
                    alert.old_price
                    is not None
                    and
                    alert.new_price
                    is not None
                ):

                    st.caption(
                        f"Price: "
                        f"${alert.old_price:.2f}"
                        f" → "
                        f"${alert.new_price:.2f}"
                    )

                elif (
                    alert.new_price
                    is not None
                ):

                    st.caption(
                        f"Current Price: "
                        f"${alert.new_price:.2f}"
                    )

                # ---------------------------------
                # Change Rate
                # ---------------------------------

                if (
                    alert.change_rate
                    is not None
                ):

                    st.caption(
                        f"Change: "
                        f"{alert.change_rate:+.1f}%"
                    )

                # ---------------------------------
                # Action Buttons
                # ---------------------------------

                action_cols = st.columns(2)

                # ---------------------------------
                # Confirm
                # NEW → ACTIVE
                # ---------------------------------

                with action_cols[0]:

                    if alert.status == "NEW":

                        if st.button(
                            "✓ Confirm",
                            key=(
                                f"view_{alert.id}"
                            ),
                            use_container_width=True,
                        ):

                            alert.status = (
                                "ACTIVE"
                            )

                            alert.viewed_at = (
                                datetime.now()
                                .strftime(
                                    "%Y-%m-%d %H:%M"
                                )
                            )

                            session.commit()

                            st.rerun()

                    else:

                        st.button(
                            "✓ Confirmed",
                            key=(
                                f"viewed_{alert.id}"
                            ),
                            disabled=True,
                            use_container_width=True,
                        )

                # ---------------------------------
                # Resolve
                # NEW / ACTIVE → RESOLVED
                # ---------------------------------

                with action_cols[1]:

                    if st.button(
                        "✓ Resolve",
                        key=(
                            f"resolve_{alert.id}"
                        ),
                        use_container_width=True,
                    ):

                        alert.status = (
                            "RESOLVED"
                        )

                        alert.resolved_at = (
                            datetime.now()
                            .strftime(
                                "%Y-%m-%d %H:%M"
                            )
                        )

                        session.commit()

                        st.rerun()