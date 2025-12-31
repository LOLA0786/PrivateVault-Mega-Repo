from fastapi import FastAPI
from policy_engine import authorize_intent

app = FastAPI(title="UAAL / Intent Engine")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/authorize-intent")
def authorize(payload: dict):
    return authorize_intent(payload)
