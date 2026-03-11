import numpy as np
from sklearn.ensemble import RandomForestRegressor

class MLADR:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50)

    def train(self, X, y):
        self.model.fit(X, y)

    def predict_rssi(self, pos):
        return self.model.predict([[pos]])[0]
