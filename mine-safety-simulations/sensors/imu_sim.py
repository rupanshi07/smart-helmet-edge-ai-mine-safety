import numpy as np

def simulate_acc_signal(duration=1.5, fs=25, anomaly=False):
    """
    Improved IMU accelerometer simulation:
    - baseline = walking/still
    - anomaly = fall with random spike magnitude + recovery pattern
    """

    n = int(duration * fs)
    t = np.linspace(0, duration, n)

    # baseline walking / idle sensor noise
    acc = np.zeros((n, 3))
    acc[:, 2] = 1 + 0.05 * np.random.randn(n)  # gravity axis
    acc[:, 0] = 0.05 * np.random.randn(n)
    acc[:, 1] = 0.05 * np.random.randn(n)

    if anomaly:
        fall_index = np.random.randint(n//4, n//2)

        # random fall magnitude
        impulse = np.array([
            np.random.uniform(3, 8),
            np.random.uniform(3, 8),
            np.random.uniform(-10, -6)
        ])
        acc[fall_index:fall_index+2] += impulse

        # recovery phase small oscillations
        for i in range(fall_index+2, n):
            acc[i] += 0.1 * np.random.randn(3)

    return t, acc
