import streamlit as st
from utility.session import init_session, show_sidebar
from pages_customize import login, scrap_konsumen, scrap_produsen, insight, forecasting, monitoring

init_session()

if not st.session_state.login_status:
    st.session_state.page = "Login"

# Sidebar navigasi
show_sidebar()

# Routing halaman
if st.session_state.page == "Login":
    login.show()
elif st.session_state.page == "Scrap Konsumen":
    scrap_konsumen.show()
elif st.session_state.page == "Scrap Produsen":
    scrap_produsen.show()
elif st.session_state.page == "Insight":
    insight.show()
elif st.session_state.page == "Forecasting":
    forecasting.show()
elif st.session_state.page == "Monitoring Harga":
    monitoring.show()
