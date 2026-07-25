import pandas as pd

# Membaca file CSV (menggunakan pemisah ;)
df = pd.read_csv("../data/sensor_data.csv", sep=";")

# Mengubah kolom timestamp menjadi datetime
df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True)

# Data suhu
suhu = (
    df[df["topic"] == "tas_ai_surya_fsm_uksw/suhu"][["timestamp", "value"]]
    .groupby("timestamp", as_index=False)
    .mean()
)
suhu = suhu.rename(columns={"value": "suhu"})

# Data kelembaban
kelembaban = (
    df[df["topic"] == "tas_ai_surya_fsm_uksw/kelembaban"][["timestamp", "value"]]
    .groupby("timestamp", as_index=False)
    .mean()
)
kelembaban = kelembaban.rename(columns={"value": "kelembaban"})
# Menggabungkan berdasarkan timestamp
data = pd.merge(suhu, kelembaban, on="timestamp", how="inner")

# Mengurutkan data
data = data.sort_values("timestamp")

# Menyimpan hasil preprocessing
data.to_csv("../data/sensor_preprocessed.csv", index=False)

# Menampilkan hasil
print("===== HASIL PREPROCESSING =====")
print(data.head())

print("\nJumlah data:", len(data))

print("\nStatistik:")
print(data.describe())

print("\nFile berhasil disimpan di:")
print("../data/sensor_preprocessed.csv")