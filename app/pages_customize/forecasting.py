import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt
from statsmodels.tsa.arima.model import ARIMA

def show():
    st.title("💡 Halaman Forecasting")
    st.subheader("📈 Forecast Harga Beras Medium dengan Berbagai Model")

    # --- Load Data ---
    df_beras = pd.read_csv("../dataset_forecast/harga_beras_medium.csv")
    df_beras.rename(columns={'ds': 'Tanggal', 'y': 'Harga'}, inplace=True)
    df_beras['Tanggal'] = pd.to_datetime(df_beras['Tanggal'])
    df_beras.set_index('Tanggal', inplace=True)

    # --- Model Forecast ---
    # Exponential Smoothing
    model_expo = ExponentialSmoothing(df_beras['Harga'], trend='add', seasonal='add', seasonal_periods=4).fit()
    forecast_expo = model_expo.forecast(steps=6)

    # Holt
    model_holt = Holt(df_beras['Harga']).fit()
    forecast_holt = model_holt.forecast(steps=6)

    # ARIMA
    model_arima = ARIMA(df_beras['Harga'], order=(2, 1, 2)).fit()
    forecast_arima = model_arima.forecast(steps=6)

    # Future Dates
    future_dates = pd.date_range(start=df_beras.index[-1] + pd.offsets.MonthEnd(), periods=6, freq='M')

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.plot(df_beras.index, df_beras['Harga'], label='Data Historis', color='black', marker='o')

    # Forecast
    ax.plot(future_dates, forecast_expo, label='Forecast - Exponential Smoothing', color='purple', marker='o')
    ax.plot(future_dates, forecast_holt, label='Forecast - Holt-Winters', color='green', marker='o')
    ax.plot(future_dates, forecast_arima, label='Forecast - ARIMA', color='red', marker='o')

    # Angka Data Historis
    for i, value in enumerate(df_beras['Harga']):
        ax.text(df_beras.index[i], value + 0.5, f"{value/1000:.1f}K", ha="right", va='center', fontsize=9, rotation=45)

    # Angka Forecast
    for i, value in enumerate(forecast_expo):
        ax.text(future_dates[i], value + 3, f"{value/1000:.1f}K", ha='center', va='bottom', fontsize=9, color='purple')
    for i, value in enumerate(forecast_holt):
        ax.text(future_dates[i], value - 5, f"{value/1000:.1f}K", ha='center', va='top', fontsize=9, color='green')
    for i, value in enumerate(forecast_arima):
        ax.text(future_dates[i], value + 7, f"{value/1000:.1f}K", ha='center', va='bottom', fontsize=9, color='red', weight='bold')

    # Finalisasi
    ax.set_title("Forecast Harga Beras Medium Menggunakan Exponential Smoothing, Holt-Winters, dan ARIMA", fontsize=16)
    ax.set_xlabel("Tanggal", fontsize=12)
    ax.set_ylabel("Harga", fontsize=12)
    ax.grid(True)
    ax.legend(fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Tampilkan di Streamlit
    st.pyplot(fig)

    # Tambahkan tabel hasil forecast
    forecast_df = pd.DataFrame({
        "Tanggal": future_dates,
        "Exponential Smoothing": forecast_expo.values,
        "Holt-Winters": forecast_holt.values,
        "ARIMA": forecast_arima.values
    })
    st.subheader("📊 Hasil Forecast (6 Bulan ke Depan)")
    st.dataframe(forecast_df.set_index("Tanggal"))
