import requests
import streamlit as st

st.set_page_config(page_title="FastAPI + Streamlit", layout="centered")

st.title("🚀 FastAPI 연동 페이지")
st.markdown("Streamlit을 통해 프론트를 제공합니다.")

with st.form("n8n 프로세스 실행"):
    try:
        data = st.text_input("디자인 업무일지 파일명을 입력해주세요. (예: OK_test_디자인업무일지)")
        submitted = st.form_submit_button("보내기")

        if submitted:
            if not data:
                st.warning("디자인 업무일지 파일명을 입력해주세요.")
            else:
                res = requests.post(
                    "http://localhost:8000/api/v1/products/xlsx-to-xml", json={"data": data})
                if res.status_code == 200:
                    st.success(f"성공! 응답: {res.json()}")
                else:
                    st.error(f"요청 실패: {res.json()}")

    except Exception as e:
        st.error(f"에러 발생: {e}")
