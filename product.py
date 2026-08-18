import streamlit as st

from database import (
    Product,
    Price,
    PricePolicy
)

from collector import collect_price


# ============================================
# Constants
# ============================================

SHOPS = [
    "amazon",
    "yesstyle",
    "stylekorean",
    "jolse",
    "stylevana",
    "coupang"
]


CURRENCIES = [
    "USD",
    "EUR",
    "KRW"
]


# ============================================
# Display Helpers
# ============================================

def shop_display_name(shop):

    if not shop:
        return "UNKNOWN"

    return str(shop).strip().upper()


# ============================================
# Policy Helpers
# ============================================

def get_policy(session, product):

    return (
        session.query(PricePolicy)
        .filter(
            PricePolicy.product_id == product.id,
            PricePolicy.country == product.country,
            PricePolicy.channel == product.channel
        )
        .first()
    )


def calculate_min_allowed_price(
    target_price,
    tolerance
):

    if target_price is None:
        return None

    if tolerance is None:
        tolerance = 0

    return float(target_price) * (
        1 - float(tolerance) / 100
    )


def get_policy_status(
    current_price,
    target_price,
    tolerance
):

    if (
        current_price is None
        or target_price is None
        or target_price <= 0
    ):
        return "NO POLICY"

    min_allowed_price = calculate_min_allowed_price(
        target_price,
        tolerance
    )

    if current_price < min_allowed_price:
        return "POLICY ALERT"

    return "NORMAL"


# ============================================
# Product Detail
# ============================================

