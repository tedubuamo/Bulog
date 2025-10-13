import streamlit as st

USERNAME = "admin"
PASSWORD = "admin123"

def show():
    st.title("🔐Login Sentral Pangan🌾")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state.login_status = True
            st.success("✅ Login berhasil")
            st.rerun()
        else:
            st.error("❌ Username atau password salah")
