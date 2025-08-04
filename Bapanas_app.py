import requests
import datetime
import os
import calendar
import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
import shutil
import pydeck as pdk

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
    st.session_state.page = st.sidebar.radio("Pilih Halaman", ["Scrap Konsumen","Scrap Produsen","Insight","Forecasting","Monitoring Harga"])
    
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

def download_data(tanggal,level_harga_id):
    formatted = tanggal.strftime("%d/%m/%Y")
    period_param = f"{formatted}%20-%20{formatted}"
    nama_bulan = bulan_mapping[calendar.month_name[tanggal.month]]
    file_name = f"harga_konsumen_bapanas_{tanggal.strftime('%d-%m-%Y')}.xlsx"
    folder_path = os.path.join("dataset_scrap", nama_bulan)
    file_path = os.path.join(folder_path, file_name)
    os.makedirs(folder_path, exist_ok=True)

    url = f"https://api-panelhargav2.badanpangan.go.id/harga-pangan-table-province/export?province_id=15&period_date={period_param}&level_harga_id={level_harga_id}"
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

# ===================== HALAMAN SCRAP KONSUMEN =====================
elif st.session_state.page == "Scrap Konsumen":
    st.title("📦 Scraper Data Harga Konsumen Bapanas")
    mode = st.radio("Pilih Mode:", ["Harian", "Periode"])

    if mode == "Harian":
        tanggal = st.date_input("Pilih tanggal", value=datetime.date.today())
        if st.button("Unduh Data Harian"):
            with st.spinner("Sedang mengunduh..."):
                status, path = download_data(tanggal, level_harga_id=3)
                if status:
                    st.success(f"✅ Berhasil: {os.path.basename(path)}")
                    if os.path.exists(path):
                        try:
                            df = pd.read_excel(path)
                            if not df.empty:
                                st.subheader("📊 Preview Data:")
                                st.dataframe(df)
                                st.download_button(
                                    "📥 Unduh File",
                                    data=open(path, "rb"),
                                    file_name=os.path.basename(path),
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            else:
                                st.warning("⚠️ File berhasil diunduh tetapi kosong.")
                        except Exception as e:
                            st.error(f"❌ Gagal membaca file Excel: {e}")
                    else:
                        st.error("❌ File tidak ditemukan setelah diunduh.")
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

# ===================== HALAMAN SCRAP PRODUSEN =====================
elif st.session_state.page == "Scrap Produsen":
    st.title("📦 Scraper Data Harga Produsen Bapanas")
    mode = st.radio("Pilih Mode:", ["Harian", "Periode"])

    if mode == "Harian":
        tanggal = st.date_input("Pilih tanggal", value=datetime.date.today())
        if st.button("Unduh Data Harian"):
            with st.spinner("Sedang mengunduh..."):
                status, path = download_data(tanggal, level_harga_id=1)
                if status:
                    st.success(f"✅ Berhasil: {os.path.basename(path)}")
                    if os.path.exists(path):
                        try:
                            df = pd.read_excel(path)
                            if not df.empty:
                                st.subheader("📊 Preview Data:")
                                st.dataframe(df)
                                st.download_button(
                                    "📥 Unduh File",
                                    data=open(path, "rb"),
                                    file_name=os.path.basename(path),
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            else:
                                st.warning("⚠️ File berhasil diunduh tetapi kosong.")
                        except Exception as e:
                            st.error(f"❌ Gagal membaca file Excel: {e}")
                    else:
                        st.error("❌ File tidak ditemukan setelah diunduh.")
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
    st.subheader("🗺️ Visualisasi Lokasi dan Nilai (Pydeck Map)")

    # Contoh data lokasi & nilai — silakan ganti dengan data aslimu
    data = pd.DataFrame({
        "latitude": [-7.25, -7.27, -7.29, -7.23],
        "longitude": [112.75, 112.73, 112.72, 112.76],
        "lokasi": ["Pasar A", "Pasar B", "Pasar C", "Pasar D"],
        "nilai": [12000, 13500, 12500, 11000]
    })

    # Tampilkan dataframe mentah (opsional)
    st.dataframe(data)

    # Konversi nilai ke ukuran radius bulatan
    max_value = data["nilai"].max()
    min_value = data["nilai"].min()
    data["radius"] = data["nilai"].apply(lambda x: ((x - min_value) / (max_value - min_value + 1e-9)) * 1000 + 500)

    # Konfigurasi Pydeck Layer
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position='[longitude, latitude]',
        get_radius="radius",
        get_fill_color='[255, 0, 0, 140]',  # Merah transparan
        pickable=True
    )

    # Tampilan awal peta
    view_state = pdk.ViewState(
        latitude=data["latitude"].mean(),
        longitude=data["longitude"].mean(),
        zoom=11,
        pitch=0
    )

    # Render map
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "{lokasi}\nHarga: {nilai}"}
    ))

    st.info("🧠 Lingkaran yang lebih besar menunjukkan nilai harga yang lebih tinggi.")

# ===================== HALAMAN FORECASTING =====================
elif st.session_state.page == "Forecasting":
    st.title("📈 Halaman Forecasting")
    st.info("🔧 Fitur forecasting akan dikembangkan di tahap berikutnya.")

# ===================== HALAMAN MONITORING HARGA =====================
elif st.session_state.page == "Monitoring Harga":
    import time

    st.title("📉 Monitoring Harga Beras Real-time")
    st.caption("🔁 Grafik ini akan diperbarui secara otomatis setiap beberapa detik.")

    # Simulasi data real-time (ganti ini dengan data API live jika tersedia)
    if "monitor_data" not in st.session_state:
        st.session_state.monitor_data = pd.DataFrame(columns=["Waktu", "Harga"])

    chart_placeholder = st.empty()

    # Tombol untuk memulai monitoring
    if st.button("Mulai Monitoring"):
        for i in range(100):
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            harga_beras = 13000 + (i % 10)  # Gantilah dengan harga aktual dari API

            new_row = pd.DataFrame({"Waktu": [current_time], "Harga": [harga_beras]})
            st.session_state.monitor_data = pd.concat([st.session_state.monitor_data, new_row], ignore_index=True)

            chart_placeholder.line_chart(st.session_state.monitor_data.set_index("Waktu"))

            time.sleep(2)  # Delay 2 detik untuk simulasi real-time
