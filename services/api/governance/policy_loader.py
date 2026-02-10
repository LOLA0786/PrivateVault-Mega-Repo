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
