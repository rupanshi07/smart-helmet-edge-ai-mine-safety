#!/usr/bin/env python3
"""
ml/edge_node.py

Simulated edge device:
 - loads trained pipeline (mine_safety_model.pkl)
 - simulates sensors (gas, vibration, imu) using project sensors
 - extracts features (gas_mean, vib_rms, acc_mean)
 - runs inference at INTERVAL seconds
 - if predicted event != normal -> packs compact payload and publishes via MQTT
 - logs statistics (packets per minute, sent bytes/min)
"""

import os
import sys
import time
import argparse
import joblib
import struct
import json
from datetime import datetime, timedelta
from collections import deque

# ensure project root imports work
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

# Import your sensor simulators (they are in sensors/)
from sensors.gas_sim import simulate_gas_spike
from sensors.vibration_sim import simulate_combined_vibration, compute_rms
from sensors.imu_sim import simulate_accelerometer_data

# MQTT library (optional)
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except Exception:
    MQTT_AVAILABLE = False

# ---------------------------
# CONFIG / DEFAULTS
# ---------------------------
MODEL_PATH = os.path.join(CURRENT_DIR, "mine_safety_model.pkl")
ENCODER_PATH = os.path.join(CURRENT_DIR, "label_encoder.pkl")

DEFAULT_BROKER = "localhost"
DEFAULT_PORT = 1883
MQTT_TOPIC_EVENTS = "mine/edge/events"   # topic for compact alerts
HEARTBEAT_TOPIC = "mine/edge/heartbeat"

# Node identity
NODE_ID = 0x01F4  # example node id 500

# ---------------------------
# Utilities
# ---------------------------
def pack_compact_payload(node_id, event_id, confidence_byte, battery_pct, seq, flags=0):
    """
    Example compact payload (8 bytes minimal):
    Byte 0-1: node_id (uint16)
    Byte 2: event_type (4 bits) | severity (4 bits)  -> here severity=0
    Byte 3: confidence (0-255)
    Byte 4: battery_pct (0-100)
    Byte 5-6: seq (uint16)
    Byte 7: flags (bitfield)
    => total 8 bytes
    """
    # event_id (0..15) in low 4 bits, severity 0 in high 4 bits
    event_sev = (0 << 4) | (event_id & 0x0F)
    payload = struct.pack("<HBBBBHB", node_id & 0xFFFF, event_sev,
                          confidence_byte, int(battery_pct) & 0xFF,
                          (seq & 0xFF), ((seq >> 8) & 0xFF), flags & 0xFF)
    # Note: struct format used to keep bytes predictable; returns 8 bytes + one extra because format used.
    # To return exactly 8 bytes we will manually construct:
    b0 = node_id & 0xFF
    b1 = (node_id >> 8) & 0xFF
    b2 = event_sev & 0xFF
    b3 = confidence_byte & 0xFF
    b4 = int(battery_pct) & 0xFF
    b5 = seq & 0xFF
    b6 = (seq >> 8) & 0xFF
    b7 = flags & 0xFF
    return bytes([b0, b1, b2, b3, b4, b5, b6, b7])


def pretty_payload_hex(payload_bytes):
    return payload_bytes.hex()


