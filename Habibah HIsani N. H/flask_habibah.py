from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
from datetime import datetime

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Variabel untuk menyimpan data
data_storage = []
current_data = {}

# Detail konfigurasi MQTT
MQTT_CONFIG = {
    "broker": "cf51542a2b6a44cf87e18d95189c5496.s1.eu.hivemq.cloud",
    "port": 8883,
    "topics": {
        "bpm": "elysian/habibah/bpm",
    },
    "auth": {
        "username": "hisaniii",
        "password": "rasyaaaa"
    }
}

def handle_connect(client, userdata, flags, rc):
    print(f"Connected with result code: {rc}")
    for topic in MQTT_CONFIG["topics"].values():
        client.subscribe(topic)

def handle_message(client, userdata, msg):
    global current_data, data_storage
    pesan = msg.payload.decode()
    topik = msg.topik
    now = datetime.now()
    print(f"terima '{pesan}' pada topik '{topik}'")
    
    if topik == MQTT_CONFIG["topics"]["bpm"]:
        current_data['bpm'] = float(pesan)
    
    if 'bpm' in current_data:
        record = {
            'timestamp': now,
            'bpm': current_data['bpm']
        }
        data_storage.append(record)
        print(f"Inserted record: {record}")
        current_data = {}

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_CONFIG["auth"]["username"], MQTT_CONFIG["auth"]["password"])
mqtt_client.on_connect = handle_connect
mqtt_client.on_message = handle_message
mqtt_client.tls_set()
mqtt_client.connect(MQTT_CONFIG["broker"], MQTT_CONFIG["port"], 60)
mqtt_client.loop_start()

@app.route('/datahabibah', methods=['POST'])
def insert_dummy_data():
    received_data = request.json

    if not received_data:
        return jsonify({"error": "data tidak ada"}), 400

    for entry in received_data:
        bpm = entry.get('bpm')
        waktu = entry.get('timestamp', datetime.now())

        if bpm is None:
            return jsonify({"error": "data tidak lengkap"}), 400

        new_record = {
            "bpm": bpm,
            "timestamp": waktu
        }
        data_storage.append(new_record)
        print(f"data baru ditambah: {new_record}")

    print(f"data masuk: {data_storage}")
    return jsonify({"message": "Don bangg"}), 200

@app.route('/datahabibah', methods=['GET'])
def retrieve_data():
    print(f"data ditampilkan: {data_storage}")
    return jsonify(data_storage), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
