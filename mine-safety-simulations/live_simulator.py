import time
import random
import pandas as pd
import joblib
from datetime import datetime

# Load trained RandomForest model
model = joblib.load("tinyml.pkl")

# Output CSV
OUTPUT_FILE = "live_data.csv"

# Ensure CSV exists with correct header
if not hasattr(live := None, "initialized"):
    with open(OUTPUT_FILE, "w") as f:
        f.write(
            "timestamp,node_id,distance,rssi,snr,sf,event,packet_success,"
            "vib_rms,gas_mean,peak_acc,predicted\n"
        )


def generate_live_row(node_id):

    vib_rms = random.uniform(0.01, 3.0)
    gas_mean = random.uniform(200, 900)
    snr = random.uniform(-20, 10)
    rssi = random.uniform(-120, -50)
    distance = random.uniform(1, 300)
    peak_acc = vib_rms * random.uniform(1.5, 3.0)

    # Simple event rule
    event = 1 if (vib_rms > 1.5 or gas_mean > 750 or peak_acc > 4.0) else 0

    sf = random.choice([7, 8, 9, 10])
    packet_success = random.choice([0, 1])

    timestamp = datetime.now().isoformat()

    return {
        "timestamp": timestamp,
        "node_id": node_id,
        "distance": distance,
        "rssi": rssi,
        "snr": snr,
        "sf": sf,
        "event": event,
        "packet_success": packet_success,
        "vib_rms": vib_rms,
        "gas_mean": gas_mean,
        "peak_acc": peak_acc,
    }


def predict_event(row_dict):
    """
    FIX: RandomForest requires named features.
    Convert dict → DataFrame with correct column names.
    """

    df = pd.DataFrame([{
        "vib_rms": row_dict["vib_rms"],
        "gas_mean": row_dict["gas_mean"],
        "snr": row_dict["snr"],
        "rssi": row_dict["rssi"],
        "distance": row_dict["distance"],
        "peak_acc": row_dict["peak_acc"],
    }])

    pred = model.predict(df)[0]
    return int(pred)


print("Starting live simulator. Press Ctrl-C to stop.")

batch = []

try:
    while True:
        for node_id in [1, 2, 3]:
            row = generate_live_row(node_id)

            # ML prediction with valid feature names
            row["predicted"] = predict_event(row)

            batch.append(row)

        if len(batch) >= 6:  # 3 nodes × 2 cycles
            df_batch = pd.DataFrame(batch)
            df_batch.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
            print(f"[{datetime.now()}] Wrote batch of {len(batch)} rows.")
            batch = []

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nStopped live simulator.")
