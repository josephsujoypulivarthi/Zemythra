from fastapi import FastAPI
from .api import router

app = FastAPI(
    title="Zemythra Backend",
    version="1.0"
)

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
