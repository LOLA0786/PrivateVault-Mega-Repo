import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


DEFAULT_AUDIT_LOG_PATH = "/var/lib/privatevault/audit.log"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _repo_root() -> str:
    return os.getenv("PV_REPO_ROOT", os.getcwd())


def _assert_path_not_in_repo(path: str) -> None:
    repo_root = os.path.realpath(_repo_root())
    real_path = os.path.realpath(path)
    if real_path == repo_root or real_path.startswith(repo_root + os.sep):
        raise RuntimeError(
            "Audit log path must not be inside the repo. "
            "Set PV_AUDIT_LOG_PATH to a non-repo location."
        )


def get_audit_log_path() -> str:
    return os.getenv("PV_AUDIT_LOG_PATH", DEFAULT_AUDIT_LOG_PATH)


def get_audit_log_paths() -> List[str]:
    raw = os.getenv("PV_AUDIT_LOG_PATHS")
    if raw:
        paths = [p.strip() for p in raw.split(",") if p.strip()]
    else:
        paths = [get_audit_log_path()]
    for path in paths:
        _assert_path_not_in_repo(path)
    return paths


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def log_audit_event(event: Dict[str, Any]) -> None:
    path = get_audit_log_path()
    _assert_path_not_in_repo(path)
    _ensure_parent_dir(path)
    payload = dict(event)
    payload.setdefault("timestamp", _utc_now_iso())
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")
        f.flush()
        os.fsync(f.fileno())


def build_request_audit_event(
    *,
    method: str,
    path: str,
    status_code: int,
    decision: str,
    latency_ms: int,
    context: Optional[Dict[str, Any]] = None,
    quorum: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    client_ip: Optional[str] = None,
) -> Dict[str, Any]:
    event = {
        "event_type": "control_plane_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "decision": decision,
        "latency_ms": latency_ms,
    }
    if context:
        event.update(
            {
                "actor_id": context.get("actor_id"),
                "tenant_id": context.get("tenant_id"),
                "role": context.get("role"),
                "request_hash": context.get("request_hash"),
            }
        )
    if quorum:
        event["quorum"] = quorum
    if error:
        event["error"] = error
    if client_ip:
        event["client_ip"] = client_ip
    return event
