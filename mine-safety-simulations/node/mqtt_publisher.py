# mqtt_publisher.py
import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = "localhost"
PORT = 1883
TOPIC_PREFIX = "mine/sim/node"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

def publish_sample(node_id=1):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "node_id": node_id,
        "distance": random.randint(10,200),
        "rssi": -70 + random.random()*10,
        "snr": 10+random.random()*20,
        "sf": 9,
        "event": 0,
        "packet_success": 1,
        "vib_rms": random.random(),
        "gas_mean": random.random()*10,
        "peak_acc": random.random()*10
    }
    client.publish(f"{TOPIC_PREFIX}/{node_id}", json.dumps(payload))

if __name__ == "__main__":
    while True:
        for nid in range(1,6):
            publish_sample(nid)
        time.sleep(1)
