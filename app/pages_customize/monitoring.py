import streamlit as st
import altair as alt
import datetime
import requests
import pandas as pd
from io import BytesIO

def fetch_data(start, end):
    """Ambil data dari API untuk rentang tanggal tertentu"""
    url = "https://api-panelhargav2.badanpangan.go.id/harga-pangan-table-province/export"
    indices = [39, 40, 41, 43]  # Rerata, HET/HAP, Tertinggi, Terendah
    params_base = {"province_id": 15, "level_harga_id": 3}

    days = (end - start).days + 1
    all_rows = []

    progress = st.progress(0)
    status_text = st.empty()

    # siapkan dict untuk simpan data_process per tanggal
    st.session_state["data_process_dict"] = {}

    for i in range(days):
        d = start + datetime.timedelta(days=i)
        d_str = d.strftime("%d/%m/%Y")
        period_date = f"{d_str} - {d_str}"
        params = {**params_base, "period_date": period_date}

        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()

            # Simpan data_process per tanggal
            url_direct = f"https://api-panelhargav2.badanpangan.go.id/harga-pangan-table-province/export?province_id=15&period_date={period_date}&level_harga_id={params_base['level_harga_id']}"
            response = requests.get(url_direct)
            data_raw = pd.read_excel(BytesIO(response.content)).drop(columns=["No"], errors='ignore')
            data_process = data_raw.copy()
            data_process.iloc[39, 0] = "Rerata"
            data_process.drop(index=0, inplace=True)

            # simpan ke dict dengan key = tanggal
            st.session_state["data_process_dict"][d.strftime("%Y-%m-%d")] = data_process

            # Data ringkas untuk chart
            df = pd.read_excel(BytesIO(r.content))
            df_sel = df.iloc[indices].copy()
            df_sel.insert(0, "Tanggal", d.strftime("%Y-%m-%d"))
            all_rows.append(df_sel)

        except Exception as e:
            st.warning(f"Gagal mengambil data pada {d.strftime('%Y-%m-%d')}: {e}")

        progress.progress((i + 1) / days)
        status_text.text(f"Memproses {i+1} dari {days} hari...")

    progress.empty()
    status_text.empty()

    if all_rows:
        result = pd.concat(all_rows, ignore_index=True)

        # Bersihkan kolom meta
        if "No" in result.columns:
            result = result.drop(columns=["No"])
        if "Kota/Kabupaten" in result.columns:
            result["Kota/Kabupaten"] = result["Kota/Kabupaten"].replace("Grand Total", "Rerata")

        # Konversi semua kolom selain meta ke numerik
        for col in result.columns:
            if col not in ["Tanggal", "Kota/Kabupaten"]:
                result[col] = pd.to_numeric(result[col], errors="coerce")

        result["Tanggal"] = pd.to_datetime(result["Tanggal"])
        return result
    return None


