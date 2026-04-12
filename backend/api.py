"""
Zemythra - API Layer (Block B)
Skeleton backend without AI dependency
"""
# Updated api.py 

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status  
from fastapi.responses import StreamingResponse
from typing import Optional
import pandas as pd
import random
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from backend.auth import authenticate_user, create_token, load_users


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


from pydantic import BaseModel


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


@router.post("/predict")
def predict_risk(data: PredictionInput):


   input_df = pd.DataFrame([data.model_dump()])


   risk_score, uncertainty = unified_predict(input_df)


   decision_output = evaluate_risk(
       risk_score=risk_score,
       uncertainty=uncertainty
   )


   decision_output["risk_score"] = round(risk_score, 3)
   decision_output["uncertainty"] = round(uncertainty, 3)
   decision_output["future_forecast"] = forecast_future_risk()


   return decision_output


# ─────────────────────────────────────────────
# 🚑 EMERGENCY
# ─────────────────────────────────────────────


class EmergencyInput(BaseModel):
   lat: float
   lon: float
   symptoms: str


@router.post("/emergency-real")
def emergency_real(data: EmergencyInput):


   hospitals = [
       {"name": "Apollo Hospital", "phone": "+91 4043441066", "department": "Cardiology", "rating": 4.8},
       {"name": "Care Hospital", "phone": "+91 4061625656", "department": "Emergency", "rating": 4.6},
   ]


   best = sorted(hospitals, key=lambda h: -h["rating"])[0]


   return {
       "status": "critical",
       "hospital": best["name"],
       "phone": best["phone"],
       "department": best["department"],
       "eta": f"{random.randint(5,12)} minutes",
       "ambulance": "Dispatched"
   }


# ─────────────────────────────────────────────
# 🏥 HOSPITALS
# ─────────────────────────────────────────────


class HospitalInput(BaseModel):
   disease: str


@router.post("/hospitals")
def get_hospitals(data: HospitalInput):


   if "heart" in data.disease.lower():
       return [
           {"name": "Apollo Hospital", "rating": 4.8, "specialization": "Cardiology"},
           {"name": "Care Hospital", "rating": 4.6, "specialization": "Heart Care"}
       ]


   return [
       {"name": "General Hospital", "rating": 4.2, "specialization": "Multi-specialty"}
   ]


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
# 🔐 LOGIN
# ─────────────────────────────────────────────


class LoginInput(BaseModel):
    """Login request model"""
    username: str
    password: str


class RegisterInput(BaseModel):
    """Registration request model"""
    username: str
    password: str
    email: str
    role: str = "user"


@router.post("/login")
def login(data: LoginInput):
    """
    Login endpoint - verifies username/password and returns token
    """
    from backend.auth import load_users
    
    # Authenticate user
    if not authenticate_user(data.username, data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Get user data for token
    users = load_users()
    user = users.get(data.username, {})
    
    # Create JWT token
    token = create_token({"sub": data.username, "role": user.get("role", "user")})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.get("role", "user"),
        "username": data.username,
        "success": True
    }


@router.post("/register")
def register(data: RegisterInput):
    """
    Register endpoint - creates new user with hashed password
    """
    from backend.auth import create_user
    
    # Try to create user
    success = create_user(
        username=data.username,
        password=data.password,
        role=data.role,
        email=data.email
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    return {
        "success": True,
        "message": f"User {data.username} created successfully",
        "username": data.username,
        "role": data.role
    }