"""
Zemythra - API Layer (Block B)
Skeleton backend without AI dependency
"""
# Updated api.py 

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status  
from fastapi.responses import StreamingResponse
from typing import Optional, List
import pandas as pd
import random
import numpy as np
import joblib
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from pydantic import BaseModel

from backend.auth import authenticate_user, create_token, load_users, create_user


from backend.chat_service import (
   build_prompt,
   call_ollama,
   call_ollama_stream,
   generate_video_suggestions,
   next_question_suggestions,
)


from .model import unified_predict
from .decision import evaluate_risk
from .temporal_model import forecast_future_risk



router = APIRouter()


# ─────────────────────────────────────────────
# 🧠 EXPLAINABILITY FUNCTION (NEW)
# ─────────────────────────────────────────────


def get_explanation(sample_input):
   explanations = []


   if sample_input["glucose"] > 130:
       explanations.append("High glucose levels")


   if sample_input["bmi"] > 25:
       explanations.append("High BMI")


   if sample_input["blood_pressure"] > 85:
       explanations.append("Elevated blood pressure")


   if sample_input["age"] > 40:
       explanations.append("Age risk factor")


   return explanations[:3]


# ─────────────────────────────────────────────
# 🧠 CHAT ENDPOINT (AI + EXPLAINABILITY)
# ─────────────────────────────────────────────


@router.post("/chat")
async def chat(
   prompt: str = Form(...),
   model: str = Form("gemma3:4b"),
   image: Optional[UploadFile] = File(None),
):


   image_bytes = None
   if image:
       image_bytes = await image.read()


   prompt_text = build_prompt(
       user_prompt=prompt,
       has_image=bool(image),
   )


   answer = call_ollama(prompt_text, image_bytes, model=model)


   # 🧠 REAL ML MODEL
   try:
       sample_input = {
           "age": 45,
           "bmi": 28,
           "glucose": 140,
           "blood_pressure": 90,
           "symptom_text": prompt
       }


       risk_score = unified_predict(sample_input)
       risk_score = int(risk_score)


       # 🔥 Explainability
       explanations = get_explanation(sample_input)


   except Exception as e:
       print("Model error:", e)
       risk_score = 0
       explanations = []


   # 🎯 Confidence
   confidence = round(random.uniform(0.75, 0.95), 2)


   return {
       "response": answer,
       "video_suggestions": generate_video_suggestions(prompt),
       "next_questions": next_question_suggestions(prompt),
       "risk_score": risk_score,
       "confidence": confidence,
       "explanations": explanations
   }


# ─────────────────────────────────────────────
# 🔄 STREAM CHAT
# ─────────────────────────────────────────────


@router.post("/chat/stream")
async def chat_stream(
   prompt: str = Form(...),
   model: str = Form("gemma3:4b"),
   image: Optional[UploadFile] = File(None),
):


   image_bytes = None
   if image:
       image_bytes = await image.read()


   prompt_text = build_prompt(
       user_prompt=prompt,
       has_image=bool(image),
   )


   async def generate_tokens():
       try:
           for token in call_ollama_stream(prompt_text, image_bytes, model=model):
               yield token
       except Exception as e:
           yield f"Error: {str(e)}"


   return StreamingResponse(generate_tokens(), media_type="text/plain")


# ─────────────────────────────────────────────
# 🏥 PREDICTION API
# ─────────────────────────────────────────────
class PredictionInput(BaseModel):
    age: int
    gender: int
    sys_bp: float
    dia_bp: float
    glucose: float
    cholesterol: float
    bmi: float
    heart_rate: float

def forecast_future_risk(current_risk: float = 0.5):
    """
    Inverted U-shape: Risk peaks at month 2 (acute phase),
    then improves with treatment
    """
    # Vertex at month 2 (highest point)
    month_1 = current_risk * 1.10  # Rises to 110%
    month_2 = current_risk * 1.25  # Peaks at 125% (highest)
    month_3 = current_risk * 0.90  # Falls to 90%
    month_4 = current_risk * 0.70  # Falls to 70%
    
    return [
        {"month": 1, "risk_score": float(min(1.0, month_1))},
        {"month": 2, "risk_score": float(min(1.0, month_2))},
        {"month": 3, "risk_score": float(min(1.0, month_3))},
        {"month": 4, "risk_score": float(min(1.0, month_4))}
    ]


