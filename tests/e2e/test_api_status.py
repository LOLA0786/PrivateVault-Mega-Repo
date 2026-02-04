from fastapi.testclient import TestClient

from services.api.app import create_app


def test_api_status_e2e():
    client = TestClient(create_app())
    resp = client.get("/api/v1/status")
    assert resp.status_code == 200
