import streamlit as st
import pandas as pd
import requests
import datetime
import altair as alt
from io import BytesIO
import calendar

# --- Fungsi ambil data ---
def fetch_data(month, year, level_harga_id):
    all_rows = []
    days_in_month = calendar.monthrange(year, month)[1]

    for day in range(1, days_in_month + 1):
        formatted_date = f"{day:02d}/{month:02d}/{year}"
        period_param = f"{formatted_date} - {formatted_date}"

        url = "https://api-panelhargav2.badanpangan.go.id/harga-pangan-table-province/export"
        params = {"province_id": 15, "period_date": period_param, "level_harga_id": level_harga_id}

        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            df = pd.read_excel(BytesIO(r.content)).drop(columns=["No"], errors="ignore")
            df["Tanggal"] = pd.to_datetime(formatted_date, dayfirst=True)
            all_rows.append(df)
        except Exception as e:
            st.warning(f"Gagal ambil data {formatted_date}: {e}")

    if all_rows:
        result = pd.concat(all_rows, ignore_index=True)
        result = result.dropna(subset=["Kota/Kabupaten"])
        exclude_labels = ["Grand Total", "HET/HAP", "Tertinggi", "Terendah"]
        result = result[~result["Kota/Kabupaten"].isin(exclude_labels)]
        result["Kota/Kabupaten"] = result["Kota/Kabupaten"].astype(str)
        for col in result.columns:
            if col not in ["Tanggal", "Kota/Kabupaten"]:
                result[col] = pd.to_numeric(result[col], errors="coerce")
        return result
    return None

