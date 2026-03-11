import numpy as np

def simulate_vibration_signal(duration=2, fs=100, anomaly=False):
    """
    Realistic vibration simulation:
    - baseline machine noise
    - random mechanical pulses
    - anomaly = high RMS due to imbalance or collision
    """

    n = int(duration * fs)
    t = np.linspace(0, duration, n)

    # baseline (normal machine vibration)
    sig = 0.01 * np.random.randn(n)

    # periodic machine cycle vibration
    sig += 0.05 * np.sin(20 * t + np.random.uniform(0, np.pi))

    if anomaly:
        # random burst of high vibration
        start = np.random.randint(0, n//2)
        end = start + np.random.randint(100, 200)
        end = min(end, n)

        sig[start:end] += np.random.uniform(0.5, 2.0) * np.sin(80 * t[start:end])

    return t, sig
