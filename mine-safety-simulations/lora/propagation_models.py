# lora/propagation_models.py
import numpy as np

def path_loss(distance, pl0=32.4, n=2.3, att_per_meter=0.02):
    """
    LoRa path loss model for underground tunnels.
    pl0: free-space path loss at 1m
    n: path loss exponent (2.0–3.0 typical underground)
    att_per_meter: additional attenuation per meter
    """
    if distance < 1:
        distance = 1

    return pl0 + 10 * n * np.log10(distance) + att_per_meter * distance
