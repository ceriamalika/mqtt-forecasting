import paho.mqtt.client as mqtt
import sqlite3
from datetime import datetime

# ==============================
# Konfigurasi MQTT
# ==============================
BROKER = "aifsmukswsurya-397a2de2.a03.euc1.aws.hivemq.cloud"
PORT = 8883
USERNAME = "mhsw"
PASSWORD = "ukswsal3"

TOPIC_SUHU = "tas_ai_surya_fsm_uksw/suhu"
TOPIC_KELEMBABAN = "tas_ai_surya_fsm_uksw/kelembaban"

# ==============================
# Database SQLite
# ==============================
conn = sqlite3.connect("sensor_data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    topic TEXT,
    value REAL
)
""")

conn.commit()


# ==============================
# Callback ketika koneksi berhasil
# ==============================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Berhasil terhubung ke MQTT Broker")

        client.subscribe(TOPIC_SUHU)
        client.subscribe(TOPIC_KELEMBABAN)

        print("Subscribe berhasil")
    else:
        print("Gagal koneksi. Error:", rc)


# ==============================
# Callback ketika menerima data
# ==============================
def on_message(client, userdata, msg):
    topic = msg.topic
    value = float(msg.payload.decode())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"[{timestamp}] {topic} = {value}")

    cursor.execute(
        "INSERT INTO sensor_data(timestamp, topic, value) VALUES (?, ?, ?)",
        (timestamp, topic, value)
    )

    conn.commit()


# ==============================
# MQTT Client
# ==============================
client = mqtt.Client()

client.username_pw_set(USERNAME, PASSWORD)

client.tls_set()

client.on_connect = on_connect
client.on_message = on_message

print("Menghubungkan ke MQTT Broker...")

client.connect(BROKER, PORT, 60)

client.loop_forever()