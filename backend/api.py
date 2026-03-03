"""
Zemythra - API Layer (Block B)
Skeleton backend without AI dependency
"""

from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd


# Import Updated Interfaces
from .model import unified_predict
from .decision import evaluate_risk
from .temporal_model import forecast_future_risk

router = APIRouter()

# -------------------------
# Input Schema
# -------------------------
class PredictionInput(BaseModel):
    age: int
    gender: int
    sys_bp: float
    dia_bp: float
    glucose: float
    cholesterol: float
    bmi: float
    heart_rate: float

# =========================
# Real Prediction Endpoint
# =========================
@router.post("/predict")
def predict_risk(data: PredictionInput):

    # Convert request to DataFrame
    input_df = pd.DataFrame([data.model_dump()])

    # Step A – AI Prediction
    risk_score, uncertainty = unified_predict(input_df)

    # Step B – Clinical Decision Logic
    decision_output = evaluate_risk(
        risk_score=risk_score,
        uncertainty=uncertainty
    )

    # Attach numerical outputs
    decision_output["risk_score"] = round(risk_score, 3)
    decision_output["uncertainty"] = round(uncertainty, 3)

    # Step C – Temporal Forecast
    decision_output["future_forecast"] = forecast_future_risk()

    return decision_output


# =========================
# Timeline Endpoint
# =========================
@router.get("/timeline/{patient_id}")
def timeline(patient_id: int):
    return [
        {"month": 1, "risk_score": 0.45},
        {"month": 2, "risk_score": 0.60},
        {"month": 3, "risk_score": 0.72},
        {"month": 4, "risk_score": 0.81}
    ]
