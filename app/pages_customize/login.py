# pages_customize/login.py
import streamlit as st

USERNAME = "admin"
PASSWORD = "admin123"

def show():
    st.title("🔐 Login Aplikasi")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state.login_status = True
            st.success("✅ Login berhasil")
            st.rerun()
        else:
            st.error("❌ Username atau password salah")
