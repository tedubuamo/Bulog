import streamlit as st
import requests
import pandas as pd
import datetime
from io import BytesIO

st.set_page_config(page_title="Harga Pangan Bapanas", layout="centered")
st.title("📡 Ambil & Pratinjau Data Harga Pangan Bapanas")

# --- PILIH SUMBER DATA ---
data_type = st.radio("Pilih Sumber Data", ["Konsumen", "Produsen"])
level_harga_id = 3 if data_type == "Konsumen" else 1

# --- PILIH TANGGAL ---
tanggal = st.date_input("📅 Pilih Tanggal", value=datetime.date.today())
formatted = tanggal.strftime("%d/%m/%Y")
period_param = f"{formatted} - {formatted}"

# --- TAMPILKAN URL ---
url = f"https://api-panelhargav2.badanpangan.go.id/harga-pangan-table-province/export?province_id=15&period_date={period_param}&level_harga_id={level_harga_id}"
st.code(f"🔗 URL API:\n{url}")

# --- TOMBOL AMBIL DATA ---
if st.button("🚀 Ambil Data"):
    with st.spinner("Mengambil data dari API..."):
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            if response.content:
                # Baca langsung file Excel dari response ke DataFrame
                df_raw = pd.read_excel(BytesIO(response.content))
                df_raw.drop(columns=["No"], inplace=True, errors='ignore')
                df_raw.drop(0, inplace=True)
                baris_yang_diambil = [39, 40, 41, 42, 43, 44]
                df_ringkasan = df_raw.loc[baris_yang_diambil].reset_index(drop=True)
                st.success("✅ Data berhasil diambil dan ditampilkan.")
                st.dataframe(df_ringkasan, use_container_width=True)
            else:
                st.warning("⚠️ Respon tidak memiliki konten.")

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Gagal mengambil data dari API: {e}")
        except Exception as e:
            st.error(f"❌ Gagal membaca file Excel: {e}")
