from fastapi.testclient import TestClient
from services.api.app import app

client = TestClient(app)


def test_chat_respond_blocked():
    r = client.post(
        "/api/v1/chat/respond",
        headers={"X-API-Key": "test"},
        json={"request_id": "req_1001"},
    )

    assert r.status_code == 200
    body = r.json()
    assert "BLOCKED" in body["message"]
    assert "GDPR_PII_RESTRICTION" in body["message"]
