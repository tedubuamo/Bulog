import streamlit as st
import pandas as pd
import datetime
import time

st.title("📉 Monitoring Harga Beras Real-time")
st.caption("🔁 Grafik ini akan diperbarui secara otomatis setiap beberapa detik.")

if "monitor_data" not in st.session_state:
    st.session_state.monitor_data = pd.DataFrame(columns=["Waktu", "Harga"])

chart_placeholder = st.empty()

if st.button("Mulai Monitoring"):
    for i in range(100):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        harga_beras = 13000 + (i % 10)

        new_row = pd.DataFrame({"Waktu": [current_time], "Harga": [harga_beras]})
        st.session_state.monitor_data = pd.concat([st.session_state.monitor_data, new_row], ignore_index=True)

        chart_placeholder.line_chart(st.session_state.monitor_data.set_index("Waktu"))

        time.sleep(2)