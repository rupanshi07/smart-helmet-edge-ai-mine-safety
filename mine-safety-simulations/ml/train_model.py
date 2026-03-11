import pandas as pd
import numpy as np
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report

DATASET_PATH = "training_dataset.csv"
MODEL_PATH = "mine_safety_model.pkl"
ENCODER_PATH = "label_encoder.pkl"

print("Loading dataset...")
df = pd.read_csv(DATASET_PATH)

X = df[["gas_mean", "vib_rms", "acc_mean"]]
y = df["label"]

# Encode labels
encoder = LabelEncoder()
y_enc = encoder.fit_transform(y)

joblib.dump(encoder, ENCODER_PATH)
print(f"Label encoder saved at {ENCODER_PATH}")

# Train-test split by scenario separation
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, shuffle=True, random_state=42
)

print("Training model (RandomForest)...")

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        random_state=42
    ))
])

pipeline.fit(X_train, y_train)

# Cross-validation
cv_score = cross_val_score(pipeline, X_train, y_train, cv=5)
print("\nCross-validation score:", cv_score)
print("Mean CV:", cv_score.mean())

# Test-set evaluation
pred = pipeline.predict(X_test)
print("\nTEST SET REPORT:\n")
print(classification_report(y_test, pred, target_names=encoder.classes_))

# Save final model
joblib.dump(pipeline, MODEL_PATH)
print(f"Model saved at {MODEL_PATH}")