def show():
    st.title("📊 Monitoring Pemantauan Harga Pangan Provinsi Jawa Timur")

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Tanggal mulai", value=datetime.date.today())
    with col2:
        end = st.date_input("Tanggal akhir", value=datetime.date.today())

    if start > end:
        st.warning("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
        return

    # Tombol ambil data
    if st.button("Lihat Data Periode"):
        result = fetch_data(start, end)
        if result is not None:
            st.session_state["result"] = result
            st.session_state["date_index"] = 0  # reset index saat ambil data baru
        else:
            st.warning("Tidak ada data pada rentang tanggal tersebut.")

    # --- Bagian tampilkan data & chart ---
    if "result" in st.session_state:
        result = st.session_state["result"]
        st.success("✅ Data berhasil diambil")

        # Ambil daftar tanggal sebagai datetime.date
        available_dates = sorted(result["Tanggal"].dt.date.unique().tolist())

        # Inisialisasi index tanggal aktif
        if "date_index" not in st.session_state:
            st.session_state.date_index = 0

        col_prev, col_date, col_next = st.columns([1,3,1])
        with col_prev:
            if st.button("⬅️"):
                if st.session_state.date_index > 0:
                    st.session_state.date_index -= 1
        with col_next:
            if st.button("➡️"):
                if st.session_state.date_index < len(available_dates)-1:
                    st.session_state.date_index += 1
        with col_date:
            st.markdown(
                f"### 📅 {available_dates[st.session_state.date_index].strftime('%Y-%m-%d')}"
            )

        selected_date = available_dates[st.session_state.date_index]
        selected_date_str = selected_date.strftime("%Y-%m-%d")

        # --- Rekap harian sesuai tanggal aktif ---
        if "data_process_dict" in st.session_state and selected_date_str in st.session_state["data_process_dict"]:
            data_rerata = st.session_state["data_process_dict"][selected_date_str].copy()

            # ambil hanya blok ringkasan (baris 39–45)
            subset = data_rerata.iloc[38:45].reset_index(drop=True)

            st.subheader(f"📊 Data Rekap Harian - {selected_date_str}")

            all_komoditas = [col for col in subset.columns if col not in ["Tanggal", "Kota/Kabupaten"]]

            hasil = []
            for komod in all_komoditas:
                try:
                    rerata_val      = subset.loc[0, komod] if 0 in subset.index else None
                    het             = subset.loc[1, komod] if 1 in subset.index else None
                    tertinggi_val   = subset.loc[2, komod] if 2 in subset.index else None
                    kota_tertinggi  = subset.loc[3, komod] if 3 in subset.index else None
                    terendah_val    = subset.loc[4, komod] if 4 in subset.index else None
                    kota_terendah   = subset.loc[5, komod] if 5 in subset.index else None
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



        # --- Bagian chart ---
        exclude = {"Tanggal", "Kota/Kabupaten"}
        commodity_options = [
            c for c in result.columns
            if c not in exclude and result[c].notna().any()
        ]

        # buat unique_dates dari result, bukan dari chart_data
        unique_dates = result["Tanggal"].dt.strftime("%Y-%m-%d").unique().tolist()

        if commodity_options:
            commodity = st.selectbox("Pilih komoditas:", commodity_options, index=0)

            chart_data = pd.concat(
                [
                    result[result["Kota/Kabupaten"]=="Rerata"][["Tanggal", commodity]].assign(Kategori="Rerata"),
                    result[result["Kota/Kabupaten"]=="HET/HAP"][["Tanggal", commodity]].assign(Kategori="HET/HAP"),
                    result[result["Kota/Kabupaten"]=="Tertinggi"][["Tanggal", commodity]].assign(Kategori="Tertinggi"),
                    result[result["Kota/Kabupaten"]=="Terendah"][["Tanggal", commodity]].assign(Kategori="Terendah"),
                ],
                ignore_index=True
            )

            line_chart = (
                alt.Chart(chart_data)
                .mark_line(point=True, strokeWidth=4)
                .encode(
                    x=alt.X("Tanggal:T",
                            axis=alt.Axis(values=pd.to_datetime(unique_dates),
                                        format="%Y-%m-%d",
                                        title="Tanggal",
                                        labelAngle=-45)),
                    y=alt.Y(f"{commodity}:Q", scale=alt.Scale(zero=False), title="Harga (Rupiah)"),
                    color=alt.Color("Kategori:N",
                                    scale=alt.Scale(domain=["Rerata","HET/HAP","Tertinggi","Terendah"],
                                                    range=["#00AA00","#234234","#FFD000","#CC0000"]),
                                    legend=alt.Legend(title="Kategori")),
                    tooltip=["Tanggal:T","Kategori:N",alt.Tooltip(f"{commodity}:Q", format=",.0f")]
                )
                .properties(width=1000, height=600, title=f"Pergerakan {commodity}", background='white')
                .configure_axis(labelFontSize=12, titleFontSize=14,
                                labelFont='Arial', titleFont='Arial',
                                labelColor='black', titleColor='black')
                .configure_legend(labelFontSize=12, titleFontSize=14,
                                labelFont='Arial', titleFont='Arial',
                                labelColor='black', titleColor='black')
                .configure_title(
                    fontSize=16,
                    font='Arial',
                    color='black'
                )
            )

            st.altair_chart(line_chart, use_container_width=True)
        else:
            st.warning("Tidak ada kolom komoditas numerik yang bisa divisualisasikan.")
