_ACTIVE_POLICIES = {}

import yaml
from pathlib import Path
from threading import RLock

_policy_cache = {}
_lock = RLock()


def load_policy(path: Path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_policy(path: Path):
    with _lock:
        mtime = path.stat().st_mtime
        cached = _policy_cache.get(path)

        if not cached or cached["mtime"] != mtime:
            _policy_cache[path] = {
                "mtime": mtime,
                "policy": load_policy(path),
            }

        return _policy_cache[path]["policy"]

# -------------------------------
# Policy cache + hot reload
# -------------------------------

_POLICY_CACHE = {}

def invalidate_policy_cache(tenant_id: str | None = None):
    """
    Invalidate cached policies.
    If tenant_id is None -> clear all.
    """
    global _POLICY_CACHE
    if tenant_id:
        _POLICY_CACHE.pop(tenant_id, None)
    else:
        _POLICY_CACHE.clear()

# -------------------------------
# Public API
# -------------------------------

def load_policy_for_tenant(tenant_id: str):
    """
    Load active policy for tenant.
    Defaults to 'default.yaml' if not found.
    """
    policy_name = _ACTIVE_POLICIES.get(tenant_id, "default.yaml")
    return load_policy(policy_name, tenant_id=tenant_id)
