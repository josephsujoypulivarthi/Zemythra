"""
Zemythra - Temporal Intelligence Module
Block C: Time-Series Progression & Drift Detection
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from scipy.stats import ks_2samp

# -------------------------
# Paths
# -------------------------
TIME_SERIES_PATH = "backend/data/raw/patient_time_series.csv"

# -------------------------
# Load Time-Series Data
# -------------------------
def load_time_series():
    df = pd.read_csv(TIME_SERIES_PATH)
    return df

# -------------------------
# Prepare LSTM Sequences
# -------------------------
def prepare_sequences(sequence_length=3):
    df = load_time_series()

    features = ["glucose", "sys_bp", "cholesterol"]
    target = "risk_score"

    X, y = [], []

    for pid in df.patient_id.unique():
        patient_df = df[df.patient_id == pid]

        values = patient_df[features].values
        risks = patient_df[target].values

        for i in range(len(values) - sequence_length):
            X.append(values[i:i + sequence_length])
            y.append(risks[i + sequence_length])

    return np.array(X), np.array(y)

# -------------------------
# Build LSTM Model
# -------------------------
def build_lstm(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(64, input_shape=input_shape),
        tf.keras.layers.Dense(1)
    ])

    model.compile(
        optimizer="adam",
        loss="mse",
        metrics=["mae"]
    )
    return model

# -------------------------
# Train Temporal Model
# -------------------------
def train_temporal_model():
    X, y = prepare_sequences()

    model = build_lstm(
        input_shape=(X.shape[1], X.shape[2])
    )

    model.fit(
        X, y,
        epochs=25,
        batch_size=8,
        verbose=1
    )

    return model

# -------------------------
# Data Drift Detection
# -------------------------
def detect_drift(reference_df, new_df, alpha=0.05):
    drifted_features = []

    for col in reference_df.columns:
        if col == "risk_score":
            continue

        _, p_value = ks_2samp(
            reference_df[col],
            new_df[col]
        )

        if p_value < alpha:
            drifted_features.append(col)

    return drifted_features

# -------------------------
# Manual Test
# -------------------------
if __name__ == "__main__":
    print("Training temporal LSTM model...")
    model = train_temporal_model()
    print("Temporal model trained successfully")
