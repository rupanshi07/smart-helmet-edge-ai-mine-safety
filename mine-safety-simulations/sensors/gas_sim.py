import numpy as np

def simulate_gas_signal(duration=10, fs=1, anomaly=False):
    """
    More realistic gas sensor with:
    - baseline drift
    - random noise
    - random spike start + magnitude (if anomaly=True)
    """

    n = int(duration * fs)
    t = np.linspace(0, duration, n)

    # natural baseline (2–5 ppm)
    baseline = 2 + 0.5 * np.sin(0.1 * t) + 0.2 * np.random.randn(n)

    # slow environmental drift
    drift = 0.02 * t * np.random.uniform(-1, 1)

    gas = baseline + drift

    if anomaly:
        # random spike start
        start = np.random.randint(n // 4, n // 2)
        end = n

        # random magnitude
        spike_height = np.random.uniform(10, 40)

        gas[start:end] += np.linspace(0, spike_height, end - start)

    return t, gas
