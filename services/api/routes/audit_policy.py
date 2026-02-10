from fastapi import APIRouter, Query
from pathlib import Path
import yaml

router = APIRouter(prefix="/audit", tags=["audit"])

BASE_DIR = Path(__file__).resolve().parents[4]
AUDIT_LOG = BASE_DIR / "policy_store" / "policy_audit.log"


@router.get("/policy-changes")
def get_policy_changes(limit: int = Query(20, ge=1, le=100)):
    if not AUDIT_LOG.exists():
        return []

    with open(AUDIT_LOG, "r") as f:
        raw = f.read()

    entries = [
        yaml.safe_load(block)
        for block in raw.split("\n---\n")
        if block.strip()
    ]

    return entries[-limit:]
