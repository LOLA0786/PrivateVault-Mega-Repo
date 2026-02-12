from pathlib import Path
import yaml
from threading import RLock

BASE_DIR = Path(__file__).resolve().parent
POLICY_DIR = BASE_DIR / "policy_store"

_ACTIVE_POLICIES = {}
_POLICY_CACHE = {}
_lock = RLock()


def _load_yaml(path: Path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _get_policy_from_cache(path: Path):
    with _lock:
        if not path.exists():
            return {"policy": {}, "active": False}

        mtime = path.stat().st_mtime
        cached = _POLICY_CACHE.get(path)

        if not cached or cached["mtime"] != mtime:
            _POLICY_CACHE[path] = {
                "mtime": mtime,
                "policy": _load_yaml(path),
            }

        return _POLICY_CACHE[path]["policy"]


# -------------------------------
# Public Stable Surface
# -------------------------------

def load_policy(policy_name: str, tenant_id: str | None = None):
    path = POLICY_DIR / policy_name
    return _get_policy_from_cache(path)


def load_policy_for_tenant(tenant_id: str):
    policy_name = _ACTIVE_POLICIES.get(tenant_id, "default.yaml")
    return load_policy(policy_name)


# ✅ RESTORED FOR BACKWARD COMPATIBILITY
def get_policy(path):
    if isinstance(path, str):
        path = POLICY_DIR / path
    return _get_policy_from_cache(path)


def invalidate_policy_cache(tenant_id: str | None = None):
    _POLICY_CACHE.clear()
