from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import os

from policy_engine import authorize_intent

app = FastAPI(title="PrivateVault Governance Brain")


# ===============================
# Models
# ===============================

class EvaluationRequest(BaseModel):
    tenant_id: str
    action: str
    principal: Dict[str, Any]
    context: Dict[str, Any]


class EvaluationResponse(BaseModel):
    allowed: bool
    policy_version: str | None = None
    risk_score: float | None = None
    reason: str | None = None
    enforcement_type: str = "hard"


# ===============================
# Health Check
# ===============================

@app.get("/health")
def health():
    return {"status": "ok"}


# ===============================
# Policy Evaluation Endpoint
# ===============================

@app.post("/v1/evaluate", response_model=EvaluationResponse)
def evaluate(req: EvaluationRequest):

    decision = authorize_intent(
        action=req.action,
        principal=req.principal,
        context=req.context
    )

    return EvaluationResponse(
        allowed=decision.get("allowed", False),
        policy_version=decision.get("policy_version"),
        risk_score=decision.get("risk_score"),
        reason=decision.get("reason"),
        enforcement_type=decision.get("enforcement_type", "hard")
    )
