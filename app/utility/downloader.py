import os, calendar, requests
import pandas as pd
from io import BytesIO
import zipfile

bulan_mapping = {
    "January": "Januari", "February": "Februari", "March": "Maret",
    "April": "April", "May": "Mei", "June": "Juni",
    "July": "Juli", "August": "Agustus", "September": "September",
    "October": "Oktober", "November": "November", "December": "Desember"
}

def download_data(tanggal, level_harga_id):
    formatted = tanggal.strftime("%d/%m/%Y")
    period_param = f"{formatted}%20-%20{formatted}"
    nama_bulan = bulan_mapping[calendar.month_name[tanggal.month]]
    file_name = f"harga_konsumen_bapanas_{tanggal.strftime('%d-%m-%Y')}.xlsx"
    folder_path = os.path.join("dataset_scrap", nama_bulan)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)

    url = f"https://api-panelhargav2.badanpangan.go.id/harga-pangan-table-province/export?province_id=15&period_date={period_param}&level_harga_id={level_harga_id}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        return True, file_path
    return False, None

def preview_xlsx(file_path):
    try:
        return pd.read_excel(file_path)
    except:
        return pd.DataFrame()

def create_zip_of_downloads(folder_path):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname)
    zip_buffer.seek(0)
    return zip_buffer
