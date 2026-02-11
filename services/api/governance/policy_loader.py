from pathlib import Path
import yaml
from threading import RLock

# ----------------------------------
# Config
# ----------------------------------

BASE_DIR = Path(__file__).resolve().parent
POLICY_DIR = BASE_DIR / "policy_store"

_ACTIVE_POLICIES = {}
_POLICY_CACHE = {}
_lock = RLock()

# ----------------------------------
# Internal loader
# ----------------------------------

def _load_yaml(path: Path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def _get_policy_from_cache(path: Path):
    with _lock:
        mtime = path.stat().st_mtime
        cached = _POLICY_CACHE.get(path)

        if not cached or cached["mtime"] != mtime:
            _POLICY_CACHE[path] = {
                "mtime": mtime,
                "policy": _load_yaml(path),
            }

        return _POLICY_CACHE[path]["policy"]

# ----------------------------------
# Public API (Stable Surface)
# ----------------------------------

def load_policy(policy_name: str, tenant_id: str | None = None):
    """
    Stable public loader.
    Accepts policy filename like 'default.yaml'
    """
    path = POLICY_DIR / policy_name
    return _get_policy_from_cache(path)

def load_policy_for_tenant(tenant_id: str):
    """
    Load active policy for tenant.
    Defaults to default.yaml
    """
    policy_name = _ACTIVE_POLICIES.get(tenant_id, "default.yaml")
    return load_policy(policy_name)

def get_policy(path):
    """
    Backward compatibility shim.
    """
    if isinstance(path, str):
        path = POLICY_DIR / path
    return _get_policy_from_cache(path)

def invalidate_policy_cache(tenant_id: str | None = None):
    global _POLICY_CACHE
    if tenant_id:
        # simple clear — safe for now
        _POLICY_CACHE.clear()
    else:
        _POLICY_CACHE.clear()
