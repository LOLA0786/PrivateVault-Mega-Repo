import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from audit_logger import get_audit_log_paths
from services.api.models import AuditEventResponse

router = APIRouter()


ALLOWLIST = {
    "timestamp",
    "event_type",
    "method",
    "path",
    "status_code",
    "decision",
    "latency_ms",
    "actor_id",
    "tenant_id",
    "role",
    "request_hash",
    "quorum",
    "error",
    "client_ip",
}


def _parse_iso(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def _in_range(ts: str, start: datetime | None, end: datetime | None) -> bool:
    try:
        parsed = _parse_iso(ts)
    except Exception:
        return False
    if start and parsed < start:
        return False
    if end and parsed > end:
        return False
    return True


def _filter(event: dict) -> dict:
    return {k: event.get(k) for k in ALLOWLIST if k in event}


@router.get("/audit", response_model=list[AuditEventResponse])
def get_audit(
    tenant_id: str | None = None,
    start: str | None = None,
    end: str | None = None,
):
    if auth.tenant_id and tenant_id and tenant_id != auth.tenant_id:
        raise HTTPException(status_code=403, detail="TENANT_SCOPE_VIOLATION")
    start_dt = _parse_iso(start) if start else None
    end_dt = _parse_iso(end) if end else None

    events = []
    for path in get_audit_log_paths():
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except Exception:
                        continue
                    if tenant_id and event.get("tenant_id") != tenant_id:
                        continue
                    ts = event.get("timestamp")
                    if ts and not _in_range(ts, start_dt, end_dt):
                        continue
                    events.append(_filter(event))
        except FileNotFoundError:
            continue

    events.sort(key=lambda e: e.get("timestamp", ""))
    return events
