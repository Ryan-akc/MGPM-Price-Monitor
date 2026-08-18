from datetime import datetime

from database import (
    Price,
    PricePolicy,
    Alert,
    AlertRule,
    SystemStatus
)




# =================================
# Price Alert Create
# =================================

def create_alert(
    session,
    product_id,
    alert_type,
    old_price,
    new_price,
    change_rate,
    message
):

    # ---------------------------------
    # NEW / ACTIVE 상태의 동일 Alert
    # 중복 생성 방지
    # ---------------------------------

    exists = (
        session.query(Alert)
        .filter(
            Alert.product_id == product_id,
            Alert.alert_type == alert_type,
            Alert.new_price == new_price,
            Alert.status.in_(["NEW", "ACTIVE"])
        )
        .first()
    )

    if exists:
        return

    # ---------------------------------
    # 신규 Alert
    # ---------------------------------

    alert = Alert(
        product_id=product_id,
        alert_type=alert_type,
        priority="NORMAL",
        old_price=old_price,
        new_price=new_price,
        change_rate=change_rate,
        message=message,
        status="NEW",
        viewed_at=None,
        resolved_at=None
    )

    session.add(alert)


# =================================
# System Alert Create
# =================================

def create_system_alert(
    session,
    service,
    message
):

    alert_message = (
        f"{service} Failed\n{message}"
    )

    # ---------------------------------
    # NEW / ACTIVE 중복 방지
    # ---------------------------------

    exists = (
        session.query(Alert)
        .filter(
            Alert.alert_type == "SYSTEM",
            Alert.message == alert_message,
            Alert.status.in_(["NEW", "ACTIVE"])
        )
        .first()
    )

    if exists:
        return

    alert = Alert(
        product_id=None,
        alert_type="SYSTEM",
        priority="HIGH",
        old_price=None,
        new_price=None,
        change_rate=None,
        message=alert_message,
        status="NEW",
        viewed_at=None,
        resolved_at=None
    )

    session.add(alert)


# =================================
# Resolve Recovered System Alerts
# =================================

def resolve_recovered_system_alerts(
    session,
    failed_services
):

    # ---------------------------------
    # 아직 처리 중인 SYSTEM Alert
    # NEW / ACTIVE 모두 확인
    # ---------------------------------

    active_alerts = (
        session.query(Alert)
        .filter(
            Alert.alert_type == "SYSTEM",
            Alert.status.in_(["NEW", "ACTIVE"])
        )
        .all()
    )

    for alert in active_alerts:

        if not alert.message:
            continue

        first_line = (
            alert.message
            .split("\n", 1)[0]
            .strip()
        )

        service = first_line

        if service.endswith(" Failed"):

            service = service[
                :-len(" Failed")
            ].strip()

        # ---------------------------------
        # 장애 복구
        # ---------------------------------

        if service not in failed_services:

            alert.status = "RESOLVED"

            alert.resolved_at = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            )


# =================================
# Check Collector System Alert
# =================================

def check_system_alert(
    session
):

    # ---------------------------------
    # Latest status per service
    # ---------------------------------

    statuses = (
        session.query(SystemStatus)
        .order_by(SystemStatus.id.desc())
        .all()
    )

    latest = {}

    for item in statuses:

        service = (
            item.service
            or ""
        )

        if service not in latest:

            latest[service] = item

    # ---------------------------------
    # Current failed services
    # ---------------------------------

    failed_collectors = [
        item
        for item in latest.values()
        if item.status == "FAILED"
        and "collector" in (
            item.service or ""
        ).lower()
    ]

    failed_services = set()

    for collector in failed_collectors:

        service = (
            collector.service
            or "System"
        )

        failed_services.add(
            service
        )

        create_system_alert(
            session,
            service,
            collector.message or "Unknown error"
        )

    # ---------------------------------
    # Resolve recovered alerts
    # ---------------------------------

    resolve_recovered_system_alerts(
        session,
        failed_services
    )

    session.commit()


