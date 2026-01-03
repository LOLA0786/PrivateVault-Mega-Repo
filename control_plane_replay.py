import json
import os

AUDIT_LOG_PATH = "audit.log"

def replay_from_audit(intent_hash: str):
    if not os.path.exists(AUDIT_LOG_PATH):
        return {
            "error": "audit.log not found",
            "intent_hash": intent_hash
        }

    with open(AUDIT_LOG_PATH, "r") as f:
        lines = f.readlines()

    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except Exception:
            continue

        if entry.get("intent_hash") == intent_hash:
            return {
                "intent_hash": intent_hash,
                "timestamp": entry.get("timestamp"),
                "domain": entry.get("domain"),
                "actor": entry.get("actor"),
                "action": entry.get("action"),
                "decision": entry.get("decision"),
                "policy": entry.get("policy"),
                "mode": entry.get("mode"),
                "evidence": entry.get("evidence", {}),
                "raw": entry
            }

    return {
        "error": "Intent not found in audit log",
        "intent_hash": intent_hash
    }