# ---------------------------
# Node runtime
# ---------------------------
def run_node(broker, port, interval=1.0, simulation_duration=None,
             publish_mqtt=True, heartbeat_every=60):
    # Load model pipeline
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model file not found: " + MODEL_PATH)
    pipeline = joblib.load(MODEL_PATH)

    # Load label encoder if exists (to print labels)
    if os.path.exists(ENCODER_PATH):
        label_encoder = joblib.load(ENCODER_PATH)
        label_names = list(label_encoder.classes_)
    else:
        label_encoder = None
        label_names = None

    # Connect MQTT if requested and available
    client = None
    if publish_mqtt:
        if not MQTT_AVAILABLE:
            print("paho-mqtt not installed. Install it or run with --no-mqtt.")
            publish_mqtt = False
        else:
            client = mqtt.Client()
            try:
                client.connect(broker, port, 60)
                client.loop_start()
                print(f"Connected to MQTT broker {broker}:{port}")
            except Exception as e:
                print("Could not connect to broker:", e)
                client = None
                publish_mqtt = False

    seq = 0
    start_time = time.time()
    sent_packets = 0
    sent_bytes = 0
    packet_times = deque()  # timestamps of sent packets for packets/min
    next_heartbeat = time.time() + heartbeat_every

    print("Edge node started. Interval:", interval, "s. Press Ctrl-C to stop.")
    try:
        while True:
            loop_start = time.time()

            # Simulate one window per interval
            # Gas: coarse fs = 1 sample/sec typically -> use simulate_gas_spike with fs=1 for short windows
            _, gas_series = simulate_gas_spike(duration=max(1, interval), fs=max(1, int(1)))
            gas_mean = float(gas_series.mean())

            # Vibration: use combined simulator with small duration window
            duration_v = max(1.0, interval)
            tv, vib = simulate_combined_vibration(duration=duration_v, fs=100.0)
            vib_rms = float(compute_rms(vib))
            vib_peak = float(max(abs(vib))) if len(vib) else 0.0

            # IMU: use accelerometer wrapper
            _, acc = simulate_accelerometer_data(duration=max(1.0, interval), fs=50, event="normal")
            acc_norm = (acc**2).sum(axis=1)**0.5
            acc_mean = float(acc_norm.mean())

            # Build feature vector consistent with training order:
            # training used columns like gas_mean, vib_rms, acc_mean (or peak_acc etc.)
            x = [[gas_mean, vib_rms, acc_mean]]

            # Run inference
            pred_encoded = pipeline.predict(x)[0]
            # probability/confidence if available
            try:
                proba = pipeline.predict_proba(x)[0]
                conf = float(max(proba))
            except Exception:
                conf = 1.0

            # Map to label name if encoder known
            if label_names:
                label_str = label_names[int(pred_encoded)]
            else:
                label_str = str(pred_encoded)

            # Convert confidence to 0..255 byte
            conf_byte = int(max(0, min(255, round(conf * 255))))

            # Simulate battery level (for message)
            battery_pct = 90 - ((time.time() - start_time) / 3600.0) * 0.1  # trivial drain

            # If event is not "normal" (assume label "normal" present), send alert
            is_alert = False
            if label_names:
                is_alert = (label_str != "normal")
            else:
                # if numeric mapping unknown, assume 3 is normal (older mapping) -> send if !=3
                is_alert = (pred_encoded != 3)

            if is_alert:
                # Pack compact payload
                payload = pack_compact_payload(NODE_ID, int(pred_encoded), conf_byte, battery_pct, seq, flags=0)
                seq = (seq + 1) & 0xFFFF

                # Publish or log
                if publish_mqtt and client:
                    client.publish(MQTT_TOPIC_EVENTS, payload)
                else:
                    # fallback: print hex + json metadata
                    print(f"[{datetime.now().isoformat()}] PUB (hex): {pretty_payload_hex(payload)} label={label_str} conf={conf:.2f}")

                # Stats
                sent_packets += 1
                sent_bytes += len(payload)
                packet_times.append(time.time())

            # Heartbeat: send a status summary periodically
            if publish_mqtt and client and time.time() >= next_heartbeat:
                hb = {
                    "node_id": NODE_ID,
                    "timestamp": datetime.now().isoformat(),
                    "battery": battery_pct,
                    "sent_packets": sent_packets
                }
                client.publish(HEARTBEAT_TOPIC, json.dumps(hb))
                next_heartbeat = time.time() + heartbeat_every

            # Periodic logging of packets/min and bytes/min (every 30s)
            if len(packet_times):
                # remove older than 60s
                cutoff = time.time() - 60.0
                while packet_times and packet_times[0] < cutoff:
                    packet_times.popleft()
            ppm = len(packet_times)  # packets in last 60s
            bps_min = (sent_bytes / max(1, (time.time() - start_time))) * 60.0  # approx bytes/min since start

            # print small status line
            print(f"[{datetime.now().strftime('%H:%M:%S')}] label={label_str:17s} conf={conf:.2f} alert={is_alert} ppm={ppm} seq={seq}")

            # Stop condition if simulation_duration provided
            if simulation_duration and (time.time() - start_time) > simulation_duration:
                break

            # Sleep until next interval (compensate for processing time)
            elapsed = time.time() - loop_start
            to_sleep = max(0.0, interval - elapsed)
            time.sleep(to_sleep)

    except KeyboardInterrupt:
        print("\nEdge node stopped by user.")

    finally:
        if client:
            client.loop_stop()
            client.disconnect()
        print("Final stats: packets_sent:", sent_packets, "bytes_sent:", sent_bytes)


# ---------------------------
# CLI
# ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulated Edge Node (Edge ML inference + compact alert publishing)")
    parser.add_argument("--broker", default=DEFAULT_BROKER, help="MQTT broker host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="MQTT broker port")
    parser.add_argument("--interval", type=float, default=1.0, help="Inference interval in seconds")
    parser.add_argument("--duration", type=float, default=None, help="Run duration in seconds (optional)")
    parser.add_argument("--no-mqtt", action="store_true", help="Do not publish to MQTT; print alerts instead")
    parser.add_argument("--node-id", type=int, default=NODE_ID, help="Node ID (uint16)")
    args = parser.parse_args()

    NODE_ID = args.node_id

    run_node(
        broker=args.broker,
        port=args.port,
        interval=args.interval,
        simulation_duration=args.duration,
        publish_mqtt=not args.no_mqtt
    )
