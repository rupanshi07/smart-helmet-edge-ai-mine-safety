import numpy as np

def features_from_imu(acc):
    mag = np.linalg.norm(acc, axis=1)
    return {
        "var_acc": np.var(mag),
        "peak_acc": np.max(mag),
        "mean_acc": np.mean(mag)
    }

def features_from_gas(gas_series):
    rise = gas_series[-1] - gas_series[0]
    return {
        "gas_rise": rise,
        "gas_mean": np.mean(gas_series)
    }
