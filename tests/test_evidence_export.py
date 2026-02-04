import json
import os
from datetime import datetime, timezone, timedelta

import pytest

from evidence_export import export_bundle


def _ts(offset_seconds: int = 0) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)).replace(
        microsecond=0
    ).isoformat()


@pytest.fixture(autouse=True)
def _env_setup(tmp_path, monkeypatch):
    export_root = tmp_path / "exports"
    audit_path = tmp_path / "audit.log"
    monkeypatch.setenv("PV_EXPORT_ROOT", str(export_root))
    monkeypatch.setenv("PV_AUDIT_LOG_PATH", str(audit_path))
    monkeypatch.setenv("PV_DECISION_LEDGER_PATH", str(tmp_path / "missing_ledger.jsonl"))
    yield


def test_export_bundle_creates_files(tmp_path):
    audit_path = os.getenv("PV_AUDIT_LOG_PATH")
    events = [
        {
            "timestamp": "2026-02-01T00:00:00+00:00",
            "event_type": "control_plane_request",
            "method": "POST",
            "path": "/api/emit/fintech",
            "status_code": 200,
            "decision": "ALLOW",
            "latency_ms": 5,
            "actor_id": "user-1",
            "tenant_id": "tenant-1",
            "role": "admin",
            "request_hash": "abc",
            "quorum": {
                "rule_id": "tenant-1-fintech",
                "action": "POST /api/emit/fintech",
                "approvals_used": [
                    {
                        "approval_id": "APP-1",
                        "approver_id": "approver-1",
                        "role": "CRO",
                        "region": "US",
                        "intent_hash": "ih",
                        "issued_at": 1736000000,
                        "expires_at": 1736003600,
                    }
                ],
            },
            "token": "should-not-export",
        }
    ]
    with open(audit_path, "w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")

    result = export_bundle(
        tenant_id="tenant-1",
        start_iso="2026-01-01T00:00:00+00:00",
        end_iso="2026-02-02T00:00:00+00:00",
        bundle_name="bundle-1",
    )

    bundle_path = result.bundle_path
    assert os.path.exists(os.path.join(bundle_path, "manifest.json"))
    assert os.path.exists(os.path.join(bundle_path, "audit_logs.jsonl"))
    assert os.path.exists(os.path.join(bundle_path, "approvals.jsonl"))
    assert os.path.exists(os.path.join(bundle_path, "evidence.json"))

    with open(os.path.join(bundle_path, "audit_logs.jsonl"), "r", encoding="utf-8") as f:
        row = json.loads(f.readline())
    assert "token" not in row


def test_export_enforces_root():
    with pytest.raises(RuntimeError):
        export_bundle(
            tenant_id="tenant-1",
            start_iso="2026-01-01T00:00:00+00:00",
            end_iso="2026-02-02T00:00:00+00:00",
            bundle_name="../escape",
        )


def test_decision_ledger_missing_sets_warning():
    result = export_bundle(
        tenant_id="tenant-1",
        start_iso="2026-01-01T00:00:00+00:00",
        end_iso="2026-02-02T00:00:00+00:00",
        bundle_name="bundle-ledger",
    )
    assert "DECISION_LEDGER_MISSING" in result.warnings
