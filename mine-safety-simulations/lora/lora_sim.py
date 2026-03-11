# lora/lora_sim.py
import numpy as np
from lora.lora_channel import compute_snr

# LoRa SNR thresholds for SF7–SF12
SF_THRESH = {
    7: -7.5,
    8: -10.0,
    9: -12.5,
    10: -15.0,
    11: -17.5,
    12: -20.0
}

def packet_success(tx_power, distance, sf):
    """
    Computes packet delivery:
    - Compute SNR based on tx power and distance
    - Compare against SF threshold
    - Logistic probability for realistic behavior
    """
    snr, rssi = compute_snr(tx_power, distance)

    threshold = SF_THRESH[sf]
    margin = snr - threshold

    # Logistic model: smooth probability curve
    p = 1 / (1 + np.exp(-1.2 * margin))

    success = np.random.rand() < p

    return success, snr, rssi
