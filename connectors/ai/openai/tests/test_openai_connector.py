import json
import os
import sys

import pytest

REPO_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
sys.path.insert(0, REPO_ROOT)

from connectors.ai.openai.connector import OpenAIConnector, ConnectorConfig, VaultAuthProvider


class DummyResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {"ok": True}
        self.text = text
        self.ok = status_code < 400

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("HTTP_ERROR")


class DummyAuth(VaultAuthProvider):
    def __init__(self):
        pass

    def get_credentials(self):
        return {"api_key": "test"}


def test_validate_requires_tenant_actor():
    connector = OpenAIConnector(auth_provider=DummyAuth())
    with pytest.raises(ValueError):
        connector.validate({}, "model_invoke")


def test_execute_requires_quorum(monkeypatch):
    connector = OpenAIConnector(auth_provider=DummyAuth())
    with pytest.raises(RuntimeError):
        connector.execute({"tenant_id": "t1", "actor_id": "a1"}, "model_invoke", {})


def test_execute_calls_openai(monkeypatch):
    connector = OpenAIConnector(auth_provider=DummyAuth())

    def fake_post(url, headers=None, data=None, timeout=None):
        payload = json.loads(data)
        assert payload["model"]
        return DummyResponse()

    monkeypatch.setattr("requests.post", fake_post)
    result = connector.execute(
        {"tenant_id": "t1", "actor_id": "a1", "quorum": {"approved": 2}},
        "model_invoke",
        {"messages": [{"role": "user", "content": "hi"}]},
    )
    assert result["ok"] is True


def test_audit_hook_called(monkeypatch):
    events = []

    def hook(event, payload):
        events.append(event)

    connector = OpenAIConnector(auth_provider=DummyAuth(), audit_hook=hook)

    def fake_post(url, headers=None, data=None, timeout=None):
        return DummyResponse()

    monkeypatch.setattr("requests.post", fake_post)
    connector.execute(
        {"tenant_id": "t1", "actor_id": "a1", "quorum": {"approved": 2}},
        "model_invoke",
        {"messages": [{"role": "user", "content": "hi"}]},
    )

    assert "request" in events
    assert "execution" in events
