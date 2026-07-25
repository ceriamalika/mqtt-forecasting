import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from groq import Groq

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================

st.set_page_config(
    page_title="Dashboard Monitoring dan Forecasting Sensor IoT",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# JUDUL DASHBOARD
# ============================================================

st.title("📊 Dashboard Monitoring dan Forecasting Sensor IoT")

st.write(
    "Dashboard ini menampilkan data monitoring sensor suhu dan "
    "kelembaban, hasil forecasting 6 jam ke depan menggunakan "
    "ARIMA, evaluasi model, serta analisis menggunakan "
    "Large Language Model (LLM) Groq."
)

# ============================================================
# LOKASI FILE
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FILE_DATA = os.path.join(
    BASE_DIR,
    "sensor_data.xlsx"
)

FILE_FORECAST = os.path.join(
    BASE_DIR,
    "hasil_forecasting_6_jam.xlsx"
)

FILE_EVALUASI = os.path.join(
    BASE_DIR,
    "hasil_evaluasi_model.xlsx"
)

# ============================================================
# MEMBACA DATA
# ============================================================

@st.cache_data
def load_data():

    # ----------------------------
    # DATA SENSOR MQTT
    # ----------------------------

    data = pd.read_excel(
        FILE_DATA,
        engine="openpyxl"
    )

    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
    )

    # ----------------------------
    # JIKA FORMAT MQTT
    # id | timestamp | topic | value
    # ----------------------------

    if (
        "topic" in data.columns
        and
        "value" in data.columns
    ):

        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            errors="coerce",
            dayfirst=True
        )

        data["value"] = pd.to_numeric(
            data["value"],
            errors="coerce"
        )

        data["jenis"] = (
            data["topic"]
            .astype(str)
            .str.lower()
            .str.split("/")
            .str[-1]
        )

        data = (
            data
            .pivot_table(
                index="timestamp",
                columns="jenis",
                values="value",
                aggfunc="mean"
            )
            .reset_index()
        )

        data.columns.name = None

    # ----------------------------
    # SAMAKAN NAMA KOLOM
    # ----------------------------

    rename_dict = {}

    for c in data.columns:

        cl = c.lower()

        if "temp" in cl:
            rename_dict[c] = "suhu"

        elif "suhu" in cl:
            rename_dict[c] = "suhu"

        elif "humid" in cl:
            rename_dict[c] = "kelembaban"

        elif "kelembaban" in cl:
            rename_dict[c] = "kelembaban"

        elif "time" in cl:
            rename_dict[c] = "timestamp"

    data = data.rename(
        columns=rename_dict
    )

    # ----------------------------
    # CEK KOLOM WAJIB
    # ----------------------------

    kolom_wajib = [
        "timestamp",
        "suhu",
        "kelembaban"
    ]

    kurang = [
        k
        for k in kolom_wajib
        if k not in data.columns
    ]

    if len(kurang) > 0:

        st.error(
            "Kolom berikut tidak ditemukan:\n\n"
            + ", ".join(kurang)
        )

        st.write(
            "Kolom yang tersedia:"
        )

        st.write(
            list(data.columns)
        )

        st.stop()

    # ----------------------------
    # URUTKAN DATA
    # ----------------------------

    data = (
        data
        .sort_values(
            "timestamp"
        )
        .reset_index(
            drop=True
        )
    )

    # ----------------------------
    # FORECAST
    # ----------------------------

    forecast = pd.read_excel(
        FILE_FORECAST,
        engine="openpyxl"
    )

    forecast["timestamp"] = pd.to_datetime(
        forecast["timestamp"],
        errors="coerce"
    )

    # ----------------------------
    # EVALUASI
    # ----------------------------

    evaluasi = pd.read_excel(
        FILE_EVALUASI,
        engine="openpyxl"
    )

    return (
        data,
        forecast,
        evaluasi
    )

# ============================================================
# MENU 2
# FORECASTING 6 JAM
# ============================================================

