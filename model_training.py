import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

# ===========================
# Membaca Data
# ===========================
df = pd.read_csv("../data/sensor_preprocessed.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.set_index("timestamp")

# ===========================
# Data per jam
# ===========================
df = df.resample("1h").mean().dropna()

print("Jumlah data per jam :", len(df))


# ==============================================
# Fungsi Forecast
# ==============================================

def forecasting(data, nama):

    print("\n==========================")
    print("Forecast", nama)
    print("==========================")

    split = int(len(data)*0.8)

    train = data[:split]
    test = data[split:]

    print("Training :", len(train))
    print("Testing  :", len(test))

    model = ARIMA(train,order=(2,1,2))
    model_fit = model.fit()

    prediksi = model_fit.forecast(steps=len(test))

    mae = mean_absolute_error(test,prediksi)
    rmse = np.sqrt(mean_squared_error(test,prediksi))
    mape = np.mean(np.abs((test-prediksi)/test))*100

    print("MAE :",round(mae,3))
    print("RMSE :",round(rmse,3))
    print("MAPE :",round(mape,2),"%")

    # Forecast 6 jam

    future = model_fit.forecast(steps=6)

    waktu = pd.date_range(
        start=df.index[-1]+pd.Timedelta(hours=1),
        periods=6,
        freq="1h"
    )

    hasil = pd.DataFrame({
        "Jam":waktu,
        nama:future.values
    })

    print("\nForecast 6 Jam")
    print(hasil)

    hasil.to_csv(f"../data/forecast_{nama.lower()}.csv",index=False)

    # Grafik

    plt.figure(figsize=(12,5))

    plt.plot(test.index,test.values,label="Aktual")
    plt.plot(test.index,prediksi.values,label="Prediksi")

    plt.title(f"Forecast {nama}")
    plt.xlabel("Waktu")
    plt.ylabel(nama)

    plt.legend()

    plt.show()


# ==============================================
# Forecast Suhu
# ==============================================

forecasting(df["suhu"],"Suhu")


# ==============================================
# Forecast Kelembaban
# ==============================================

forecasting(df["kelembaban"],"Kelembaban")