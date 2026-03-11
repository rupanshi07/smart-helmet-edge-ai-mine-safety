import numpy as np
import pandas as pd
from sensors.gas_sim import simulate_gas_signal
from sensors.vibration_sim import simulate_vibration_signal
from sensors.imu_sim import simulate_acc_signal

N_SAMPLES = 20000   # MUCH larger dataset
OUTFILE = "training_dataset.csv"

def extract_features():
    """Generate one sample containing features for model training."""

    # Randomly choose event type
    classes = ["normal", "gas_anomaly", "vibration_anomaly", "fall_impact", "combined_event"]
    label = np.random.choice(classes)

    # Decide if each sensor has anomaly
    gas_anom = label in ["gas_anomaly", "combined_event"]
    vib_anom = label in ["vibration_anomaly", "combined_event"]
    acc_anom = label in ["fall_impact", "combined_event"]

    # Simulate sensors
    _, gas = simulate_gas_signal(anomaly=gas_anom)
    _, vib = simulate_vibration_signal(anomaly=vib_anom)
    _, acc = simulate_acc_signal(anomaly=acc_anom)

    # Features
    gas_mean = np.mean(gas)
    vib_rms = np.sqrt(np.mean(vib ** 2))
    acc_mag = np.linalg.norm(acc, axis=1)
    acc_mean = np.mean(acc_mag)

    return gas_mean, vib_rms, acc_mean, label


if __name__ == "__main__":
    rows = []

    for _ in range(N_SAMPLES):
        rows.append(extract_features())

    df = pd.DataFrame(rows, columns=[
        "gas_mean", "vib_rms", "acc_mean", "label"
    ])

    df.to_csv(OUTFILE, index=False)
    print(f"Dataset saved to {OUTFILE}")
    print(df.head())
