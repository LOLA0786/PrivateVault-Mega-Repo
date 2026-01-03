import time
import hashlib
import json

def execute_and_log(intent: dict):
    try:
        intent_hash = hashlib.sha256(
            json.dumps(intent, sort_keys=True).encode()
        ).hexdigest()

        decision = "ALLOW"
        policy = "NONE"

        # VERY SIMPLE DEMO RULES (NO CRASH)
        if intent["domain"] == "fintech" and intent.get("amount", 0) >= 200000:
            decision = "BLOCK"
            policy = "FINTECH_v1.0"

        if intent["domain"] == "medtech" and intent.get("patient_age", 99) < 18:
            decision = "BLOCK"
            policy = "MEDTECH_v2.1"

        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "domain": intent["domain"],
            "actor": intent.get("actor"),
            "action": intent.get("action"),
            "mode": intent.get("mode"),
            "decision": decision,
            "policy": policy,
            "intent_hash": intent_hash,
        }

        # append audit safely
        with open("audit.log", "a") as f:
            f.write(json.dumps(record) + "\n")

        return record

    except Exception as e:
        return {
            "decision": "ERROR",
            "error": str(e)
        }
