import os
import json
from pathlib import Path
from typing import Dict, List

# ------------------------------------------------------------------
# Configurable data directory (12-factor style)
# ------------------------------------------------------------------

DATA_PATH = Path(
    os.getenv("PRIVATEVAULT_DATA_PATH", Path.cwd() / "data")
)

DATA_PATH.mkdir(parents=True, exist_ok=True)

API_KEYS_FILE = DATA_PATH / "api_keys.json"

if not API_KEYS_FILE.exists():
    API_KEYS_FILE.write_text(json.dumps([]))


# ------------------------------------------------------------------
# Storage helpers
# ------------------------------------------------------------------

def _read_keys() -> List[Dict]:
    with open(API_KEYS_FILE, "r") as f:
        return json.load(f)


def _write_keys(keys: List[Dict]):
    with open(API_KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=2)


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def create_api_key(key: str, tenant_id: str):
    keys = _read_keys()
    keys.append({
        "key": key,
        "tenant_id": tenant_id,
    })
    _write_keys(keys)


def list_api_keys() -> List[Dict]:
    return _read_keys()
