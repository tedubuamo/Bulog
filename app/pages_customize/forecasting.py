import streamlit as st
import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import MinMaxScaler

plt.style.use("seaborn-v0_8-whitegrid")


def show():
    st.title("💡 Halaman Forecasting")
    st.subheader("📈 Forecast Harga Komoditas dengan Beberapa Model Seasonal")

    uploaded_file = st.file_uploader(
        "📤 Upload file Excel/CSV dengan kolom ds,y. Gunakan rerata yang sudah dihitung pada masing-masing bulan setelah dilakukan scraping.",
        type=["xlsx", "xls", "csv"]
    )

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        if not {"ds", "y"}.issubset(df.columns):
            st.error("❌ File harus memiliki kolom 'ds' (tanggal) dan 'y' (harga).")
            return

        df["ds"] = pd.to_datetime(df["ds"])
        df = df.set_index("ds").sort_index()

        st.write("📄 Data yang diunggah:")
        st.dataframe(df)

        model_choice = st.selectbox(
            "Pilih Model Forecasting:",
            ["SARIMAX", "Holt-Winters", "ARIMA", "Seasonal Naïve"]
        )
        steps_ahead = st.number_input(
            "🔮 Jumlah bulan ke depan untuk forecast:",
            min_value=1, max_value=24, value=6
        )

        if model_choice == "SARIMAX":
            df["y_log"] = np.log(df["y"])
            scaler = MinMaxScaler()
            y_scaled = scaler.fit_transform(df[["y_log"]])

            p = d = q = range(0, 2)
            P = D = Q = range(0, 2)
            s = 12
            pdq = list(itertools.product(p, d, q))
            seasonal_pdq = list(itertools.product(P, D, Q, [s]))

            best_aic = np.inf
            best_order = None
            best_seasonal = None
            best_model = None

            with st.spinner("🔍 Mencari model SARIMA terbaik..."):
                for order in pdq:
                    for seasonal_order in seasonal_pdq:
                        try:
                            model = SARIMAX(
                                y_scaled,
                                order=order,
                                seasonal_order=seasonal_order,
                                enforce_stationarity=False,
                                enforce_invertibility=False
                            )
                            model_fit = model.fit(disp=False)
                            if model_fit.aic < best_aic:
                                best_aic = model_fit.aic
                                best_order = order
                                best_seasonal = seasonal_order
                                best_model = model_fit
                        except:
                            continue

            st.success(f"✅ Model terbaik: SARIMA{best_order}x{best_seasonal} | AIC: {best_aic:.2f}")

            forecast_object = best_model.get_forecast(steps=steps_ahead)
            forecast_scaled = forecast_object.predicted_mean
            forecast_log = scaler.inverse_transform(np.array(forecast_scaled).reshape(-1, 1)).flatten()
            forecast = np.exp(forecast_log)

            conf_int_scaled = forecast_object.conf_int(alpha=0.05)
            conf_int_log = scaler.inverse_transform(np.array(conf_int_scaled))
            conf_int = np.exp(conf_int_log)

        elif model_choice == "Holt-Winters":
            model = ExponentialSmoothing(df["y"], seasonal="add", seasonal_periods=12)
            model_fit = model.fit()
            forecast = model_fit.forecast(steps_ahead)
            conf_int = np.column_stack([forecast * 0.95, forecast * 1.05])

        elif model_choice == "ARIMA":
            model = ARIMA(df["y"], order=(2, 1, 2))
            model_fit = model.fit()
            forecast_object = model_fit.get_forecast(steps=steps_ahead)
            forecast = forecast_object.predicted_mean
            conf_int = forecast_object.conf_int(alpha=0.05).values

        elif model_choice == "Seasonal Naïve":
            last_season = df["y"].iloc[-12:]
            reps = int(np.ceil(steps_ahead / 12))
            forecast = np.tile(last_season.values, reps)[:steps_ahead]
            conf_int = np.column_stack([forecast * 0.95, forecast * 1.05])

        # ===============================
        # VISUALISASI HASIL FORECAST
        # ===============================
        last_date = df.index[-1]
        future_dates = pd.date_range(start=last_date + pd.offsets.MonthEnd(), periods=steps_ahead, freq="M")

        fig, ax = plt.subplots(figsize=(16, 7))
        ax.plot(df.index, df["y"], label="Data Historis", marker="o", color="#1f77b4", linewidth=2)
        for i, value in enumerate(df["y"]):
            ax.text(df.index[i], value, f"{value:.0f}", ha="center", va="bottom", color="blue", fontsize=8, rotation=45)

        ax.plot(future_dates, forecast, label=f"Forecast - {model_choice}", color="#d62728",
                marker="o", linewidth=2, linestyle="--")
        ax.fill_between(future_dates, conf_int[:, 0], conf_int[:, 1], color="#ff9999", alpha=0.3,
                        label="95% Confidence Interval")
        ax.axvline(x=last_date, color="gray", linestyle="--", alpha=0.7)

        for i, value in enumerate(forecast):
            ax.text(future_dates[i], value, f"{value:.0f}", ha="center", va="bottom",
                    color="red", fontsize=9, rotation=45, weight="bold")

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b-%Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.xticks(rotation=45)
        plt.title(f"Forecast Harga Komoditas - {model_choice}", fontsize=14, weight="bold")
        plt.xlabel("Tanggal", fontsize=12)
        plt.ylabel("Harga (Rupiah)", fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend(loc="upper left", fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)

        # ===============================
        # TABEL HASIL PREDIKSI
        # ===============================
        df_forecast = pd.DataFrame({
            "Tanggal": future_dates,
            "Forecast": forecast,
            "Lower CI": conf_int[:, 0],
            "Upper CI": conf_int[:, 1]
        })
        df_forecast["Forecast"] = df_forecast["Forecast"].round(2)
        df_forecast["Lower CI"] = df_forecast["Lower CI"].round(2)
        df_forecast["Upper CI"] = df_forecast["Upper CI"].round(2)

        st.subheader("📊 Hasil Prediksi")
        st.dataframe(df_forecast)