from fastapi import FastAPI

app = FastAPI(
    title="Zemythra – Clinical Intelligence System",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {"status": "ok"}
