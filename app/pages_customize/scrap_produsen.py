import streamlit as st
import datetime
import os
import shutil
import pandas as pd
from utility.downloader import download_data, create_zip_of_downloads

def show():
    st.title("📦 Scraper Data Harga Produsen Bapanas")
    mode = st.radio("Pilih Mode:", ["Harian", "Periode"])

    if mode == "Harian":
        tanggal = st.date_input("Pilih tanggal", value=datetime.date.today())
        if st.button("Unduh Data Harian"):
            with st.spinner("Sedang mengunduh..."):
                status, path = download_data(tanggal, level_harga_id=1)
                if status:
                    st.success(f"✅ Berhasil: {os.path.basename(path)}")
                    df = pd.read_excel(path)
                    st.dataframe(df)
                    st.download_button("📥 Unduh File", data=open(path, "rb"), file_name=os.path.basename(path))
                else:
                    st.error("❌ Gagal mengunduh data.")

    elif mode == "Periode":
        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input("Tanggal mulai", value=datetime.date.today())
        with col2:
            end = st.date_input("Tanggal akhir", value=datetime.date.today())

        if start > end:
            st.warning("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
        elif st.button("Unduh Data Periode"):
            if os.path.exists("dataset_scrap"):
                shutil.rmtree("dataset_scrap")

            total = (end - start).days + 1
            progress_bar = st.progress(0)
            status_text = st.empty()
            for i in range(total):
                tanggal = start + datetime.timedelta(days=i)
                status_text.markdown(f"⏳ Mengunduh: {tanggal.strftime('%d-%m-%Y')}")
                download_data(tanggal, level_harga_id=1)
                progress_bar.progress((i + 1) / total)

            st.success("✅ Selesai mengunduh semua data.")
            zip_bytes = create_zip_of_downloads("dataset_scrap", "dataset_scrap.zip")
            st.download_button("📦 Unduh Semua Data (ZIP)", data=zip_bytes, file_name="dataset_scrap.zip")