import streamlit as st

USERNAME = "admin"
PASSWORD = "admin123"

def init_session():
    if "login_status" not in st.session_state:
        st.session_state.login_status = False
    if "page" not in st.session_state:
        st.session_state.page = "Login"

def show_sidebar():
    st.sidebar.title("📊 Menu Navigasi")
    if st.session_state.login_status:
        st.sidebar.success(f"👋 Selamat datang, {USERNAME}")
        st.session_state.page = st.sidebar.radio("Pilih Halaman", [
            "Scrap Konsumen", "Scrap Produsen", "Insight", "Forecasting", "Monitoring Harga"])
        if st.sidebar.button("🔓 Logout"):
            st.session_state.login_status = False
            st.rerun()
    else:
        st.sidebar.warning("🔒 Login terlebih dahulu")
