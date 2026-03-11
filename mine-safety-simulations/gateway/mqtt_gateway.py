# mqtt_gateway.py
import paho.mqtt.client as mqtt
import json

BROKER = "localhost"
PORT = 1883
TOPIC = "mine/sim/#"

def on_connect(client, userdata, flags, rc):
    print("Connected with rc", rc)
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    # Here you could run ML inference, ADR, and append to CSV
    print("Msg:", payload)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
