import streamlit as st
import pandas as pd
import requests
import datetime
from io import BytesIO

def show():
    st.title("💡 Halaman Insight")
    data_type = st.radio("Pilih Sumber Data", ["Konsumen", "Produsen"])
    level_harga_id = 3 if data_type == "Konsumen" else 1
    tanggal = st.date_input("📅 Pilih Tanggal", value=datetime.date.today())
    formatted = tanggal.strftime("%d/%m/%Y")
    period_param = f"{formatted} - {formatted}"
    url = f"https://api-panelhargav2.badanpangan.go.id/harga-pangan-table-province/export?province_id=15&period_date={period_param}&level_harga_id={level_harga_id}"

    # --- Ambil Data ---
    if st.button("🚀 Ambil Data"):
        with st.spinner("Mengambil data dari API..."):
            try:
                response = requests.get(url)
                response.raise_for_status()

                if not response.content:
                    st.warning("⚠️ Respon tidak memiliki konten.")
                else:
                    data_raw = pd.read_excel(BytesIO(response.content)).drop(columns=["No"], errors='ignore')
                    data_process = data_raw.copy()
                    data_process.iloc[39, 0] = "Rerata"
                    data_process.drop(index=0, inplace=True)
                    data_kabkot = data_process.copy()
                    data_kabkot.columns = data_kabkot.columns.astype(str).str.strip()

                    st.session_state.data_kabkot = data_kabkot
                    st.session_state.data_process = data_process

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Gagal mengambil data dari API: {e}")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")

    # --- Filter Interaktif ---
    if "data_kabkot" in st.session_state:
        data_kabkot = st.session_state.data_kabkot
        daftar_kabkot = sorted(data_kabkot["Kota/Kabupaten"].dropna().unique())[1:-3]
        daftar_komoditas = list(data_kabkot.columns[1:])

        st.subheader("🏙️ Data Filter Kab/Kota & Komoditas")
        filter_kabkot = st.multiselect("Pilih Kabupaten/Kota:", daftar_kabkot, [])
        filter_komoditas = st.multiselect("Pilih Komoditas:", daftar_komoditas, [])

        if filter_kabkot and filter_komoditas:
            kolom_terpilih = ["Kota/Kabupaten"] + filter_komoditas
            st.dataframe(
                data_kabkot[data_kabkot["Kota/Kabupaten"].isin(filter_kabkot)][kolom_terpilih].reset_index(drop=True),
                use_container_width=True
            )
        else:
            st.warning("Silakan pilih minimal satu kabupaten/kota dan satu komoditas.")

    if "data_process" in st.session_state:
        st.subheader("📊 Data Rekap Harian")
        data_rerata = st.session_state.data_process.copy()
        subset = data_rerata.loc[39:45].reset_index(drop=True)

        hasil = []
        for komod in filter_komoditas:
            try:
                rerata_val = subset.loc[0, komod] if 0 in subset.index else None
                het = subset.loc[1, komod] if 1 in subset.index else None
                tertinggi_val = subset.loc[2, komod] if 2 in subset.index else None
                kota_tertinggi = subset.loc[3, komod] if 3 in subset.index else None
                terendah_val = subset.loc[4, komod] if 4 in subset.index else None
                kota_terendah = subset.loc[5, komod] if 5 in subset.index else None
            except KeyError:
                rerata_val = het = tertinggi_val = kota_tertinggi = terendah_val = kota_terendah = None

            hasil.append({
                "Komoditas": komod,
                "HET/HAP": het,
                "Rerata": rerata_val,
                "Tertinggi": tertinggi_val,
                "Kota Tertinggi": kota_tertinggi,
                "Terendah": terendah_val,
                "Kota Terendah": kota_terendah
            })

        df_hasil = pd.DataFrame(hasil)
        st.dataframe(df_hasil, use_container_width=True)
