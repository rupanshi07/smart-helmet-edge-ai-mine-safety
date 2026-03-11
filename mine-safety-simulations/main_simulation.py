# main_simulation.py
import numpy as np
import pandas as pd

from sensors.imu_sim import simulate_fall
from sensors.gas_sim import simulate_gas_spike
from node.feature_extraction import features_from_imu, features_from_gas
from node.tinyml_model import TinyMLModel
from lora.lora_sim import packet_success
from gateway.ml_adr import MLADR

import matplotlib.pyplot as plt


# ============================================================
# 1. SIMULATE SENSOR INPUTS
# ============================================================

print("Simulating IMU fall event...")
t_imu, acc = simulate_fall()

print("Simulating gas spike event...")
t_gas, gas = simulate_gas_spike()


# ============================================================
# 2. FEATURE EXTRACTION
# ============================================================

imu_feats = features_from_imu(acc)
gas_feats = features_from_gas(gas)

combined_features = {**imu_feats, **gas_feats}

print("\nExtracted Features:")
for k, v in combined_features.items():
    print(f"{k}: {v:.3f}")


# ============================================================
# 3. LOAD TINYML MODEL
# ============================================================

model = TinyMLModel()
model.load()

event = model.predict(combined_features)
print(f"\nTinyML Detection Result (0=Safe, 1=Hazard): {event}")


# ============================================================
# 4. LORA SIMULATION (Corrected)
# ============================================================

distance = 120     # meters
tx_power = 14      # dBm
sf = 9             # spreading factor

success, snr, rssi = packet_success(tx_power, distance, sf)

print("\nLoRa Transmission:")
print(f"Distance: {distance} m")
print(f"RSSI: {rssi:.2f} dBm")
print(f"SNR:  {snr:.2f} dB")
print("Packet Success!" if success else "Packet Lost!")


# ============================================================
# 5. GATEWAY ML-ADR OPTIMIZATION
# ============================================================

positions = np.array([[20], [50], [80], [120], [150], [200]])
rssi_data = np.array([-70, -83, -90, -98, -105, -115])

adr = MLADR()
adr.train(positions, rssi_data)

predicted_rssi = adr.predict_rssi(distance)

print(f"\nGateway ML-ADR Predicted RSSI at {distance} m: {predicted_rssi:.2f} dBm")

if predicted_rssi < -100:
    sf = min(12, sf + 1)
    print(f"ADR Recommendation → Increase SF to {sf}")
else:
    print("ADR Recommendation → Keep SF unchanged")


# ============================================================
# 6. LOG AND SAVE RESULTS
# ============================================================

df = pd.DataFrame([{
    "distance": distance,
    "snr": snr,
    "rssi": rssi,
    "sf": sf,
    "event": event,
    "packet_success": int(success)
}])

df.to_csv("simulation_log.csv", index=False)
print("\nSaved simulation_log.csv")


# ============================================================
# 7. VISUALIZATION
# ============================================================

plt.figure()
plt.plot(rssi_data, label="Training RSSI")
plt.scatter([distance], [rssi], label="Current", marker='o')
plt.title("RSSI Trend (ML-ADR Training Data)")
plt.xlabel("Sample Index")
plt.ylabel("RSSI (dBm)")
plt.legend()
plt.grid(True)
plt.savefig("rssi_plot.png")

print("Saved rssi_plot.png")
print("\nSimulation Completed Successfully!")
