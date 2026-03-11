import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import joblib
from datetime import datetime
import os

# ------------------------------------------------------
# 1. DATA GENERATION
# ------------------------------------------------------

def generate_sample():
    """Generate one synthetic mining-sensor sample."""
    vib_rms = np.random.uniform(0.01, 3.0)
    gas = np.random.uniform(200, 900)
    snr = np.random.uniform(-20, 10)
    rssi = np.random.uniform(-120, -50)
    distance = np.random.uniform(1, 300)
    peak_acc = vib_rms * np.random.uniform(1.5, 3.0)

    # Event logic (very simple)
    is_event = 1 if (vib_rms > 1.5 or gas > 750 or peak_acc > 4.0) else 0

    return vib_rms, gas, snr, rssi, distance, peak_acc, is_event


def generate_dataset(n=5000):
    """Generate dataset of n rows."""
    rows = [generate_sample() for _ in range(n)]
    df = pd.DataFrame(
        rows,
        columns=[
            "vib_rms",
            "gas_mean",
            "snr",
            "rssi",
            "distance",
            "peak_acc",
            "event"
        ]
    )
    return df


# ------------------------------------------------------
# 2. TRAIN RANDOM FOREST (for TinyML classical model)
# ------------------------------------------------------

def train_random_forest(df):
    X = df[["vib_rms", "gas_mean", "snr", "rssi", "distance", "peak_acc"]]
    y = df["event"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("RandomForest accuracy:", (preds == y_test).mean())
    print(classification_report(y_test, preds))

    joblib.dump(model, "tinyml.pkl")
    print("Saved tinyml.pkl")

    return model


# ------------------------------------------------------
# 3. TRAIN TENSORFLOW MODEL + EXPORT TFLITE
# ------------------------------------------------------

def train_tf_and_export_tflite(df):

    X = df[["vib_rms", "gas_mean", "snr", "rssi", "distance", "peak_acc"]].values
    y = df["event"].values

    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(6,)),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(8, activation="relu"),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )

    model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=20,
        batch_size=32
    )

    # Test accuracy
    acc = model.evaluate(X_test, y_test)[1]
    print(f"TF model test acc: {acc:.3f}")

    # ------------------------------------------------
    # Save model in Keras format (fix for your error)
    # ------------------------------------------------
    model.save("tiny_model_tf.keras")
    print("Saved tiny_model_tf.keras")

    # ------------------------------------------------
    # Export SavedModel properly (for TFLite)
    # ------------------------------------------------
    export_dir = "tiny_model_tf_savedmodel"
    model.export(export_dir)
    print(f"Saved TensorFlow SavedModel -> {export_dir}/")

    # ------------------------------------------------
    # Convert to TFLite
    # ------------------------------------------------
    converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
    tflite_model = converter.convert()

    with open("tiny_model.tflite", "wb") as f:
        f.write(tflite_model)

    print("Saved tiny_model.tflite")

    return model


# ------------------------------------------------------
# MAIN SCRIPT
# ------------------------------------------------------

if __name__ == "__main__":

    print("Generating dataset...")
    df = generate_dataset(5000)
    print("Dataset generated!")

    # Save raw dataset
    df.to_csv("generated_dataset.csv", index=False)
    print("Saved generated_dataset.csv")

    print("\nTraining RandomForest model...")
    train_random_forest(df)

    print("\nTraining TensorFlow model + exporting TFLite...")
    train_tf_and_export_tflite(df)

    print("\nAll models saved successfully!")