# --- Halaman Insight ---
def show():
    st.title("💡 Halaman Insight Komoditas Jawa Timur")

    data_type = st.radio("Pilih Sumber Data", ["Konsumen", "Produsen"])
    level_harga_id = 3 if data_type == "Konsumen" else 1

    year = st.selectbox("Pilih Tahun", range(2020, 2026), index=5)
    month = st.selectbox("Pilih Bulan", range(1, 13), index=datetime.datetime.now().month - 1)

    if st.button("🚀 Ambil Data"):
        with st.spinner("Mengambil data dari API..."):
            data = fetch_data(month, year, level_harga_id)
            if data is not None:
                st.session_state["data"] = data
            else:
                st.warning("Data tidak tersedia untuk bulan dan tahun tersebut.")

    if "data" in st.session_state:
        data = st.session_state["data"]
        st.success("✅ Data berhasil diambil")

        # --- Filter komoditas ---
        filter_komoditas = [col for col in data.columns if col not in ["Tanggal", "Kota/Kabupaten"]]
        komoditas_options = ["Pilih Semua"] + filter_komoditas
        selected_komoditas = st.multiselect("Pilih Komoditas", komoditas_options, default=["Pilih Semua"])
        if "Pilih Semua" in selected_komoditas or not selected_komoditas:
            selected_komoditas = filter_komoditas

        # --- Filter kota ---
        exclude_labels = ["nan", "Grand Total", "HET/HAP", "Tertinggi", "Terendah"]
        kota_options_clean = sorted([k for k in data["Kota/Kabupaten"].unique().tolist() if k not in exclude_labels])
        kota_options = ["Pilih Semua"] + kota_options_clean
        selected_kota = st.multiselect("Pilih Kota/Kabupaten", kota_options, default=["Pilih Semua"])
        if "Pilih Semua" in selected_kota or not selected_kota:
            selected_kota = kota_options_clean

        # Filter data
        filtered_data = data[data["Kota/Kabupaten"].isin(selected_kota)]
        filtered_data = filtered_data[selected_komoditas + ["Tanggal", "Kota/Kabupaten"]]

        # st.subheader("📊 Data Rekap Bulanan")
        # st.dataframe(filtered_data, use_container_width=True)

        st.subheader("📈 Grafik Pergerakan Harga Komoditas")

        chart_data = pd.melt(
            filtered_data,
            id_vars=["Tanggal", "Kota/Kabupaten"],
            value_vars=selected_komoditas,
            var_name="Komoditas",
            value_name="Harga"
        )
        chart_data["Harga"] = pd.to_numeric(chart_data["Harga"], errors="coerce")
        chart_data = chart_data.dropna(subset=["Harga"])

        mode = st.radio("Mode Grafik", ["Rata-rata per Komoditas", "Per Komoditas & Kota"])

        if mode == "Rata-rata per Komoditas":
            chart_avg = chart_data.groupby(["Tanggal", "Komoditas"], as_index=False).agg({"Harga": "mean"})
            line_chart = (
                alt.Chart(chart_avg)
                .mark_line(point=True, interpolate="monotone", strokeWidth=2)
                .encode(
                    x=alt.X("Tanggal:T", title="Tanggal",
                            axis=alt.Axis(format="%d-%b", labelAngle=-45,
                                          labelColor="black", titleColor="black")),
                    y=alt.Y("Harga:Q", title="Harga (Rupiah)",
                            scale=alt.Scale(zero=False),
                            axis=alt.Axis(labelColor="black", titleColor="black")),
                    color=alt.Color("Komoditas:N",
                                    legend=alt.Legend(title="Komoditas",
                                                      labelColor="black", titleColor="black")),
                    tooltip=["Tanggal:T", "Komoditas:N", alt.Tooltip("Harga:Q", format=",.0f")]
                )
                .properties(width=700, height=500,
                            title=alt.TitleParams("Pergerakan Harga Komoditas (Rata-rata)", color="black"),
                            background="white")
                .configure_axis(labelFontSize=12, titleFontSize=14,
                                labelColor="black", titleColor="black")
                .configure_legend(labelFontSize=12, titleFontSize=14,
                                  labelColor="black", titleColor="black")
                .configure_title(fontSize=16, font="Arial", color="black")
            )
            st.altair_chart(line_chart, use_container_width=False)

        else:  # Per Komoditas & Kota
            base = (
                alt.Chart(chart_data)
                .mark_line(point=True, interpolate="monotone", strokeWidth=1.5)
                .encode(
                    x=alt.X("Tanggal:T", title="Tanggal",
                            axis=alt.Axis(format="%d-%b", labelAngle=-45,
                                        labelColor="black", titleColor="black")),
                    y=alt.Y("Harga:Q", title="Harga (Rupiah)",
                            scale=alt.Scale(zero=False),
                            axis=alt.Axis(labelColor="black", titleColor="black")),
                    color=alt.Color("Kota/Kabupaten:N",
                                    legend=alt.Legend(title="Kota/Kabupaten",
                                                    labelColor="black", titleColor="black")),
                    tooltip=["Tanggal:T", "Komoditas:N", "Kota/Kabupaten:N",
                            alt.Tooltip("Harga:Q", format=",.0f")]
                )
                .properties(width=400, height=250)  # tiap panel lebar penuh, tinggi proporsional
            )

            line_chart = base.facet(
                row=alt.Row("Komoditas:N",
                            title="Komoditas",
                            header=alt.Header(labelColor="black", titleColor="black"))
            ).properties(background="white")

            # tampilkan chart kotak, tiap komoditas ke bawah
            st.altair_chart(line_chart, use_container_width=True)

        st.subheader("📊 Perubahan Harga per Kota (Awal vs Akhir Bulan)")

        start_date = chart_data["Tanggal"].min()
        end_date = chart_data["Tanggal"].max()

        start_data = chart_data[chart_data["Tanggal"] == start_date]
        end_data = chart_data[chart_data["Tanggal"] == end_date]

        merged = pd.merge(
            start_data,
            end_data,
            on=["Komoditas", "Kota/Kabupaten"],
            suffixes=("_awal", "_akhir")
        )

        merged["Perubahan_%"] = ((merged["Harga_akhir"] - merged["Harga_awal"]) / merged["Harga_awal"]) * 100

        # --- Tampilkan sebagai card 3 kolom ---
        n_cols = 3
        for i in range(0, len(merged), n_cols):
            cols = st.columns(n_cols, gap="large")  # beri jarak antar kolom
            for j, col in enumerate(cols):
                if i + j < len(merged):
                    row = merged.iloc[i + j]
                    komoditas = row["Komoditas"]
                    kota = row["Kota/Kabupaten"]
                    harga_akhir = row["Harga_akhir"]
                    perubahan = row["Perubahan_%"]

                    delta_str = f"{perubahan:+.1f}%"

                    # Tentukan warna & panah
                    if round(perubahan, 1) == 0.0:
                        color = "yellow"
                        arrow = "🟰"
                    elif perubahan > 0:
                        color = "green"
                        arrow = "▲"
                    else:
                        color = "red"
                        arrow = "▼"

                    # Card custom pakai markdown HTML
                    col.markdown(
                        f"""
                        <div style="background-color:orange; border-radius:10px; padding:10px; 
                                    box-shadow:0 2px 6px rgba(0,0,0,0.15); text-align:center;
                                    margin-bottom:24px; margin-top:12px;">
                            <h4 style="margin:0; color:white; font-weight:bold;">{komoditas}</h4>
                            <p style="margin:0; color:black; font-size:14px; font-weight:bold;">{kota}</p>
                            <h3 style="margin:8px 0; color:black;">Rp {harga_akhir:,.0f}</h3>
                            <p style="margin:0; font-weight:bold; color:{color}; font-size:16px;">
                                {arrow} {delta_str}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
