import time
import json
import hashlib
from shadow_mode import shadow_evaluate

def execute_and_log(intent: dict):
    intent_hash = hashlib.sha256(
        json.dumps(intent, sort_keys=True).encode()
    ).hexdigest()

    intent["intent_hash"] = intent_hash

    # ---- REAL decision (production) ----
    decision = "ALLOW"
    policy = "NONE"

    if intent["domain"] == "fintech" and intent.get("amount", 0) >= 200000:
        decision = "BLOCK"
        policy = "FINTECH_v1.0"

    real_allowed = decision == "ALLOW"

    # ---- SHADOW decision ----
    shadow = shadow_evaluate(intent)

    record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "domain": intent["domain"],
        "actor": intent.get("actor"),
        "action": intent.get("action"),
        "mode": intent.get("mode"),
        "amount": intent.get("amount"),
        "decision": decision,
        "policy": policy,
        "allowed": real_allowed,
        "shadow_decision": shadow,
        "shadow_diff": shadow["allowed"] != real_allowed,
        "intent_hash": intent_hash,
    }

    with open("audit.log", "a") as f:
        f.write(json.dumps(record) + "\n")

    return record