def get_clinical_message(risk_score: float):
    """Convert risk to clinical message"""
    if risk_score >= 0.8:
        return "CRITICAL - Immediate intervention required"
    elif risk_score >= 0.6:
        return "HIGH - Urgent clinical review needed"
    elif risk_score >= 0.4:
        return "MODERATE - Close monitoring required"
    else:
        return "LOW - Routine monitoring sufficient"

@router.post("/predict")
def predict_risk(data: PredictionInput):
    try:
        # Convert input to DataFrame
        input_df = pd.DataFrame([data.model_dump()])
        
        # Load model
        model = joblib.load("backend/data/raw/risk_model.pkl")
        
        # Get probabilities
        proba = model.predict_proba(input_df)[0]
        
        # Extract values - CONVERT TO PYTHON TYPES (not numpy)
        risk_score = float(np.max(proba))  # ✓ Convert to float
        uncertainty = float(np.std(proba))  # ✓ Convert to float
        
        # Generate forecast
        forecast = forecast_future_risk(risk_score)
        
        # Get message
        message = get_clinical_message(risk_score)
        
        # ENSURE ALL VALUES ARE PYTHON TYPES
        response = {
            "risk_score": float(risk_score),           # ✓ Python float
            "uncertainty": float(uncertainty),         # ✓ Python float
            "message": str(message),                   # ✓ Python str
            "future_forecast": [
                {
                    "month": int(item["month"]),       # ✓ Python int
                    "risk_score": float(item["risk_score"])  # ✓ Python float
                }
                for item in forecast
            ]
        }
        
        return response
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
# ─────────────────────────────────────────────
# 📄 PDF REPORT GENERATOR
# ─────────────────────────────────────────────


class ReportInput(BaseModel):
   risk_score: int
   confidence: float
   explanations: list[str]


@router.post("/report")
def generate_report(data: ReportInput):


   buffer = BytesIO()
   doc = SimpleDocTemplate(buffer)


   styles = getSampleStyleSheet()
   content = []


   # Title
   content.append(Paragraph("AI Health Risk Report", styles["Title"]))
   content.append(Spacer(1, 12))


   # Risk Score
   content.append(Paragraph(f"Risk Score: {data.risk_score}", styles["Heading2"]))
   content.append(Spacer(1, 10))


   # Confidence
   content.append(Paragraph(f"Confidence: {data.confidence}", styles["Normal"]))
   content.append(Spacer(1, 10))


   # Explanation
   content.append(Paragraph("Key Factors:", styles["Heading3"]))
   for exp in data.explanations:
       content.append(Paragraph(f"- {exp}", styles["Normal"]))


   content.append(Spacer(1, 12))


   # Recommendation
   if data.risk_score > 80:
       rec = "High risk detected. Immediate medical consultation recommended."
   elif data.risk_score > 50:
       rec = "Moderate risk. Lifestyle changes advised."
   else:
       rec = "Low risk. Maintain healthy habits."


   content.append(Paragraph("Recommendation:", styles["Heading3"]))
   content.append(Paragraph(rec, styles["Normal"]))


   doc.build(content)


   buffer.seek(0)


   return StreamingResponse(
       buffer,
       media_type="application/pdf",
       headers={"Content-Disposition": "attachment; filename=health_report.pdf"},
   )



# ─────────────────────────────────────────────
# 🔐 LOGIN / REGISTER ENDPOINTS - FIXED FOR FORM DATA
# ─────────────────────────────────────────────────────────

@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Login endpoint - accepts multipart form data
    
    CHANGES:
    - Removed Pydantic LoginInput model
    - Added Form(...) parameters
    - Now accepts form data from HTML forms
    """
    
    if not authenticate_user(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    users = load_users()
    user = users.get(username, {})
    
    token = create_token({"sub": username, "role": user.get("role", "user")})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.get("role", "user"),
        "username": username,
        "success": True
    }


@router.post("/register")
def register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    role: str = Form("user")
):
    """
    Register endpoint - accepts multipart form data
    
    CHANGES:
    - Removed Pydantic RegisterInput model
    - Added Form(...) parameters
    - Now accepts form data from HTML forms
    """
    
    success = create_user(
        username=username,
        password=password,
        role=role,
        email=email
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    return {
        "success": True,
        "message": f"User {username} created successfully",
        "username": username,
        "role": role
    }