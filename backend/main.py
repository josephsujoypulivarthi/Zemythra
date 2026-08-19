from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.db import init_db
from .api import router
from backend.chat_service import warmup_model

# Import the auth functions from auth.py
from .auth import authenticate_user, create_token, register_new_user

init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up — warming Ollama model...")
    warmup_model()
    yield
    print("🛑 Shutting down...")

app = FastAPI(
    lifespan=lifespan,
    title="Zemythra Backend",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🚨 AUTH ROUTES (Moved ABOVE the router!) 🚨
# This forces FastAPI to use these instead of api.py
# ==========================================

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

@app.post("/login")
def login(request: LoginRequest):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_token(data={"sub": user["email"], "role": user["role"]})
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user["role"]
    }

@app.post("/register")
def register(request: RegisterRequest):
    success = register_new_user(request.name, request.email, request.password)
    if not success:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return {"message": "User created successfully"}

# ==========================================
# Include other routes AFTER our login routes
# ==========================================
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}