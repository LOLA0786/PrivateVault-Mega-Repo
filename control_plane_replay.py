import json
import os

from audit_logger import get_audit_log_paths


def replay_from_audit(intent_hash: str):
    log_paths = get_audit_log_paths()
    for path in log_paths:
        if not os.path.exists(path):
            continue

        with open(path, "r") as f:
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
                    "raw": entry,
                }

    return {"error": "Intent not found in audit log", "intent_hash": intent_hash}
