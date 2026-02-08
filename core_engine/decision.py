import uuid
import logging
import os

from policy_engine import authorize_intent, infer_risk
from audit_logger import log_audit_event

logger = logging.getLogger("decision")


def run_decision(payload: dict):

    request_id = str(uuid.uuid4())
    audit_id = str(uuid.uuid4())

    action = payload.get("action", "unknown")
    principal = payload.get("principal", {})
    context = payload.get("context", payload)

    # 1️⃣ Policy evaluation
    policy_result = authorize_intent(
        action=action,
        principal=principal,
        context=context,
    )

    # 2️⃣ Risk scoring
    risk_result = infer_risk(
        action=action,
        principal=principal,
        context=context,
    )

    risk_score = float(risk_result.get("risk_score", 0))

    # 3️⃣ Final decision
    decision = "ALLOW"

    if risk_score > 0.7:
        decision = "DENY"

    # 4️⃣ Audit log (immutable)
    event = {
        "audit_id": audit_id,
        "request_id": request_id,
        "action": action,
        "principal": principal,
        "context": context,
        "decision": decision,
        "risk": risk_score,
        "policy": policy_result,
        "service": "privatevault-api",
    }

    log_audit_event(event)

    logger.info(f"Decision={decision} risk={risk_score} audit={audit_id}")

    return {
        "decision": decision,
        "risk": risk_score,
        "policy": policy_result,
        "audit_id": audit_id,
        "confidence": round(1 - risk_score, 2),
    }
