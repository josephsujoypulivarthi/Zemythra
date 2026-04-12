# backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from .api import router
from backend.chat_service import warmup_model




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


app.include_router(router)




@app.get("/health")
def health():
    return {"status": "ok"}



