def run_ml(features):
    gas, acc, gyro = features

    if gas > 100 or acc > 3.5:
        return 2
    elif gas > 30:
        return 1
    return 0
