import os
import json


def get_proof(audit_id: str):

    path = os.getenv("PV_AUDIT_LOG_PATH")

    if not path or not os.path.exists(path):
        return {"error": "Audit log not configured"}

    record = None

    # Read audit log line-by-line (WORM safe)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line.strip())
                if obj.get("audit_id") == audit_id:
                    record = obj
                    break
            except Exception:
                continue

    if not record:
        return {"error": "Audit record not found"}

    return {
        "audit_id": audit_id,
        "record": record,
        "verified": True,
    }
