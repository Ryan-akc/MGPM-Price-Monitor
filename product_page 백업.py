import streamlit as st
from database import Product
from collector import collect_price

SHOPS = ["amazon","yesstyle","stylekorean","jolse","stylevana"]
CURRENCIES = ["USD","EUR","KRW"]

def product_page(session):
    st.header("📦 상품 관리")

    with st.expander("➕ 새 상품 등록", expanded=False):
        with st.form("product_form", clear_on_submit=True):
            channel = st.text_input("채널명", placeholder="Amazon US")
            product = st.text_input("상품명")
            url = st.text_input("판매 URL")
            shop_type = st.selectbox("쇼핑몰", SHOPS)
            country = st.text_input("국가", value="US")
            currency = st.selectbox("통화", CURRENCIES)
            save = st.form_submit_button("상품 등록")

            if save:
                if not channel or not product or not url:
                    st.error("채널명, 상품명, URL은 필수입니다.")
                else:
                    session.add(Product(
                        channel=channel,
                        product=product,
                        url=url,
                        shop_type=shop_type,
                        country=country,
                        currency=currency
                    ))
                    session.commit()
                    st.success("상품 등록 완료")
                    st.rerun()

    st.divider()

    keyword = st.text_input("🔍 상품 검색")

    products = session.query(Product).order_by(Product.product).all()

    if keyword:
        k = keyword.lower()
        products = [p for p in products if k in p.product.lower() or k in p.channel.lower()]

    st.caption(f"등록 상품 : {len(products)}")

    if not products:
        st.info("등록된 상품이 없습니다.")
        return

    for p in products:
        with st.expander(f"{p.product} ({p.channel})"):
            st.write(f"**쇼핑몰** : {p.shop_type}")
            st.write(f"**국가** : {p.country}")
            st.write(f"**통화** : {p.currency}")
            st.write(f"**URL** : {p.url}")

            c1,c2 = st.columns([1,1])
            if c1.button("🔄 가격 확인", key=f"check_{p.id}"):
                price = collect_price(p.id)
                if price is not None:
                    st.success(f"현재 가격 : {price:.2f} {p.currency}")
                else:
                    st.error("가격 조회 실패")

            with st.form(f"edit_{p.id}"):
                st.subheader("✏️ 상품 수정")
                new_channel = st.text_input("채널명", value=p.channel)
                new_product = st.text_input("상품명", value=p.product)
                new_url = st.text_input("판매 URL", value=p.url)
                new_shop = st.selectbox("쇼핑몰", SHOPS, index=SHOPS.index(p.shop_type))
                new_country = st.text_input("국가", value=p.country)
                new_currency = st.selectbox("통화", CURRENCIES, index=CURRENCIES.index(p.currency))
                save_edit = st.form_submit_button("💾 저장")

                if save_edit:
                    p.channel = new_channel
                    p.product = new_product
                    p.url = new_url
                    p.shop_type = new_shop
                    p.country = new_country
                    p.currency = new_currency
                    session.commit()
                    st.success("수정 완료")
                    st.rerun()

            if st.button("🗑 삭제", key=f"delete_{p.id}"):
                session.delete(p)
                session.commit()
                st.success("삭제 완료")
                st.rerun()
