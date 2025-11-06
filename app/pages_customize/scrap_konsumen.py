# pages/scrap_konsumen.py
import streamlit as st
import datetime
import os
import shutil
import pandas as pd
from io import BytesIO
from utility.downloader import download_data, preview_xlsx

def show():
    st.title("📦 Scraper Data Harga Konsumen Bapanas Provinsi Jawa Timur")
    mode = st.radio("Pilih Mode:", ["Harian", "Periode"])

    if mode == "Harian":
        tanggal = st.date_input("Pilih tanggal", value=datetime.date.today())
        if st.button("Unduh Data Harian"):
            with st.spinner("Sedang mengunduh..."):
                status, path = download_data(tanggal, level_harga_id=3)
                if status:
                    st.success(f"✅ Berhasil: {os.path.basename(path)}")
                    df = preview_xlsx(path)
                    if not df.empty:
                        st.subheader("📊 Preview Data:")
                        st.dataframe(df)
                        st.download_button("📥 Unduh File", data=open(path, "rb"), file_name=os.path.basename(path))
                    else:
                        st.warning("⚠️ File berhasil diunduh tetapi kosong.")
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
            total = (end - start).days + 1
            progress_bar = st.progress(0)
            status_text = st.empty()

            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                for i in range(total):
                    tanggal = start + datetime.timedelta(days=i)
                    status_text.markdown(f"⏳ Mengunduh: `{tanggal.strftime('%d-%m-%Y')}` ({i+1}/{total})")
                    success, path = download_data(tanggal, level_harga_id=3)
                    if success:
                        df = preview_xlsx(path)
                        if not df.empty:
                            sheet_name = tanggal.strftime("%d-%m-%Y")
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                    progress_bar.progress((i + 1) / total)

            output.seek(0)
            st.success("✅ Selesai mengunduh semua data.")
            st.download_button(
                "📥 Unduh Semua Data (Excel)",
                data=output,
                file_name="dataset_periode_konsumen.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )