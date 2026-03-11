# lora/lora_channel.py
import numpy as np
from lora.propagation_models import path_loss

def compute_noise_floor(bw=125000, nf=6):
    """
    Computes LoRa noise floor based on bandwidth and noise figure.
    -174 dBm/Hz is thermal noise
    """
    return -174 + 10 * np.log10(bw) + nf


def compute_snr(tx_power, distance, bw=125000, nf=6, shadow_sigma=3):
    """
    Computes SNR and RSSI for a given Tx power and distance.
    Includes path loss + shadowing.
    """
    pl = path_loss(distance)

    # Log-normal shadowing
    shadow = np.random.normal(0, shadow_sigma)

    rssi = tx_power - pl + shadow
    noise = compute_noise_floor(bw=bw, nf=nf)
    snr = rssi - noise
    
    return snr, rssi
