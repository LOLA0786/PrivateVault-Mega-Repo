import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from audit_logger import get_audit_log_paths
from services.api.models import ApprovalRecord

router = APIRouter()


ALLOWLIST = {
    "approval_id",
    "approver_id",
    "role",
    "region",
    "intent_hash",
    "issued_at",
    "expires_at",
    "rule_id",
    "tenant_id",
    "action",
    "timestamp",
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


@router.get("/approvals", response_model=list[ApprovalRecord])
def list_approvals(
    tenant_id: str | None = None,
    start: str | None = None,
    end: str | None = None,
):
    if auth.tenant_id and tenant_id and tenant_id != auth.tenant_id:
        raise HTTPException(status_code=403, detail="TENANT_SCOPE_VIOLATION")

    start_dt = _parse_iso(start) if start else None
    end_dt = _parse_iso(end) if end else None

    approvals: list[dict] = []
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
                    quorum = event.get("quorum") or {}
                    used = quorum.get("approvals_used") or []
                    for approval in used:
                        row = dict(approval)
                        row["rule_id"] = quorum.get("rule_id")
                        row["tenant_id"] = event.get("tenant_id")
                        row["action"] = quorum.get("action")
                        row["timestamp"] = event.get("timestamp")
                        approvals.append(_filter(row))
        except FileNotFoundError:
            continue

    approvals.sort(key=lambda a: (a.get("timestamp", ""), a.get("approval_id") or ""))
    return approvals
