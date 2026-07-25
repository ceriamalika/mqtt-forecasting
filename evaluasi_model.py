import pandas as pd
import numpy as np
import warnings

from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings("ignore")

# ============================================================
# EVALUASI MODEL FORECASTING ARIMA
# ============================================================

file_path = "sensor_data_forecasting.xlsx"

df = pd.read_excel(file_path)

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp")

# ============================================================
# DATA
# ============================================================

suhu = df["suhu"].dropna().reset_index(drop=True)

kelembaban = df["kelembaban"].dropna().reset_index(drop=True)

# ============================================================
# FUNGSI EVALUASI
# ============================================================

def evaluasi_model(data, nama_variabel, order):

    print("\n" + "=" * 70)
    print("EVALUASI MODEL:", nama_variabel.upper())
    print("=" * 70)

    # --------------------------------------------------------
    # PEMBAGIAN DATA TRAINING DAN TESTING
    # --------------------------------------------------------

    jumlah_data = len(data)

    jumlah_training = int(jumlah_data * 0.8)

    train = data.iloc[
        :jumlah_training
    ]

    test = data.iloc[
        jumlah_training:
    ]

    print("\nJumlah data keseluruhan :", jumlah_data)
    print("Jumlah data training    :", len(train))
    print("Jumlah data testing     :", len(test))

    print("\nModel ARIMA:", order)

    # --------------------------------------------------------
    # PEMBENTUKAN MODEL
    # --------------------------------------------------------

    model = ARIMA(
        train,
        order=order
    )

    model_fit = model.fit()

    # --------------------------------------------------------
    # FORECAST DATA TESTING
    # --------------------------------------------------------

    forecast = model_fit.forecast(
        steps=len(test)
    )

    forecast = pd.Series(
        forecast
    ).reset_index(drop=True)

    aktual = test.reset_index(
        drop=True
    )

    # --------------------------------------------------------
    # EVALUASI MAE
    # --------------------------------------------------------

    mae = mean_absolute_error(
        aktual,
        forecast
    )

    # --------------------------------------------------------
    # EVALUASI RMSE
    # --------------------------------------------------------

    rmse = np.sqrt(
        mean_squared_error(
            aktual,
            forecast
        )
    )

    # --------------------------------------------------------
    # EVALUASI MAPE
    # --------------------------------------------------------

    mape = np.mean(
        np.abs(
            (aktual - forecast)
            / aktual
        )
    ) * 100

    print("\nHASIL EVALUASI")
    print("-" * 70)

    print(
        "MAE  :",
        round(mae, 4)
    )

    print(
        "RMSE :",
        round(rmse, 4)
    )

    print(
        "MAPE :",
        round(mape, 4),
        "%"
    )

    # --------------------------------------------------------
    # DATA HASIL PREDIKSI
    # --------------------------------------------------------

    hasil = pd.DataFrame({

        "Data_Aktual":
            aktual,

        "Data_Prediksi":
            forecast,

        "Error":
            aktual - forecast

    })

    return {

        "variabel":
            nama_variabel,

        "model":
            str(order),

        "jumlah_training":
            len(train),

        "jumlah_testing":
            len(test),

        "MAE":
            mae,

        "RMSE":
            rmse,

        "MAPE":
            mape

    }, hasil


# ============================================================
# EVALUASI SUHU
# ============================================================

hasil_suhu, prediksi_suhu = evaluasi_model(

    suhu,

    "Suhu",

    (1, 1, 0)

)


# ============================================================
# EVALUASI KELEMBABAN
# ============================================================

hasil_kelembaban, prediksi_kelembaban = evaluasi_model(

    kelembaban,

    "Kelembaban",

    (2, 0, 1)

)


# ============================================================
# RINGKASAN HASIL
# ============================================================

ringkasan = pd.DataFrame([

    hasil_suhu,

    hasil_kelembaban

])


print("\n" + "=" * 70)
print("RINGKASAN HASIL EVALUASI MODEL")
print("=" * 70)

print(
    ringkasan.to_string(
        index=False
    )
)


# ============================================================
# SIMPAN HASIL KE EXCEL
# ============================================================

with pd.ExcelWriter(

    "hasil_evaluasi_model.xlsx"

) as writer:

    ringkasan.to_excel(

        writer,

        sheet_name="Ringkasan",

        index=False

    )

    prediksi_suhu.to_excel(

        writer,

        sheet_name="Prediksi_Suhu",

        index=False

    )

    prediksi_kelembaban.to_excel(

        writer,

        sheet_name="Prediksi_Kelembaban",

        index=False

    )


print("\n" + "=" * 70)

print(
    "HASIL EVALUASI DISIMPAN"
)

print(
    "File: hasil_evaluasi_model.xlsx"
)

print("=" * 70)