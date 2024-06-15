from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
from datetime import datetime

app = Flask(__name__)
data_list = []
temp_data = {}

MQTT_BROKER = "cf51542a2b6a44cf87e18d95189c5496.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC_TEMPERATURE = "elysian/rasya/temperature"
MQTT_TOPIC_HUMIDITY = "elysian/rasya/humidity"
MQTT_USERNAME = "doruu"
MQTT_PASSWORD = "DoruKajuju1"

def on_connect(client, userdata, flags, rc):
    print(f"Terhubung\nKode: {rc}")
    client.subscribe(MQTT_TOPIC_TEMPERATURE)
    client.subscribe(MQTT_TOPIC_HUMIDITY)

def on_message(client, userdata, msg):
    global temp_data, data_list
    payload = msg.payload.decode()
    topic = msg.topic
    timestamp = datetime.now()
    print(f"Menerima Pesan '{payload}' pada topik '{topic}'")
    
    if topic == MQTT_TOPIC_TEMPERATURE:
        temp_data['suhu'] = float(payload)
    elif topic == MQTT_TOPIC_HUMIDITY:
        temp_data['kelembaban'] = float(payload)
    if 'suhu' in temp_data and 'kelembaban' in temp_data:
        data = {
            'timestamp': timestamp,
            'suhu': temp_data['suhu'],
            'kelembaban': temp_data['kelembaban']
        }
        data_list.append(data)
        print(f"Data dimasukan: {data}")
        temp_data = {}

client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.tls_set()

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

@app.route('/datarasya', methods=['POST'])
def add_dummy_data():
    datadariesp = request.json.get()

    if not datadariesp:
        return jsonify({"error": "Missing data"}), 400

    for data in datadariesp:
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        timestamp = data.get('timestamp', datetime.now())

        if temperature == None or humidity == None:
            return jsonify({"error": "Data tidak lengkap"}), 400

        dummy_data = {
            "suhu": temperature,
            "kelembaban": humidity,
            "timestamp": timestamp
        }
        data_list.append(dummy_data)
        print(f"Appended data: {dummy_data}")

    print(f"Final data list: {data_list}")
    return jsonify({"message": "Data berhasil diinput"}), 200

@app.route('/datarasya', methods=['GET'])
def get_data():
    print(f"Data list on GET request: {data_list}")
    return jsonify(data_list), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)