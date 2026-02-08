import json
import os
import secrets
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


def create_api_key(plan: str, monthly_limit: int | None = None):
    limits = {
        "starter": 10_000,
        "pro": 100_000,
        "enterprise": 1_000_000,
    }

    if plan not in limits:
        raise ValueError("INVALID_PLAN")

    record = {
        "api_key": f"pv_{secrets.token_urlsafe(32)}",
        "plan": plan,
        "monthly_limit": monthly_limit or limits[plan],
        "used": 0,
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


def increment_usage(api_key: str):
    records = _load()
    for r in records:
        if r["api_key"] == api_key:
            r["used"] += 1
            r["last_used_at"] = datetime.utcnow().isoformat()
            _save(records)
            return
