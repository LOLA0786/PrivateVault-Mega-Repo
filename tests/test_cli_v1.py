import json
import os
from types import SimpleNamespace

import pytest

from cli import pv
from cli.config import CONFIG_ENV


class DummyResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload


def test_login_writes_config(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "creds.json"
    monkeypatch.setenv(CONFIG_ENV, str(config_path))

    argv = ["login", "--token", "abc", "--api-url", "http://localhost:8000/api/v1"]
    assert pv.main(argv) == 0

    assert config_path.exists()
    data = json.loads(config_path.read_text())
    assert data["token"] == "abc"


def test_status_calls_api(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "creds.json"
    monkeypatch.setenv(CONFIG_ENV, str(config_path))
    config_path.write_text(json.dumps({"api_url": "http://localhost:8000/api/v1", "token": "abc"}))

    called = {}

    def fake_request(method, url, json=None, params=None, headers=None, timeout=None):
        called["method"] = method
        called["url"] = url
        return DummyResponse({"status": "ok", "version": "v1"})

    monkeypatch.setattr("requests.request", fake_request)

    assert pv.main(["status"]) == 0
    assert called["method"] == "GET"
    assert called["url"].endswith("/api/v1/status")
