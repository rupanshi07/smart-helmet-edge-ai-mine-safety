from sklearn.linear_model import LogisticRegression
import joblib
import numpy as np

class TinyMLModel:
    def __init__(self):
        self.model = LogisticRegression()

    def train(self, X, y):
        self.model.fit(X, y)
        joblib.dump(self.model, "tinyml.pkl")

    def load(self):
        self.model = joblib.load("tinyml.pkl")

    def predict(self, feats):
        x = np.array([feats[k] for k in sorted(feats.keys())]).reshape(1, -1)
        return self.model.predict(x)[0]
