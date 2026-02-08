from fastapi import FastAPI, Header, HTTPException, Depends
import os

from core_engine.decision import run_decision
from core_engine.proof import get_proof
from core_engine.optimize import run_optimization

app = FastAPI(title="PrivateVault Platform")

API_KEYS = {
    k.strip()
    for k in os.getenv("PRIVATEVAULT_API_KEYS","").split(",")
    if k.strip()
}


def auth(x_api_key: str = Header(None)):
    if x_api_key not in API_KEYS:
        raise HTTPException(401, "Unauthorized")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/decision", dependencies=[Depends(auth)])
def decision(payload: dict):
    return run_decision(payload)


@app.get("/v1/proof/{audit_id}", dependencies=[Depends(auth)])
def proof(audit_id: str):
    return get_proof(audit_id)


@app.post("/v1/optimize", dependencies=[Depends(auth)])
def optimize(payload: dict):
    return run_optimization(payload)
