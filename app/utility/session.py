import streamlit as st

USERNAME = "admin"
PASSWORD = "admin123"

st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
    section[data-testid="stSidebar"] h1 {
        font-family: 'Poppins', sans-serif !important;
        font-size: 26px !important;   
        font-weight: 650 !important;     
    }
    </style>
    """,
    unsafe_allow_html=True
)

def init_session():
    if "login_status" not in st.session_state:
        st.session_state.login_status = False
    if "page" not in st.session_state:
        st.session_state.page = "Login"

def show_sidebar():
    st.sidebar.title("📊 Menu Navigasi")
    
    if st.session_state.login_status:        
        st.session_state.page = st.sidebar.radio(
            "Pilih Halaman",
            ["Homepage","Scrap Konsumen", "Scrap Produsen", "Monitoring Harga", "Insight", "Forecasting"]
        )
        
        # Tombol Logout dengan warna teks putih
        if st.sidebar.button("🔓 Logout"):
            st.session_state.login_status = False
            st.rerun()
    else:
        # Tampilkan error merah jika belum login
        st.sidebar.exception(Exception("🚨 Login terlebih dahulu"))