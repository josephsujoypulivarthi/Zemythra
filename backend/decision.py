"""
Zemythra Decision Intelligence
Block E - Clinical Risk Stratification
Owner: Sujoy
"""

import pandas as pd

# -------------------------
# Load Risk Thresholds
# -------------------------
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THRESHOLD_PATH = os.path.join(BASE_DIR, "data", "raw", "risk_thresholds.csv")


def load_thresholds():
    return pd.read_csv(THRESHOLD_PATH)


thresholds = load_thresholds()


# -------------------------
# Risk Level Classification
# -------------------------
def classify_risk(score):

    for _, row in thresholds.iterrows():
        if row["min"] <= score < row["max"]:
            return row["label"]

    return "Unknown"


# -------------------------
# Clinical Decision Engine
# -------------------------
def evaluate_risk(risk_score, uncertainty):

    risk_level = classify_risk(risk_score)

    emergency = False
    recommendation = "Routine monitoring"

    # High Risk Logic
    if risk_level == "High":
        emergency = True
        recommendation = "Immediate clinical evaluation required"

    # Medium Risk Logic
    elif risk_level == "Medium":
        recommendation = "Lifestyle intervention and follow-up"

    # Uncertainty Safety Layer
    if uncertainty > 0.25:
        recommendation += " (High uncertainty — further testing advised)"

    return {
        "risk_level": risk_level,
        "emergency": emergency,
        "recommendation": recommendation
    }


# -------------------------
# Manual Test
# -------------------------
if __name__ == "__main__":

    result = evaluate_risk(
        risk_score=0.72,
        uncertainty=0.12
    )

    print(result)