import json
import os
import uuid
from datetime import datetime

DATA_PATH = "/var/lib/privatevault"
API_KEYS_FILE = f"{DATA_PATH}/api_keys.json"

os.makedirs(DATA_PATH, exist_ok=True)

def _load():
    if not os.path.exists(API_KEYS_FILE):
        return []
    with open(API_KEYS_FILE, "r") as f:
        return json.load(f)

def _save(records):
    with open(API_KEYS_FILE, "w") as f:
        json.dump(records, f, indent=2)

def create_api_key(plan: str, monthly_limit: int = 10000):
    api_key = f"pv_{uuid.uuid4().hex}"
    record = {
        "api_key": api_key,
        "plan": plan,
        "monthly_limit": monthly_limit,
        "used": 0,
        "tenant_id": None,
        "created_at": datetime.utcnow().isoformat(),
        "last_used_at": None,
    }
    records = _load()
    records.append(record)
    _save(records)
    return record

def get_api_key_record(api_key: str):
    for r in _load():
        if r["api_key"] == api_key:
            return r
    return None

def bind_tenant(api_key: str):
    records = _load()
    for r in records:
        if r["api_key"] == api_key:
            if not r.get("tenant_id"):
                r["tenant_id"] = f"tenant_{uuid.uuid4().hex[:8]}"
                _save(records)
            return r["tenant_id"]
    return None

def increment_usage(api_key: str):
    records = _load()
    for r in records:
        if r["api_key"] == api_key:
            r["used"] += 1
            r["last_used_at"] = datetime.utcnow().isoformat()
            _save(records)
            return
