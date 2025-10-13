import streamlit as st
import altair as alt
import datetime
import requests
import pandas as pd
from io import BytesIO

def fetch_data(start, end):
    """Ambil data dari API untuk rentang tanggal tertentu"""
    url = "https://api-panelhargav2.badanpangan.go.id/harga-pangan-table-province/export"
    indices = [39, 41, 43]  # Rerata, Tertinggi, Terendah
    params_base = {"province_id": 15, "level_harga_id": 3}

    days = (end - start).days + 1
    all_rows = []

    progress = st.progress(0)
    status_text = st.empty()

    for i in range(days):
        d = start + datetime.timedelta(days=i)
        d_str = d.strftime("%d/%m/%Y")
        period_date = f"{d_str} - {d_str}"
        params = {**params_base, "period_date": period_date}

        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
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
    st.title("📊 Monitoring Pemantauan Harga Pangan")

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
        else:
            st.warning("Tidak ada data pada rentang tanggal tersebut.")

    # Selalu cek session_state, bukan tombol
    if "result" in st.session_state:
        result = st.session_state["result"]

        st.success("✅ Data berhasil diambil")
        # st.dataframe(result, use_container_width=True)

        # Dropdown tetap aktif meskipun tombol tidak ditekan lagi
        exclude = {"Tanggal", "Kota/Kabupaten"}
        commodity_options = [
            c for c in result.columns
            if c not in exclude and result[c].notna().any()
        ]

        if commodity_options:
            commodity = st.selectbox("Pilih komoditas:", commodity_options, index=0)

            # Siapkan data untuk chart
            chart_data = pd.concat(
                [
                    result[result["Kota/Kabupaten"]=="Rerata"][["Tanggal", commodity]].assign(Kategori="Rerata"),
                    result[result["Kota/Kabupaten"]=="Tertinggi"][["Tanggal", commodity]].assign(Kategori="Tertinggi"),
                    result[result["Kota/Kabupaten"]=="Terendah"][["Tanggal", commodity]].assign(Kategori="Terendah"),
                ],
                ignore_index=True
            )

            # Ambil daftar tanggal unik untuk tick sumbu X
            unique_dates = chart_data["Tanggal"].dt.strftime("%Y-%m-%d").unique().tolist()

            # Buat chart Altair
            line_chart = (
                alt.Chart(chart_data)
                .mark_line(point=True)
                .encode(
                    x=alt.X(
                        "Tanggal:T",
                        axis=alt.Axis(
                            values=pd.to_datetime(unique_dates),
                            format="%Y-%m-%d",
                            title="Tanggal",
                            labelAngle=-45  # miringkan label agar rapi
                        )
                    ),
                    y=alt.Y(f"{commodity}:Q", scale=alt.Scale(zero=False), title=commodity),
                    color=alt.Color(
                        "Kategori:N",
                        scale=alt.Scale(
                            domain=["Rerata", "Tertinggi", "Terendah"],
                            range=["#00AA00", "#FFD000", "#CC0000"]
                        ),
                        legend=alt.Legend(title="Kategori")
                    ),
                    tooltip=["Tanggal:T", "Kategori:N", alt.Tooltip(f"{commodity}:Q", format=",.0f")]
                )
                .properties(width=800, height=500, title=f"Pergerakan {commodity}")
            )

            st.altair_chart(line_chart, use_container_width=True)
        else:
            st.warning("Tidak ada kolom komoditas numerik yang bisa divisualisasikan.")
