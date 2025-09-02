import streamlit as st
import pandas as pd
import folium
import json
import requests
import datetime
from streamlit_folium import folium_static
from io import BytesIO

import matplotlib.pyplot as plt

def show():
    st.title("💡 Halaman Insight")
    st.subheader("🗺️ Visualisasi Harga Pangan di Jawa Timur (Folium Map)")

    # --- PILIH SUMBER DATA ---
    data_type = st.radio("Pilih Sumber Data", ["Konsumen", "Produsen"])
    level_harga_id = 3 if data_type == "Konsumen" else 1

    # --- PILIH TANGGAL ---
    tanggal = st.date_input("📅 Pilih Tanggal", value=datetime.date.today())
    formatted = tanggal.strftime("%d/%m/%Y")
    period_param = f"{formatted} - {formatted}"

    # --- TAMPILKAN URL ---
    url = f"https://api-panelhargav2.badanpangan.go.id/harga-pangan-table-province/export?province_id=15&period_date={period_param}&level_harga_id={level_harga_id}"

    # --- TOMBOL AMBIL DATA ---
    if st.button("🚀 Ambil Data"):
        with st.spinner("Mengambil data dari API..."):
            try:
                response = requests.get(url)
                response.raise_for_status()

                if response.content:
                    # Baca langsung file Excel dari response ke DataFrame
                    df_raw = pd.read_excel(BytesIO(response.content))
                    df_raw.drop(columns=["No"], inplace=True, errors='ignore')
                    df_raw.drop(0, inplace=True)
                    baris_yang_diambil = [39, 40, 41, 42, 43, 44]
                    df_ringkasan = df_raw.loc[baris_yang_diambil].reset_index(drop=True)

                    header_kabkot = df_ringkasan.iloc[3, 1:].tolist()
                    header_kabkot = ["komoditas"] + header_kabkot
                    st.dataframe(header_kabkot, use_container_width=True)
                else:
                    st.warning("⚠️ Respon tidak memiliki konten.")

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Gagal mengambil data dari API: {e}")
            except Exception as e:
                st.error(f"❌ Gagal membaca file Excel: {e}")

    # Data harga per kabupaten
    data = pd.DataFrame({
        "kabkot": ["Surabaya", "Malang", "Kediri", "Jember", "Banyuwangi", "Madiun", "Blitar", "Lamongan"],
        "nilai": [14500, 15200, 13700, 12800, 16000, 14000, 12500, 15500]
    })

    st.dataframe(data)

    # Load GeoJSON
    with open("app/data_geo/jawa-timur.json", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    tile_dict = {
        "OpenStreetMap": {
            "tiles": "OpenStreetMap",
            "attr": None
        },
        "CartoDB positron": {
            "tiles": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
            "attr": "Tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
        },
        "CartoDB dark_matter": {
            "tiles": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            "attr": "Tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
        }
    }

    tile_options = list(tile_dict.keys())
    selected_tile = st.selectbox("Pilih Tipe Peta", tile_options)

    # Buat peta sesuai pilihan tile
    if tile_dict[selected_tile]["attr"]:
        m = folium.Map(
            location=[-7.7, 112.75],
            zoom_start=8,
            tiles=tile_dict[selected_tile]["tiles"],
            attr=tile_dict[selected_tile]["attr"]
        )
    else:
        m = folium.Map(
            location=[-7.7, 112.75],
            zoom_start=8,
            tiles=tile_dict[selected_tile]["tiles"]
        )

    # Gabungkan data nilai ke GeoJSON berdasarkan kabupaten
    for feature in geojson_data["features"]:
        kabkot_name = feature["properties"]["kabkot"]
        match = data[data["kabkot"].str.lower() == kabkot_name.lower()]
        if not match.empty:
            feature["properties"]["nilai"] = int(match["nilai"].values[0])
        else:
            feature["properties"]["nilai"] = None

    # Tentukan nilai min/max untuk colormap
    nilai_values = [f["properties"]["nilai"] for f in geojson_data["features"] if f["properties"]["nilai"] is not None]
    min_val = min(nilai_values)
    max_val = max(nilai_values)

    # Colormap
    from branca.colormap import linear
    colormap = linear.YlOrRd_09.scale(min_val, max_val)
    colormap.caption = "Harga Pangan per Kabupaten/Kota (Rp)"
    colormap.add_to(m)

    # Tampilkan wilayah dengan warna berdasarkan nilai
    folium.GeoJson(
        geojson_data,
        name="Wilayah Harga",
        style_function=lambda feature: {
            "fillColor": colormap(feature["properties"]["nilai"]) if feature["properties"]["nilai"] else "#cccccc",
            "color": "#AF913F",
            "weight": 1,
            "fillOpacity": 0.8,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["kabkot", "nilai"],
            aliases=["Kabupaten/Kota:", "Harga:"],
            localize=True
        ),
    ).add_to(m)

    # Tampilkan kontrol layer
    folium.LayerControl().add_to(m)

    folium_static(m)

    st.caption("📊 Warna menunjukkan harga pangan (dari rendah ke tinggi) | Abu-abu: tidak ada panen/tidak ada transaksi")

    

    # --- Dummy Data: Komoditas per Kota per Tahun ---
    data = {
        "komoditas": ["Beras Premium", "Beras Premium", "Beras Premium", 
                    "Cabai Merah", "Cabai Merah", "Cabai Merah",
                    "Telur Ayam", "Telur Ayam", "Telur Ayam"],
        "kabkot": ["Surabaya"] * 9,
        "tahun": [2022, 2023, 2024, 2022, 2023, 2024, 2022, 2023, 2024],
        "nilai": [14500, 15000, 15500, 32000, 31000, 33000, 27000, 26800, 26500]
    }

    # Data tambahan untuk kota lain
    additional_data = pd.DataFrame({
        "komoditas": ["Beras Premium", "Cabai Merah", "Telur Ayam"] * 3,
        "kabkot": ["Malang"] * 9,
        "tahun": [2022, 2022, 2022, 2023, 2023, 2023, 2024, 2024, 2024],
        "nilai": [14000, 31000, 26000, 14500, 30500, 25500, 15000, 31500, 25800]
    })

    # Gabungkan semua data
    df = pd.concat([pd.DataFrame(data), additional_data], ignore_index=True)

    # --- FILTERS ---
    available_kabkot = sorted(df["kabkot"].unique().tolist())
    available_komoditas = sorted(df["komoditas"].unique().tolist())
    available_tahun = sorted(df["tahun"].unique().tolist())

    selected_kabkot = st.multiselect("📍 Pilih Kabupaten/Kota", available_kabkot, default=available_kabkot)
    selected_komoditas = st.multiselect("🌾 Pilih Komoditas", available_komoditas, default=available_komoditas)
    selected_tahun = st.multiselect("📅 Pilih Tahun", available_tahun, default=available_tahun)

    # --- Filter dataframe berdasarkan pilihan ---
    df_filtered = df[
        (df["kabkot"].isin(selected_kabkot)) &
        (df["komoditas"].isin(selected_komoditas)) &
        (df["tahun"].isin(selected_tahun))
    ].copy()

    df_filtered["tahun"] = df_filtered["tahun"].astype(int)

    # --- Visualisasi Line Chart ---
    fig, ax = plt.subplots(figsize=(12, 6))

    for komod in df_filtered["komoditas"].unique():
        for kab in df_filtered["kabkot"].unique():
            subset = df_filtered[(df_filtered["komoditas"] == komod) & (df_filtered["kabkot"] == kab)]
            if not subset.empty:
                ax.plot(
                    subset["tahun"], 
                    subset["nilai"], 
                    marker='o', 
                    label=f"{komod} - {kab}"
                )

    # Set axis labels dan judul
    ax.set_title("📊 Harga Komoditas per Tahun")
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Harga (Rp)")

    # ✅ Gunakan xticks hanya untuk tahun yang dipilih
    tahun_list = sorted(df_filtered["tahun"].unique())
    ax.set_xticks(tahun_list)

    # Tambahan styling
    ax.legend(title="Komoditas - Kabupaten/Kota")
    ax.grid(True)
    plt.tight_layout()

    # Tampilkan di Streamlit
    st.pyplot(fig)