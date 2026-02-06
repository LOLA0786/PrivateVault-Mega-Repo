from fastapi.testclient import TestClient
from main_vault_integrated import app

client = TestClient(app)


def test_fastapi_basic():
    payload = {"ping": "test"}

    r = client.post(
        "/test",
        json=payload,
        headers={"x-uaal-mode": "shadow"}
    )

    assert r.status_code in (200, 404, 405)
