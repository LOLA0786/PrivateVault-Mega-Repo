from fastapi import FastAPI
import requests

app = FastAPI(title="PrivateIntent OS")

INTENT_ENGINE = "http://localhost:8000"
PRIVATE_VAULT = "http://localhost:8001"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/execute")
def execute(payload: dict):
    decision = requests.post(f"{INTENT_ENGINE}/authorize-intent", json=payload).json()

    if not decision.get("allowed"):
        return {
            "status": "BLOCKED",
            "reason": decision.get("reason"),
            "policy": decision.get("policy_version"),
            "evidence": decision.get("evidence_id"),
        }

    result = requests.post(f"{PRIVATE_VAULT}/vault/secure-action", json=payload).json()

    return {
        "status": "EXECUTED",
        "vault_result": result,
        "evidence": decision.get("evidence_id"),
    }