def render_product_detail(
    session,
    p
):

    # ========================================
    # Current Product Information
    # ========================================

    if not st.session_state.get(
        f"editing_product_{p.id}",
        False
    ):

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**쇼핑몰 :** "
                f"{shop_display_name(p.shop_type)}"
            )

            st.write(
                f"**통화 :** {p.currency}"
            )

        with col2:

            st.write(
                f"**URL :** {p.url}"
            )

        # ------------------------------------
        # Edit Button
        # ------------------------------------

        if st.button(
            "✏️ 상품 수정",
            key=f"edit_product_{p.id}"
        ):

            st.session_state[
                f"editing_product_{p.id}"
            ] = True

            st.rerun()


    else:

        # ====================================
        # Product Edit Form
        # ====================================

        st.subheader(
            "✏️ 상품 정보 수정"
        )


        # ====================================
        # Shop FIRST
        # ====================================

        current_shop = (
            str(p.shop_type).strip().lower()
            if p.shop_type
            else SHOPS[0]
        )


        if current_shop not in SHOPS:
            current_shop = SHOPS[0]


        edit_shop = st.selectbox(
            "쇼핑몰",
            SHOPS,
            index=SHOPS.index(current_shop),
            format_func=shop_display_name,
            key=f"edit_shop_{p.id}"
        )


        # ====================================
        # Channel = Shop
        # ====================================

        edit_channel = edit_shop.upper()


        # ====================================
        # Product
        # ====================================

        edit_product = st.text_input(
            "상품명",
            value=p.product or "",
            key=f"edit_product_name_{p.id}"
        )


        edit_url = st.text_input(
            "판매 URL",
            value=p.url or "",
            key=f"edit_url_{p.id}"
        )


        # ====================================
        # Currency
        # ====================================

        current_currency = (
            p.currency
            if p.currency in CURRENCIES
            else CURRENCIES[0]
        )


        edit_currency = st.selectbox(
            "통화",
            CURRENCIES,
            index=CURRENCIES.index(current_currency),
            key=f"edit_currency_{p.id}"
        )


        # ====================================
        # Save / Cancel
        # ====================================

        col_save, col_cancel = st.columns(2)


        with col_save:

            if st.button(
                "💾 상품 정보 저장",
                key=f"save_product_{p.id}"
            ):

                if (
                    not edit_product
                    or not edit_url
                ):

                    st.error(
                        "상품명과 URL은 필수입니다."
                    )

                else:

                    # --------------------------------
                    # Product
                    # --------------------------------

                    p.shop_type = edit_shop

                    p.channel = edit_channel

                    p.product = edit_product

                    p.url = edit_url

                    p.currency = edit_currency


                    # --------------------------------
                    # Existing Country 유지
                    # --------------------------------

                    existing_country = (
                        p.country
                        if p.country
                        else "US"
                    )


                    p.country = existing_country


                    # --------------------------------
                    # Price Policy
                    # --------------------------------

                    policies = (
                        session.query(PricePolicy)
                        .filter(
                            PricePolicy.product_id == p.id
                        )
                        .all()
                    )


                    for policy in policies:

                        policy.channel = edit_channel

                        policy.country = existing_country


                    session.commit()


                    st.session_state[
                        f"editing_product_{p.id}"
                    ] = False


                    st.success(
                        "상품 정보 수정 완료"
                    )

                    st.rerun()


        with col_cancel:

            if st.button(
                "취소",
                key=f"cancel_product_{p.id}"
            ):

                st.session_state[
                    f"editing_product_{p.id}"
                ] = False

                st.rerun()


    # ========================================
    # Latest Price
    # ========================================

    latest = (
        session.query(Price)
        .filter(
            Price.product_id == p.id
        )
        .order_by(
            Price.id.desc()
        )
        .first()
    )


    current_price = None


    if latest:

        current_price = float(
            latest.price
        )

        st.info(
            f"현재 가격 : "
            f"{current_price:.2f} "
            f"{p.currency}"
        )

    else:

        st.warning(
            "가격 데이터 없음"
        )


    st.divider()


    # ========================================
    # Price Policy
    # ========================================

    st.subheader(
        "📋 Price Policy"
    )


    policy = get_policy(
        session,
        p
    )


    if policy:

        current_target_price = (
            float(policy.target_price)
            if policy.target_price is not None
            else 0.0
        )

        current_tolerance = (
            float(policy.tolerance)
            if policy.tolerance is not None
            else 0.0
        )

    else:

        current_target_price = 0.0
        current_tolerance = 10.0


    col1, col2 = st.columns(2)


    with col1:

        new_target_price = st.number_input(
            "기준단가",
            min_value=0.0,
            value=current_target_price,
            step=0.01,
            format="%.2f",
            key=f"target_{p.id}"
        )


    with col2:

        new_tolerance = st.number_input(
            "최대 할인율 (%)",
            min_value=0.0,
            max_value=100.0,
            value=current_tolerance,
            step=0.5,
            format="%.1f",
            key=f"tolerance_{p.id}"
        )


    # ========================================
    # Min Allowed Price
    # ========================================

    if new_target_price > 0:

        min_allowed_price = (
            calculate_min_allowed_price(
                new_target_price,
                new_tolerance
            )
        )

        st.info(
            f"허용 최저가격 : "
            f"{min_allowed_price:.2f} "
            f"{p.currency}"
        )

    else:

        min_allowed_price = None

        st.warning(
            "기준단가를 입력하면 허용 최저가격이 계산됩니다."
        )


    # ========================================
    # Policy Status
    # ========================================

    if current_price is not None:

        status = get_policy_status(
            current_price,
            new_target_price,
            new_tolerance
        )

        if status == "POLICY ALERT":

            st.error(
                "🔴 POLICY ALERT "
                "- 현재 가격이 허용 최저가격보다 낮습니다."
            )

        elif status == "NORMAL":

            st.success(
                "🟢 POLICY NORMAL"
            )

        else:

            st.warning(
                "⚠ POLICY 상태 확인 필요"
            )


    # ========================================
    # Save Price Policy
    # ========================================

    if st.button(
        "💾 Price Policy 저장",
        key=f"save_policy_{p.id}"
    ):

        if new_target_price <= 0:

            st.error(
                "기준단가는 0보다 커야 합니다."
            )

        else:

            if policy:

                policy.target_price = (
                    new_target_price
                )

                policy.tolerance = (
                    new_tolerance
                )

                policy.country = (
                    p.country
                )

                policy.channel = (
                    p.channel
                )

            else:

                policy = PricePolicy(
                    product_id=p.id,
                    country=p.country,
                    channel=p.channel,
                    target_price=new_target_price,
                    tolerance=new_tolerance
                )

                session.add(
                    policy
                )


            session.commit()


            st.success(
                "Price Policy 저장 완료"
            )

            st.rerun()


    # ========================================
    # Collection
    # ========================================

    st.divider()


    if st.button(
        "🔄 가격 확인",
        key=f"collect_{p.id}"
    ):

        result = collect_price(
            p.id
        )

        if result:

            st.success(
                f"{result}"
            )

            st.rerun()

        else:

            st.error(
                "가격 조회 실패"
            )


    # ========================================
    # Delete
    # ========================================

    if st.button(
        "🗑 삭제",
        key=f"delete_{p.id}"
    ):

        # Price 삭제

        session.query(
            Price
        ).filter(
            Price.product_id == p.id
        ).delete(
            synchronize_session=False
        )


        # PricePolicy 삭제

        session.query(
            PricePolicy
        ).filter(
            PricePolicy.product_id == p.id
        ).delete(
            synchronize_session=False
        )


        # Product 삭제

        session.delete(
            p
        )

        session.commit()


        # Edit 상태 정리

        st.session_state.pop(
            f"editing_product_{p.id}",
            None
        )


        st.success(
            "상품 및 관련 정책 삭제 완료"
        )

        st.rerun()


