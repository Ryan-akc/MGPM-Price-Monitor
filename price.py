import streamlit as st
import pandas as pd
from database import Product, Price
from datetime import date


def price_page(session):

    st.header("💲 가격 관리")

    products = session.query(Product).all()

    if len(products) == 0:
        st.warning("먼저 상품을 등록하세요.")
        return

    product_map = {
        f"{p.channel} | {p.product}": p.id
        for p in products
    }

    selected = st.selectbox(
        "상품 선택",
        list(product_map.keys())
    )

    price = st.number_input(
        "판매 가격",
        min_value=0.0,
        step=0.01,
        format="%.2f"
    )

    save_date = st.date_input(
        "날짜",
        value=date.today()
    )

    if st.button("가격 저장"):

        session.add(
            Price(
                product_id=product_map[selected],
                price=price,
                date=str(save_date)
            )
        )

        session.commit()

        st.success("가격이 저장되었습니다.")

        st.rerun()

    st.divider()

    st.subheader("가격 이력")

    history = session.query(Price).filter(
        Price.product_id == product_map[selected]
    ).order_by(Price.date.desc()).all()

    if len(history) == 0:

        st.info("등록된 가격이 없습니다.")

    else:

        rows = []

        for h in history:

            rows.append({
                "날짜": h.date,
                "가격": h.price
            })

        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )