"""
Zemythra - AI Core (Block A)
Static Risk Intelligence
"""

import pandas as pd
import numpy as np
import joblib
import shap

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

# -------------------------
# Paths
# -------------------------
DATA_PATH = "backend/data/raw/clinical_risk_data.csv"
MODEL_PATH = "backend/data/raw/risk_model.pkl"

# -------------------------
# Load Data
# -------------------------
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df

# -------------------------
# Train Risk Model
# -------------------------
def train_model():
    df = load_data()

    X = df.drop(["patient_id", "disease"], axis=1)
    y = df["disease"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000))
    ])

    pipeline.fit(X_train, y_train)

    preds = pipeline.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)

    print("ROC-AUC:", round(auc, 3))

    joblib.dump(pipeline, MODEL_PATH)
    return pipeline

# -------------------------
# Load Model
# -------------------------
def load_model():
    return joblib.load(MODEL_PATH)

# -------------------------
# Uncertainty Estimation
# -------------------------
def predict_with_uncertainty(model, X, runs=25):
    samples = []
    for _ in range(runs):
        samples.append(model.predict_proba(X)[:, 1])
    samples = np.array(samples)
    return samples.mean(axis=0), samples.std(axis=0)

# -------------------------
# Explainability
# -------------------------
def explain(model, X_sample):
    explainer = shap.Explainer(model.named_steps["clf"], X_sample)
    return explainer(X_sample)



# =========================
# UNIFIED AI INTERFACE
# =========================

def unified_predict(input_df):
    """
    Single entry point for risk prediction + uncertainty
    Used by backend API
    """
    model = load_model()
    risk, uncertainty = predict_with_uncertainty(model, input_df)
    return float(risk[0]), float(uncertainty[0])

# -------------------------
# Manual Test
# -------------------------
if __name__ == "__main__":
    model = train_model()
    