# =================================
# Price Policy Alert Check
# =================================

def check_price_policy(
    session,
    product_id,
    current_price,
    previous_price=None,
    change_rate=None
):
    """
    PricePolicy 검사

    기준:
        Min Allowed Price =
        target_price × (1 - tolerance / 100)

    현재 가격이 허용 최저가격보다 낮을 경우
    POLICY Alert 생성
    """

    policies = (
        session.query(PricePolicy)
        .filter(
            PricePolicy.product_id == product_id
        )
        .all()
    )

    if not policies:
        return

    for policy in policies:

        # -------------------------
        # 기준단가 확인
        # -------------------------

        if policy.target_price is None:
            continue

        target_price = float(
            policy.target_price
        )

        if target_price <= 0:
            continue

        # -------------------------
        # 최대 할인율
        # -------------------------

        tolerance = (
            float(policy.tolerance)
            if policy.tolerance is not None
            else 10.0
        )

        # -------------------------
        # 허용 최저가격
        # -------------------------

        min_allowed_price = (
            target_price
            * (
                1
                - tolerance / 100
            )
        )

        # -------------------------
        # POLICY violation
        # -------------------------

        if current_price < min_allowed_price:

            if change_rate is None:

                change_text = (
                    "Price policy violation"
                )

            else:

                change_text = (
                    f"Price changed "
                    f"{change_rate:+.1f}%"
                )

            create_alert(
                session,
                product_id,
                "POLICY",
                previous_price,
                current_price,
                change_rate,
                (
                    f"POLICY ALERT: "
                    f"Current price "
                    f"{current_price:.2f} "
                    f"is below minimum allowed price "
                    f"{min_allowed_price:.2f}. "
                    f"Reference price: "
                    f"{target_price:.2f}, "
                    f"Max discount: "
                    f"{tolerance:.1f}%. "
                    f"{change_text}"
                )
            )


# =================================
# Price Alert Check
# =================================

def check_price_alert(
    session,
    product_id
):

    prices = (
        session.query(Price)
        .filter(
            Price.product_id == product_id
        )
        .order_by(
            Price.id.desc()
        )
        .limit(2)
        .all()
    )

    if not prices:
        return

    # =================================
    # Current Price
    # =================================

    current = float(
        prices[0].price
    )

    # =================================
    # Previous Price
    # =================================

    previous = None
    change_rate = None

    if len(prices) >= 2:

        previous = float(
            prices[1].price
        )

        if previous != 0:

            change_rate = (
                (current - previous)
                / previous
                * 100
            )

    # =================================
    # DROP / RISE Alert
    # =================================

    if change_rate is not None:

        # -----------------------------
        # DROP
        # -----------------------------

        if any(r.alert_type == "DROP_PERCENT" and r.enabled == 1 and change_rate <= -abs(float(r.threshold)) for r in session.query(AlertRule).filter(AlertRule.product_id == product_id).all()):

            create_alert(
                session,
                product_id,
                "DROP_PERCENT",
                previous,
                current,
                change_rate,
                (
                    f"Price dropped "
                    f"{abs(change_rate):.1f}%"
                )
            )

        # -----------------------------
        # RISE
        # -----------------------------

        elif any(r.alert_type == "RISE_PERCENT" and r.enabled == 1 and change_rate >= abs(float(r.threshold)) for r in session.query(AlertRule).filter(AlertRule.product_id == product_id).all()):

            create_alert(
                session,
                product_id,
                "RISE_PERCENT",
                previous,
                current,
                change_rate,
                (
                    f"Price increased "
                    f"{change_rate:.1f}%"
                )
            )

    # =================================
    # Price Policy
    # =================================

    check_price_policy(
        session,
        product_id,
        current,
        previous,
        change_rate
    )

    # =================================
    # Commit
    # =================================

    session.commit()