elif pilihan == "Forecasting 6 Jam":

    st.header("🔮 Forecasting 6 Jam ke Depan")

    st.write(
        "Peramalan dilakukan menggunakan model ARIMA "
        "berdasarkan data historis sensor."
    )

    st.subheader("📋 Hasil Forecasting")

    st.dataframe(
        forecast,
        use_container_width=True
    )

    # ========================================================
    # GRAFIK SUHU
    # ========================================================

    st.subheader("🌡️ Forecasting Suhu")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["timestamp"],
            y=data["suhu"],
            mode="lines+markers",
            name="Data Aktual"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast["timestamp"],
            y=forecast["prediksi_suhu"],
            mode="lines+markers",
            name="Forecast"
        )
    )

    if (
        "batas_bawah_suhu" in forecast.columns
        and
        "batas_atas_suhu" in forecast.columns
    ):

        fig.add_trace(

            go.Scatter(

                x=list(forecast["timestamp"])
                +
                list(forecast["timestamp"][::-1]),

                y=list(forecast["batas_atas_suhu"])
                +
                list(forecast["batas_bawah_suhu"][::-1]),

                fill="toself",

                fillcolor="rgba(0,100,255,0.2)",

                line=dict(
                    color="rgba(255,255,255,0)"
                ),

                hoverinfo="skip",

                showlegend=True,

                name="Interval Kepercayaan"

            )

        )

    fig.update_layout(

        xaxis_title="Waktu",

        yaxis_title="Suhu (°C)",

        hovermode="x unified"

    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ========================================================
    # GRAFIK KELEMBABAN
    # ========================================================

    st.subheader("💧 Forecasting Kelembaban")

    fig2 = go.Figure()

    fig2.add_trace(

        go.Scatter(

            x=data["timestamp"],

            y=data["kelembaban"],

            mode="lines+markers",

            name="Data Aktual"

        )

    )

    fig2.add_trace(

        go.Scatter(

            x=forecast["timestamp"],

            y=forecast["prediksi_kelembaban"],

            mode="lines+markers",

            name="Forecast"

        )

    )

    if (

        "batas_bawah_kelembaban" in forecast.columns

        and

        "batas_atas_kelembaban" in forecast.columns

    ):

        fig2.add_trace(

            go.Scatter(

                x=list(forecast["timestamp"])
                +
                list(forecast["timestamp"][::-1]),

                y=list(forecast["batas_atas_kelembaban"])
                +
                list(forecast["batas_bawah_kelembaban"][::-1]),

                fill="toself",

                fillcolor="rgba(0,180,255,0.2)",

                line=dict(
                    color="rgba(255,255,255,0)"
                ),

                hoverinfo="skip",

                showlegend=True,

                name="Interval Kepercayaan"

            )

        )

    fig2.update_layout(

        xaxis_title="Waktu",

        yaxis_title="Kelembaban (%)",

        hovermode="x unified"

    )

    st.plotly_chart(

        fig2,

        use_container_width=True

    )

# ============================================================
# MENU 3
# EVALUASI MODEL
# ============================================================

elif pilihan == "Evaluasi Model":

    st.header("📈 Evaluasi Model ARIMA")

    st.write(
        "Evaluasi dilakukan menggunakan MAE, RMSE, dan MAPE."
    )

    st.subheader("📋 Hasil Evaluasi")

    st.dataframe(
        evaluasi,
        use_container_width=True
    )

    if len(evaluasi) == 0:

        st.warning(
            "Data evaluasi tidak ditemukan."
        )

    else:

        for _, row in evaluasi.iterrows():

            st.markdown("---")

            st.subheader(
                f"Variabel : {row['variabel']}"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Model",
                    str(row["model"])
                )

            with col2:

                st.metric(
                    "MAE",
                    f"{float(row['MAE']):.4f}"
                )

            with col3:

                st.metric(
                    "RMSE",
                    f"{float(row['RMSE']):.4f}"
                )

            with col4:

                st.metric(
                    "MAPE",
                    f"{float(row['MAPE']):.4f} %"
                )

            if float(row["MAPE"]) < 10:

                st.success(
                    "Kategori Akurasi : Sangat Baik"
                )

            elif float(row["MAPE"]) < 20:

                st.info(
                    "Kategori Akurasi : Baik"
                )

            elif float(row["MAPE"]) < 50:

                st.warning(
                    "Kategori Akurasi : Cukup"
                )

            else:

                st.error(
                    "Kategori Akurasi : Buruk"
                )

    st.markdown("---")

    st.subheader(
        "Interpretasi Metrik"
    )

    st.markdown(
        """
**MAE (Mean Absolute Error)** menunjukkan rata-rata
kesalahan absolut hasil prediksi terhadap data aktual.

**RMSE (Root Mean Square Error)** memberikan penalti
lebih besar terhadap kesalahan yang besar.

**MAPE (Mean Absolute Percentage Error)** menunjukkan
persentase rata-rata kesalahan prediksi.

Semakin kecil nilai MAE, RMSE dan MAPE maka semakin
baik performa model ARIMA.
"""
    )

# ============================================================
# MENU 4
# KOMENTATOR AI
# ============================================================

elif pilihan == "Komentator AI":

    st.header("💬 Komentator AI")

    st.write(
        "Analisis otomatis menggunakan Large Language Model (LLM) Groq "
        "berdasarkan data monitoring dan hasil forecasting."
    )

    # ========================================================
    # DATA TERAKHIR
    # ========================================================

    data_terakhir = data.iloc[-1]

    suhu_terakhir = float(data_terakhir["suhu"])
    kelembaban_terakhir = float(data_terakhir["kelembaban"])
    waktu_terakhir = str(data_terakhir["timestamp"])

    st.subheader("📊 Kondisi Sensor Terakhir")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Suhu",
            f"{suhu_terakhir:.2f} °C"
        )

    with c2:
        st.metric(
            "Kelembaban",
            f"{kelembaban_terakhir:.2f} %"
        )

    with c3:
        st.metric(
            "Waktu",
            waktu_terakhir
        )

    st.markdown("---")

    st.subheader("🔮 Forecasting 6 Jam")

    st.dataframe(
        forecast,
        use_container_width=True
    )

    prediksi_suhu = forecast["prediksi_suhu"].tolist()
    prediksi_kelembaban = forecast["prediksi_kelembaban"].tolist()

    st.markdown("---")

    if st.button("🔍 Analisis Data dengan AI"):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:

            st.error(
                "Environment Variable GROQ_API_KEY belum ditemukan."
            )

            st.stop()

        try:

            client = Groq(
                api_key=api_key
            )

            prompt = f"""
Anda adalah analis IoT.

Analisis data berikut.

DATA TERAKHIR

Waktu :
{waktu_terakhir}

Suhu :
{suhu_terakhir:.2f} °C

Kelembaban :
{kelembaban_terakhir:.2f} %

HASIL FORECASTING SUHU

{prediksi_suhu}

HASIL FORECASTING KELEMBABAN

{prediksi_kelembaban}

Berikan jawaban dalam Bahasa Indonesia.

Gunakan format:

## Kondisi Saat Ini

## Prediksi

## Rekomendasi

## Kesimpulan

Jangan membuat data yang tidak ada.
"""

            with st.spinner(
                "AI sedang menganalisis..."
            ):

                response = client.chat.completions.create(

                    model="openai/gpt-oss-120b",

                    messages=[

                        {
                            "role": "system",
                            "content": (
                                "Anda adalah analis data IoT."
                            )
                        },

                        {
                            "role": "user",
                            "content": prompt
                        }

                    ],

                    temperature=0.7,

                    max_completion_tokens=1024,

                    top_p=1,

                    stream=False

                )

                hasil_ai = (
                    response
                    .choices[0]
                    .message
                    .content
                )

            st.success(
                "Analisis berhasil dibuat."
            )

            st.markdown(
                "## 🤖 Analisis dan Rekomendasi AI"
            )

            st.markdown(
                hasil_ai
            )

        except Exception as e:

            st.error(
                "Gagal menghubungkan ke Groq API."
            )

            st.code(str(e))

