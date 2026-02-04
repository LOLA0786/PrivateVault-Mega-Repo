import hashlib
import hmac
import json
import time

import sys
import types

import pytest
from fastapi.testclient import TestClient

from intent_binding import canonical_hash
from security_context import compute_request_hash


def _sign(secret: str, payload: str) -> str:
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _build_context_headers(method: str, path: str, body: bytes, key_id: str, secret: str):
    request_hash = compute_request_hash(method, path, body)
    context = {
        "actor_id": "user-1",
        "tenant_id": "tenant-1",
        "role": "admin",
        "timestamp": int(time.time()),
        "nonce": "nonce-1",
        "request_hash": request_hash,
        "key_id": key_id,
    }
    context_raw = json.dumps(context, separators=(",", ":"), sort_keys=True)
    signature = _sign(secret, context_raw)
    return {
        "X-PV-Context": context_raw,
        "X-PV-Signature": signature,
    }


def _build_approval(approver_id: str, key_id: str, secret: str, intent_hash: str):
    return {
        "approver_id": approver_id,
        "key_id": key_id,
        "signature": _sign(secret, intent_hash),
        "intent_hash": intent_hash,
    }


@pytest.fixture(autouse=True)
def _env_setup(tmp_path, monkeypatch):
    audit_path = tmp_path / "audit.log"
    monkeypatch.setenv("PV_AUDIT_LOG_PATH", str(audit_path))
    monkeypatch.setenv("PV_CONTEXT_KEYS", json.dumps({"k1": "secret-1", "k2": "secret-2"}))
    yield


def test_missing_context_rejected():
    from control_plane_api import app

    client = TestClient(app)
    response = client.get("/status")
    assert response.status_code == 401


def test_valid_context_allows_status(tmp_path):
    from control_plane_api import app
    import policy_registry

    policy_registry.get_active_policy_version = lambda: "test"
    client = TestClient(app)
    body = b""
    headers = _build_context_headers("GET", "/status", body, "k1", "secret-1")
    response = client.get("/status", headers=headers)
    assert response.status_code == 200


def test_emit_requires_quorum(monkeypatch):
    from control_plane_api import app
    fake = types.ModuleType("fintech_final_demo")
    fake.run_fintech_intent = lambda payload: {"ok": True}
    sys.modules["fintech_final_demo"] = fake

    client = TestClient(app)
    payload = {"amount": 100, "recipient": "acct-1"}
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    headers = _build_context_headers("POST", "/api/emit/fintech", body, "k1", "secret-1")
    response = client.post(
        "/api/emit/fintech",
        data=body,
        headers={**headers, "Content-Type": "application/json"},
    )
    assert response.status_code == 403


def test_emit_accepts_quorum_and_logs(monkeypatch, tmp_path):
    from control_plane_api import app
    fake = types.ModuleType("fintech_final_demo")
    fake.run_fintech_intent = lambda payload: {"ok": True}
    sys.modules["fintech_final_demo"] = fake

    client = TestClient(app)
    payload = {"amount": 100, "recipient": "acct-1"}
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    intent_hash = canonical_hash(payload)
    approvals = [
        _build_approval("approver-1", "k1", "secret-1", intent_hash),
        _build_approval("approver-2", "k2", "secret-2", intent_hash),
    ]
    headers = _build_context_headers("POST", "/api/emit/fintech", body, "k1", "secret-1")
    headers["X-PV-Approvals"] = json.dumps(approvals, separators=(",", ":"), sort_keys=True)

    response = client.post(
        "/api/emit/fintech",
        data=body,
        headers={**headers, "Content-Type": "application/json"},
    )
    assert response.status_code == 200

    audit_path = tmp_path / "audit.log"
    assert audit_path.exists()
    lines = audit_path.read_text().strip().splitlines()
    assert len(lines) >= 1
    event = json.loads(lines[-1])
    assert event.get("event_type") == "control_plane_request"
    assert event.get("decision") == "ALLOW"
