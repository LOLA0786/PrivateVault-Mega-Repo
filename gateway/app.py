from fastapi import FastAPI
import requests

from control_plane.governance_guard import enforce_governance, GovernanceBlocked

app = FastAPI(title="PrivateIntent OS")

INTENT_ENGINE = "http://localhost:8000"
PRIVATE_VAULT = "http://localhost:8001"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/execute")
def execute(payload: dict):
    decision = requests.post(
        f"{INTENT_ENGINE}/api/emit/fintech",
        json=payload,
        timeout=10
    ).json()

    if not decision.get("allowed", True):
        return {
            "status": "BLOCKED",
            "reason": decision.get("reason"),
            "evidence": decision.get("evidence_id"),
        }

    result = requests.post(
        f"{PRIVATE_VAULT}/vault/secure-action",
        json=payload,
        timeout=10
    ).json()

    return {
        "status": "EXECUTED",
        "vault_result": result,
        "evidence": decision.get("evidence_id"),
    }
