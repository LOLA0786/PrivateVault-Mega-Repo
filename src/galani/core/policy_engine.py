import uuid
import time


def authorize_intent(intent: dict):
    """
    Deterministic policy enforcement.
    NO randomness. NO models. NO side effects.
    """

    action = intent.get("action")
    args = intent.get("args", {})
    context = intent.get("context", {})

    evidence_id = str(uuid.uuid4())
    timestamp = int(time.time())

    # ================================
    # FINTECH POLICY — HARD INVARIANT
    # ================================
    if action == "transfer_money":
        amount = args.get("amount", 0)
        jurisdiction = context.get("jurisdiction")

        if jurisdiction == "IN" and amount >= 100000:
            return {
                "allowed": False,
                "decision": "BLOCK",
                "reason": "High-value transfer blocked by policy",
                "policy_version": "fintech-v1.0",
                "evidence_id": evidence_id,
                "timestamp": timestamp
            }

    # ================================
    # MEDTECH POLICY — HARD INVARIANT
    # ================================
    if action == "prescribe_medication":
        patient_age = context.get("patient_age", 0)
        consent = context.get("consent", False)

        if patient_age < 18 and consent is False:
            return {
                "allowed": False,
                "decision": "BLOCK",
                "reason": "Minor prescription without consent",
                "policy_version": "medtech-v1.0",
                "evidence_id": evidence_id,
                "timestamp": timestamp
            }

    # ================================
    # DEFAULT ALLOW
    # ================================
    return {
        "allowed": True,
        "decision": "ALLOW",
        "reason": "Allowed by policy",
        "policy_version": "default-v1.0",
        "evidence_id": evidence_id,
        "timestamp": timestamp
    }
