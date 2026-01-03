import hashlib
import json
from datetime import datetime, timezone

def freeze_regulation(regulation_payload: dict) -> dict:
    payload = json.dumps(regulation_payload, sort_keys=True)
    return {
        "hash": hashlib.sha256(payload.encode()).hexdigest(),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "payload": regulation_payload
    }
