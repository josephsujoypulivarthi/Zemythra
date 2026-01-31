"""
Zemythra - API Layer (Block B)
Skeleton backend without AI dependency
"""

from fastapi import APIRouter
from pydantic import BaseModel

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

# -------------------------
# Dummy Predict Endpoint
# -------------------------
@router.post("/predict")
def predict_dummy(data: PredictionInput):
    return {
        "risk_score": 0.5,
        "uncertainty": 0.1,
        "risk_level": "Medium",
        "emergency": False,
        "recommended_hospitals": ["District Hospital"]
    }

# -------------------------
# Dummy Timeline
# -------------------------
@router.get("/timeline/{patient_id}")
def timeline(patient_id: int):
    return [
        {"month": 1, "risk_score": 0.3},
        {"month": 2, "risk_score": 0.4},
        {"month": 3, "risk_score": 0.5}
    ]
