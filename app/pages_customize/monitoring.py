import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

def show():
    st.title("📊 Monitoring Pemantauan Harga Pangan")
    st.subheader("Pantau harga komoditas pangan secara real-time")

    # --- Dummy Data ---
    # Misalnya data harga beras, cabai, bawang
    data = {
        "Tanggal": pd.date_range(end=pd.Timestamp.today(), periods=30),
        "Beras": np.random.randint(10000, 15000, 30),
        "Cabai": np.random.randint(20000, 60000, 30),
        "Bawang": np.random.randint(15000, 35000, 30),
    }
    df = pd.DataFrame(data)

    # --- Pilihan Filter ---
    komoditas = st.selectbox("Pilih Komoditas", ["Beras", "Cabai", "Bawang"])
    st.write(f"📌 Menampilkan harga untuk: **{komoditas}**")

    # --- Tabel Data ---
    st.dataframe(df[["Tanggal", komoditas]].rename(columns={komoditas: "Harga (Rp)"}))

    # --- Grafik Harga ---
    st.line_chart(df.set_index("Tanggal")[[komoditas]])

    # --- Simulasi Real-Time ---
    st.subheader("⏱️ Live Monitoring (Simulasi)")
    placeholder = st.empty()

    # Tombol mulai live update
    if st.button("Mulai Monitoring"):
        for i in range(30):
            new_price = df[komoditas].iloc[-1] + np.random.randint(-200, 200)
            new_row = {"Tanggal": pd.Timestamp.now(), komoditas: new_price}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            with placeholder.container():
                st.line_chart(df.set_index("Tanggal")[[komoditas]])
                st.write(f"Harga terbaru {komoditas}: **Rp {new_price:,}**")

            time.sleep(1)
