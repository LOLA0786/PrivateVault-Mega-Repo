from fastapi.testclient import TestClient
from services.api.app import app

client = TestClient(app)

def test_no_api_key():
    r = client.get("/api/v1/auth/whoami")
    assert r.status_code == 401

def test_with_api_key():
    r = client.get("/api/v1/auth/whoami", headers={"X-API-Key": "test"})
    assert r.status_code == 200
    assert r.json()["tenant_id"] == "test-tenant"
