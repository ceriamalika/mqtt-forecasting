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
    "Dashboard ini menampilkan data monitoring sensor suhu dan kelembaban, "
    "hasil forecasting 6 jam ke depan menggunakan ARIMA, "
    "evaluasi model, serta analisis dan rekomendasi berbasis "
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

FILE_SENSOR_FORECASTING = os.path.join(
    BASE_DIR,
    "sensor_data_forecasting.xlsx"
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

    data = pd.read_excel(FILE_DATA)

    sensor_forecasat = pd.read_excel(FILE_DATA, engine="openpyxl")

    
    sensor_forecast.columns = (
    sensor_forecast.columns
    .str.strip()
    .str.lower()
    )
    
    sensor_forecast["timestamp"] = pd.to_datetime(
    sensor_forecast["timestamp"]
    )

    forecast = pd.read_excel(FILE_FORECAST)

    evaluasi = pd.read_excel(FILE_EVALUASI)

    data["timestamp"] = pd.to_datetime(
        data["timestamp"]
    )

    forecast["timestamp"] = pd.to_datetime(
        forecast["timestamp"]
    )

    return data, sensor_forecast, forecast, evaluasi


# ============================================================
# LOAD DATA
# ============================================================

try:

    data, sensor_forecast, forecast, evaluasi = load_data()

except Exception as e:

    st.error(
        "Terjadi kesalahan saat membaca file data."
    )

    st.code(str(e))

    st.stop()


# ============================================================
# MENU SIDEBAR
# ============================================================

st.sidebar.title("Menu Dashboard")

pilihan = st.sidebar.radio(
    "Pilih tampilan:",
    [
        "Monitoring Data",
        "Forecasting 6 Jam",
        "Evaluasi Model",
        "Komentator AI"
    ]
)


# ============================================================
# MENU 1
# MONITORING DATA
# ============================================================

if pilihan == "Monitoring Data":

    st.header("📡 Monitoring Data Sensor")

    st.write(
        "Data monitoring sensor suhu dan kelembaban "
        "yang telah melalui proses preprocessing dan agregasi per jam."
    )

    # --------------------------------------------------------
    # DATA TERAKHIR
    # --------------------------------------------------------

    data_terakhir = sensor_forecast.iloc[-1]

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Suhu Terakhir",
            f"{data_terakhir['suhu']:.2f} °C"
        )

    with col2:

        st.metric(
            "Kelembaban Terakhir",
            f"{data_terakhir['kelembaban']:.2f} %"
        )

    with col3:

        st.metric(
            "Waktu Data",
            str(data_terakhir["timestamp"])
        )


    # --------------------------------------------------------
    # GRAFIK SUHU
    # --------------------------------------------------------

    st.subheader("🌡️ Perubahan Suhu per Jam")

    fig_suhu = go.Figure()

    fig_suhu.add_trace(
        go.Scatter(
            x=sensor_forecast["timestamp"],
            y=sensor_forecast["suhu"],
            mode="lines+markers",
            name="Suhu"
        )
    )

    fig_suhu.update_layout(
        xaxis_title="Waktu",
        yaxis_title="Suhu (°C)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_suhu,
        use_container_width=True
    )


    # --------------------------------------------------------
    # GRAFIK KELEMBABAN
    # --------------------------------------------------------

    st.subheader("💧 Perubahan Kelembaban per Jam")

    fig_kelembaban = go.Figure()

    fig_kelembaban.add_trace(
        go.Scatter(
            x=sensor_forecast["timestamp"],
            y=sensor_forecast["kelembaban"],
            mode="lines+markers",
            name="Kelembaban"
        )
    )

    fig_kelembaban.update_layout(
        xaxis_title="Waktu",
        yaxis_title="Kelembaban (%)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_kelembaban,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TABEL DATA
    # --------------------------------------------------------

    st.subheader("📋 Data Monitoring")

    st.dataframe(
        sensor_forecast,
        use_container_width=True
    )


# ============================================================
# MENU 2
# FORECASTING 6 JAM
# ============================================================

elif pilihan == "Forecasting 6 Jam":

    st.header("🔮 Forecasting 6 Jam ke Depan")

    st.write(
        "Peramalan dilakukan untuk 6 periode atau 6 jam ke depan "
        "menggunakan model ARIMA."
    )


    # --------------------------------------------------------
    # TABEL FORECASTING
    # --------------------------------------------------------

    st.subheader("📋 Hasil Forecasting")

    st.dataframe(
        forecast,
        use_container_width=True
    )


    # --------------------------------------------------------
    # GRAFIK FORECASTING SUHU
    # --------------------------------------------------------

    st.subheader("🌡️ Forecasting Suhu")

    fig_suhu_forecast = go.Figure()

    fig_suhu_forecast.add_trace(
        go.Scatter(
            x=sensor_forecast["timestamp"],
            y=sensor_forecast["suhu"],
            mode="lines",
            name="Suhu Aktual"
        )
    )

    fig_suhu_forecast.add_trace(
        go.Scatter(
            x=forecast["timestamp"],
            y=forecast["prediksi_suhu"],
            mode="lines+markers",
            name="Forecast Suhu"
        )
    )

    fig_suhu_forecast.add_trace(
        go.Scatter(
            x=list(forecast["timestamp"]) +
              list(forecast["timestamp"][::-1]),

            y=list(forecast["batas_atas_suhu"]) +
              list(forecast["batas_bawah_suhu"][::-1]),

            fill="toself",

            fillcolor="rgba(100, 100, 200, 0.2)",

            line=dict(
                color="rgba(255,255,255,0)"
            ),

            name="Interval Kepercayaan"
        )
    )

    fig_suhu_forecast.update_layout(
        xaxis_title="Waktu",
        yaxis_title="Suhu (°C)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_suhu_forecast,
        use_container_width=True
    )


    # --------------------------------------------------------
    # GRAFIK FORECASTING KELEMBABAN
    # --------------------------------------------------------

    st.subheader("💧 Forecasting Kelembaban")

    fig_kelembaban_forecast = go.Figure()

    fig_kelembaban_forecast.add_trace(
        go.Scatter(
            x=sensor_forecast["timestamp"],
            y=sensor_forecast["kelembaban"],
            mode="lines",
            name="Kelembaban Aktual"
        )
    )

    fig_kelembaban_forecast.add_trace(
        go.Scatter(
            x=forecast["timestamp"],
            y=forecast["prediksi_kelembaban"],
            mode="lines+markers",
            name="Forecast Kelembaban"
        )
    )

    fig_kelembaban_forecast.add_trace(
        go.Scatter(
            x=list(forecast["timestamp"]) +
              list(forecast["timestamp"][::-1]),

            y=list(forecast["batas_atas_kelembaban"]) +
              list(forecast["batas_bawah_kelembaban"][::-1]),

            fill="toself",

            fillcolor="rgba(100, 100, 200, 0.2)",

            line=dict(
                color="rgba(255,255,255,0)"
            ),

            name="Interval Kepercayaan"
        )
    )

    fig_kelembaban_forecast.update_layout(
        xaxis_title="Waktu",
        yaxis_title="Kelembaban (%)",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_kelembaban_forecast,
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


    # --------------------------------------------------------
    # TABEL EVALUASI
    # --------------------------------------------------------

    st.subheader("📋 Hasil Evaluasi")

    st.dataframe(
        evaluasi,
        use_container_width=True
    )


    # --------------------------------------------------------
    # METRIK MODEL
    # --------------------------------------------------------

    for i, row in evaluasi.iterrows():

        st.subheader(
            f"Model {row['variabel']}"
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
                f"{row['MAE']:.4f}"
            )

        with col3:

            st.metric(
                "RMSE",
                f"{row['RMSE']:.4f}"
            )

        with col4:

            st.metric(
                "MAPE",
                f"{row['MAPE']:.4f} %"
            )


# ============================================================
# MENU 4
# KOMENTATOR AI
# ============================================================

elif pilihan == "Komentator AI":

    st.header("💬 Komentator AI")

    st.write(
        "LLM digunakan sebagai komentator untuk memberikan analisis "
        "dan rekomendasi berdasarkan data monitoring dan hasil "
        "forecasting 6 jam ke depan."
    )


    # --------------------------------------------------------
    # DATA SENSOR TERAKHIR
    # --------------------------------------------------------

    data_terakhir = sensor_forecast.iloc[-1]

    suhu_terakhir = float(
        data_terakhir["suhu"]
    )

    kelembaban_terakhir = float(
        data_terakhir["kelembaban"]
    )

    waktu_terakhir = str(
        data_terakhir["timestamp"]
    )


    # --------------------------------------------------------
    # FORECAST 6 JAM
    # --------------------------------------------------------

    prediksi_suhu = forecast[
        "prediksi_suhu"
    ].tolist()

    prediksi_kelembaban = forecast[
        "prediksi_kelembaban"
    ].tolist()


    # --------------------------------------------------------
    # KONDISI SENSOR TERAKHIR
    # --------------------------------------------------------

    st.subheader(
        "📊 Kondisi Sensor Terakhir"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Suhu",
            f"{suhu_terakhir:.2f} °C"
        )

    with col2:

        st.metric(
            "Kelembaban",
            f"{kelembaban_terakhir:.2f} %"
        )


    # --------------------------------------------------------
    # HASIL FORECASTING
    # --------------------------------------------------------

    st.subheader(
        "🔮 Hasil Forecasting 6 Jam"
    )

    st.dataframe(
        forecast,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TOMBOL ANALISIS AI
    # --------------------------------------------------------

    if st.button(
        "🔍 Analisis Data dengan AI"
    ):

        # ----------------------------------------------------
        # MENGAMBIL API KEY GROQ
        # ----------------------------------------------------

        api_key = os.getenv(
            "GROQ_API_KEY"
        )


        # ----------------------------------------------------
        # CEK API KEY
        # ----------------------------------------------------

        if not api_key:

            st.error(
                "GROQ_API_KEY belum ditemukan. "
                "Pastikan API Key Groq sudah disimpan "
                "sebagai Environment Variable."
            )

            st.stop()


        # ----------------------------------------------------
        # MEMBUAT CLIENT GROQ
        # ----------------------------------------------------

        client = Groq(
            api_key=api_key
        )


        # ----------------------------------------------------
        # MEMBUAT PROMPT
        # ----------------------------------------------------

        prompt = f"""
Anda adalah komentator AI untuk sistem monitoring sensor IoT.

Analisis data berikut.

DATA SENSOR TERAKHIR:
- Waktu: {waktu_terakhir}
- Suhu terakhir: {suhu_terakhir:.2f} °C
- Kelembaban terakhir: {kelembaban_terakhir:.2f} %

HASIL FORECASTING 6 JAM KE DEPAN:

Prediksi suhu:
{prediksi_suhu}

Prediksi kelembaban:
{prediksi_kelembaban}

Berikan analisis singkat dalam bahasa Indonesia dengan struktur:

1. Kondisi terkini
Jelaskan kondisi suhu dan kelembaban terakhir.

2. Prediksi 6 jam ke depan
Jelaskan kecenderungan perubahan suhu dan kelembaban berdasarkan hasil forecasting.

3. Rekomendasi
Berikan rekomendasi yang relevan berdasarkan kondisi sensor dan hasil prediksi.

4. Insight
Berikan kesimpulan singkat mengenai pola atau kecenderungan data.

Jangan membuat informasi yang tidak terdapat dalam data.
Gunakan bahasa yang mudah dipahami.
"""


        # ----------------------------------------------------
        # MEMANGGIL LLM GROQ
        # ----------------------------------------------------

        with st.spinner(
            "AI sedang menganalisis data..."
        ):

            try:

                completion = client.chat.completions.create(

                    model="openai/gpt-oss-120b",

                    messages=[

                        {
                            "role": "system",
                            "content": (
                                "Anda adalah komentator AI "
                                "untuk sistem monitoring "
                                "sensor IoT."
                            )
                        },

                        {
                            "role": "user",
                            "content": prompt
                        }

                    ],

                    temperature=1,

                    max_completion_tokens=2048,

                    top_p=1,

                    reasoning_effort="medium",

                    stream=False

                )


                # ------------------------------------------------
                # MENGAMBIL HASIL DARI GROQ
                # ------------------------------------------------

                hasil_ai = (
                    completion
                    .choices[0]
                    .message
                    .content
                )


                # ------------------------------------------------
                # MENAMPILKAN HASIL AI
                # ------------------------------------------------

                st.success(
                    "Analisis AI berhasil dibuat."
                )

                st.markdown(
                    "### 🤖 Analisis dan Rekomendasi AI"
                )

                st.write(
                    hasil_ai
                )


            except Exception as e:

                st.error(
                    "Terjadi kesalahan saat "
                    "menghubungkan dengan Groq API."
                )

                st.code(
                    str(e)
                )