# ============================================
# Product Page
# ============================================

def product_page(session):

    st.header(
        "📦 상품 관리"
    )


    # ========================================
    # New Product
    # ========================================

    with st.expander(
        "➕ 새 상품 등록"
    ):

        with st.form(
            "add_product",
            clear_on_submit=True
        ):

            # =================================
            # Shop FIRST
            # =================================

            shop = st.selectbox(
                "쇼핑몰",
                SHOPS,
                format_func=shop_display_name
            )


            # =================================
            # Channel = Shop
            # =================================

            channel = shop.upper()


            # =================================
            # Product
            # =================================

            product = st.text_input(
                "상품명"
            )


            url = st.text_input(
                "판매 URL"
            )


            # =================================
            # Currency
            # =================================

            currency = st.selectbox(
                "통화",
                CURRENCIES
            )


            st.divider()


            # =================================
            # Price Policy
            # =================================

            st.subheader(
                "📋 Price Policy"
            )


            target_price = st.number_input(
                "기준단가 (Reference Price)",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f"
            )


            tolerance = st.number_input(
                "최대 할인율 (%)",
                min_value=0.0,
                max_value=100.0,
                value=10.0,
                step=0.5,
                format="%.1f"
            )


            if target_price > 0:

                min_allowed_price = (
                    calculate_min_allowed_price(
                        target_price,
                        tolerance
                    )
                )

                st.info(
                    f"허용 최저가격 : "
                    f"{min_allowed_price:.2f} "
                    f"{currency}"
                )


            submitted = st.form_submit_button(
                "상품 등록"
            )


            if submitted:

                if (
                    not product
                    or not url
                ):

                    st.error(
                        "상품명과 URL은 필수입니다."
                    )

                elif target_price <= 0:

                    st.error(
                        "기준단가를 입력하세요."
                    )

                else:

                    # --------------------------------
                    # Internal Country
                    # --------------------------------
                    # 화면에는 표시하지 않음.
                    # 기존 DB 구조 유지를 위해 US 사용.

                    country = "US"


                    # --------------------------------
                    # Product
                    # --------------------------------

                    new_product = Product(
                        channel=channel,
                        product=product,
                        url=url,
                        shop_type=shop,
                        country=country,
                        currency=currency,
                        monitoring=1
                    )


                    session.add(
                        new_product
                    )


                    session.flush()


                    # --------------------------------
                    # PricePolicy
                    # --------------------------------

                    new_policy = PricePolicy(
                        product_id=new_product.id,
                        country=country,
                        channel=channel,
                        target_price=target_price,
                        tolerance=tolerance
                    )


                    session.add(
                        new_policy
                    )


                    session.commit()


                    st.success(
                        "상품 및 Price Policy 등록 완료"
                    )

                    st.rerun()


    st.divider()


    # ========================================
    # Product Summary
    # ========================================

    products = (
        session.query(Product)
        .order_by(
            Product.channel,
            Product.product
        )
        .all()
    )


    # ========================================
    # Channel Groups
    # ========================================

    channel_groups = {}


    for p in products:

        channel_name = (
            shop_display_name(p.channel)
            if p.channel
            else "미지정 채널"
        )


        if channel_name not in channel_groups:

            channel_groups[channel_name] = []


        channel_groups[channel_name].append(
            p
        )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "등록 상품",
            len(products)
        )


    with col2:

        st.metric(
            "등록 채널",
            len(channel_groups)
        )


    st.divider()


    # ========================================
    # Channel → Product Structure
    # ========================================

    for channel_name in sorted(
        channel_groups.keys(),
        key=lambda x: x.lower()
    ):

        channel_products = channel_groups[
            channel_name
        ]


        with st.expander(
            f"🛒 {channel_name}   |   등록 상품 {len(channel_products)}개",
            expanded=True
        ):

            for p in channel_products:

                with st.expander(
                    f"▸ {p.product}",
                    expanded=False
                ):

                    render_product_detail(
                        session,
                        p
                    )