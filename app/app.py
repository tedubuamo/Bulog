import streamlit as st
from utility.session import init_session, show_sidebar
from pages_customize import login, scrap_konsumen, scrap_produsen, insight, forecasting, monitoring, homepage
import base64
import os

# ====== CSS Styling ======
st.markdown(
    """
    <style>
        /* Background utama */
        .stApp {
            background-color: #204d86 !important;
            color: #000000 !important;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #ffae00 !important;
            color: #FFFFFF !important;
        }
        section[data-testid="stSidebar"] * {
            color: #000000 !important;
        }

        /* Header bar */
        header[data-testid="stHeader"] {
            background-color: #204d86 !important;
            color: #ffffff !important;
        }
        header[data-testid="stHeader"] * {
            color: #ffffff !important;
        }

        /* Judul halaman */
        h1, h2, h3 {
            color: #ffffff !important;
            font-weight: 1000;
        }

        /* Label input */
        label {
            color: #ffffff !important;
            font-weight: 600;
        }

        /* Input field */
        input, textarea, select {
            background-color: #A7C7E7 !important;
            color: #000000 !important;
            border: 0px solid #204d86 !important;
            border-radius: 5px;
        }
        input:focus, textarea:focus, select:focus {
            border-color: #204d86 !important;
            box-shadow: 0 0 5px rgba(32,77,134,0.4) !important;
        }

        /* Tombol */
        .stButton>button {
            background-color: #204d86 !important;
            color: #ffffff !important;
            border-radius: 5px;
            font-weight: 600;
            padding: 0.5rem 1rem;
        }
        .stButton>button:hover {
            background-color: #163a63 !important;
            color: #ffffff !important;
        }

        /* Container logo custom */
        .sidebar-logo-box {
            background-color: white;
            padding: 10px;
            border-radius: 12px;
            text-align: center;
            width: 100%;
            border: 3px solid #204d86;
            margin-bottom: 15px;
        }
        .sidebar-logo-box img {
            width: 100%; /* penuh container */
            max-width: 200px; /* batas maksimal */
            border-radius: 8px; /* pinggiran melengkung */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ====== Inisialisasi Session ======
init_session()

if not st.session_state.login_status:
    st.session_state.page = "Login"

def img_to_base64(path: str):
    """Konversi gambar ke base64, dengan pengecekan file."""
    if not os.path.exists(path):
        st.warning(f"Logo tidak ditemukan di {path}")
        return None
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Path logo relatif terhadap file ini (app.py)
BASE_DIR = os.path.dirname(__file__)
logo_path = os.path.join(BASE_DIR, "static", "logo.png")
logo_base64 = img_to_base64(logo_path)

with st.sidebar:
    if logo_base64:
        st.markdown(
            f"""
            <div style="background:white; padding:7px; border-radius:10px; text-align:center;">
                <img src="data:image/png;base64,{logo_base64}" width="250">
            </div>
            """,
            unsafe_allow_html=True
        )

# ====== Navigasi Sidebar ======
show_sidebar()

# ====== Routing Halaman ======
if st.session_state.page == "Login":
    login.show()
elif st.session_state.page == "Homepage":
    homepage.show()
elif st.session_state.page == "Scrap Konsumen":
    scrap_konsumen.show()
elif st.session_state.page == "Scrap Produsen":
    scrap_produsen.show()
elif st.session_state.page == "Monitoring Harga":
    monitoring.show()
elif st.session_state.page == "Insight":
    insight.show()
elif st.session_state.page == "Forecasting":
    forecasting.show()
