import requests
import datetime
import os
import calendar
import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
import shutil

# ===================== KONFIGURASI LOGIN =====================
USERNAME = "admin"
PASSWORD = "admin123"

# ===================== SESSION STATE LOGIN =====================
if "login_status" not in st.session_state:
    st.session_state.login_status = False
if "page" not in st.session_state:
    st.session_state.page = "Login"

# ===================== SIDEBAR =====================
st.sidebar.title("📊 Menu Navigasi")
if st.session_state.login_status:
    st.sidebar.success(f"👋 Selamat datang, {USERNAME}")
    st.session_state.page = st.sidebar.radio("Pilih Halaman", ["Scrap", "Insight", "Forecasting"])
    
    if st.sidebar.button("🔓 Logout"):
        st.session_state.login_status = False
        st.session_state.page = "Login"
        st.rerun()
else:
    st.session_state.page = "Login"
    st.sidebar.warning("🔒 Login terlebih dahulu")

# ===================== FUNGSI SCRAPING =====================
bulan_mapping = {
    "January": "Januari", "February": "Februari", "March": "Maret",
    "April": "April", "May": "Mei", "June": "Juni",
    "July": "Juli", "August": "Agustus", "September": "September",
    "October": "Oktober", "November": "November", "December": "Desember"
}

def download_data(tanggal):
    formatted = tanggal.strftime("%d/%m/%Y")
    period_param = f"{formatted}%20-%20{formatted}"
    nama_bulan = bulan_mapping[calendar.month_name[tanggal.month]]
    file_name = f"harga_konsumen_bapanas_{tanggal.strftime('%d-%m-%Y')}.xlsx"
    folder_path = os.path.join("dataset_scrap", nama_bulan)
    file_path = os.path.join(folder_path, file_name)
    os.makedirs(folder_path, exist_ok=True)

    url = f"https://api-panelhargav2.badanpangan.go.id/harga-pangan-table-province/export?province_id=15&period_date={period_param}&level_harga_id=1"
    response = requests.get(url)

    if response.status_code == 200 and response.content:
        with open(file_path, "wb") as f:
            f.write(response.content)
        return True, file_path
    return False, None

def preview_xlsx(file_path):
    try:
        return pd.read_excel(file_path)
    except Exception:
        return pd.DataFrame()

def create_zip_of_downloads(folder_path, zip_name):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname)
    zip_buffer.seek(0)
    return zip_buffer

# ===================== HALAMAN LOGIN =====================
if st.session_state.page == "Login":
    st.title("🔐 Login Aplikasi")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state.login_status = True
            st.success("✅ Login berhasil")
        else:
            st.error("❌ Username atau password salah")

# ===================== HALAMAN SCRAP =====================
elif st.session_state.page == "Scrap":
    st.title("📦 Scraper Data Harga Konsumen Bapanas")
    mode = st.radio("Pilih Mode:", ["Harian", "Periode"])

    if mode == "Harian":
        tanggal = st.date_input("Pilih tanggal", value=datetime.date.today())
        if st.button("Unduh Data Harian"):
            with st.spinner("Sedang mengunduh..."):
                status, path = download_data(tanggal)
                if status:
                    st.success(f"✅ Berhasil: {os.path.basename(path)}")
                    df = preview_xlsx(path)
                    st.subheader("📊 Preview Data:")
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
            # Kosongkan folder lama
            if os.path.exists("dataset_scrap"):
                shutil.rmtree("dataset_scrap")

            total = (end - start).days + 1
            progress_bar = st.progress(0)
            status_text = st.empty()

            st.session_state.downloaded_files = {}

            for i in range(total):
                tanggal = start + datetime.timedelta(days=i)
                nama_file = f"harga_konsumen_bapanas_{tanggal.strftime('%d-%m-%Y')}.xlsx"
                status_text.markdown(f"⏳ Mengunduh: `{nama_file}` ({i+1}/{total})")

                success, path = download_data(tanggal)
                if success:
                    tanggal_key = tanggal.strftime('%d-%m-%Y')
                    st.session_state.downloaded_files[tanggal_key] = path
                progress_bar.progress((i + 1) / total)

            st.success("✅ Selesai mengunduh semua data.")
            status_text.markdown("🎉 Semua file berhasil diunduh.")

            # Tampilkan tombol unduh ZIP
            if os.path.exists("dataset_scrap"):
                zip_bytes = create_zip_of_downloads("dataset_scrap", "dataset_scrap.zip")
                st.download_button(
                    "📦 Unduh Semua Data (ZIP)",
                    data=zip_bytes,
                    file_name="dataset_scrap.zip",
                    mime="application/zip"
                )

# ===================== HALAMAN INSIGHT =====================
elif st.session_state.page == "Insight":
    st.title("💡 Halaman Insight")
    st.info("🦿 Fitur forecasting akan dikembangkan di tahap berikutnya.")

# ===================== HALAMAN FORECASTING =====================
elif st.session_state.page == "Forecasting":
    st.title("📈 Halaman Forecasting")
    st.info("🔧 Fitur forecasting akan dikembangkan di tahap berikutnya.")
