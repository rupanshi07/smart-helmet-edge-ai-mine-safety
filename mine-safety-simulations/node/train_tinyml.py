import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from tinyml_model import TinyMLModel

# --------------------------------------------------------
# 1. Generate dummy synthetic data (replace with real later)
# --------------------------------------------------------

# Features: [var_acc, peak_acc, mean_acc, gas_rise, gas_mean]
# We create 200 samples with random values
X = np.random.rand(200, 5) * np.array([10, 15, 5, 30, 15])  # scaling ranges

# Labels:
# 0 = normal
# 1 = dangerous
y = np.random.randint(0, 2, 200)

# --------------------------------------------------------
# 2. Train model
# --------------------------------------------------------
model = RandomForestClassifier(n_estimators=50)
model.fit(X, y)

# --------------------------------------------------------
# 3. Save trained model
# --------------------------------------------------------
joblib.dump(model, "tinyml.pkl")

print("Training complete! Model saved as tinyml.pkl")
