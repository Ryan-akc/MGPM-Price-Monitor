import streamlit as st

st.set_page_config(
    page_title="Price Monitor",
    layout="wide"
)

st.title("🌎 Price Monitor")

st.write("첫 번째 프로그램이 정상적으로 실행되었습니다!")

st.sidebar.title("메뉴")

menu = st.sidebar.radio(
    "선택",
    ["Dashboard", "상품관리"]
)

if menu == "Dashboard":
    st.header("Dashboard")

    col1, col2 = st.columns(2)

    col1.metric("등록 상품", 0)
    col2.metric("오늘 가격변동", 0)

elif menu == "상품관리":
    st.header("상품관리")

    st.text_input("채널명")

    st.text_input("상품명")

    st.text_input("판매 URL")

    st.button("저장")