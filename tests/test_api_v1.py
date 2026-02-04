import hashlib
import hmac
import json
import os

import pytest
from fastapi.testclient import TestClient

from services.api.app import create_app


def _sign(secret: str, payload: str) -> str:
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


@pytest.fixture(autouse=True)
def _env_setup(tmp_path, monkeypatch):
    tokens = [
        {
            "token": "token-admin",
            "scopes": ["tenant:read", "tenant:write", "quorum:read", "audit:read"],
        },
        {
            "token": "token-tenant",
            "scopes": ["tenant:read", "quorum:read", "audit:read"],
            "tenant_id": "tenant-1",
        },
    ]
    monkeypatch.setenv("PV_SERVICE_TOKENS", json.dumps(tokens))
    monkeypatch.setenv("PV_CONTEXT_KEYS", json.dumps({"k1": "secret-1"}))

    audit_path = tmp_path / "audit.log"
    audit_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-02-01T00:00:00Z",
                "event_type": "control_plane_request",
                "method": "GET",
                "path": "/api/v1/status",
                "status_code": 200,
                "decision": "ALLOW",
                "latency_ms": 1,
                "tenant_id": "tenant-1",
            }
        )
        + "\n"
    )
    monkeypatch.setenv("PV_AUDIT_LOG_PATH", str(audit_path))
    yield


def _client():
    return TestClient(create_app())


def test_status_health_public():
    client = _client()
    assert client.get("/api/v1/status").status_code == 200
    assert client.get("/api/v1/health").status_code == 200


def test_auth_required():
    client = _client()
    resp = client.get("/api/v1/tenants")
    assert resp.status_code == 401


def test_tenant_crud():
    client = _client()
    headers = {"Authorization": "Bearer token-admin"}
    create = client.post(
        "/api/v1/tenants",
        headers=headers,
        json={"tenant_id": "tenant-1", "name": "Acme"},
    )
    assert create.status_code == 200

    get = client.get("/api/v1/tenants/tenant-1", headers=headers)
    assert get.status_code == 200
    assert get.json()["tenant_id"] == "tenant-1"


def test_tenant_scope_enforced():
    client = _client()
    headers = {"Authorization": "Bearer token-admin"}
    client.post(
        "/api/v1/tenants",
        headers=headers,
        json={"tenant_id": "tenant-1", "name": "Acme"},
    )

    tenant_headers = {"Authorization": "Bearer token-tenant"}
    resp = client.get("/api/v1/tenants/tenant-2", headers=tenant_headers)
    assert resp.status_code == 403


def test_quorum_validate():
    client = _client()
    headers = {"Authorization": "Bearer token-admin"}
    payload = {"amount": 1}
    intent_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    approvals = [
        {
            "approval_id": "APP-1",
            "approver_id": "approver-1",
            "role": "CRO",
            "region": "US",
            "key_id": "k1",
            "signature": _sign("secret-1", intent_hash),
            "intent_hash": intent_hash,
        },
        {
            "approval_id": "APP-2",
            "approver_id": "approver-2",
            "role": "Legal",
            "region": "EU",
            "key_id": "k1",
            "signature": _sign("secret-1", intent_hash),
            "intent_hash": intent_hash,
        },
    ]
    resp = client.post(
        "/api/v1/quorum/validate",
        headers=headers,
        json={"action": "POST /api/emit/fintech", "payload": payload, "approvals": approvals},
    )
    assert resp.status_code == 200
    assert resp.json()["approved"] >= 2


def test_audit_read():
    client = _client()
    headers = {"Authorization": "Bearer token-admin"}
    resp = client.get("/api/v1/audit", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
