import json
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

import requests


AuditHook = Callable[[str, Dict[str, Any]], None]


@dataclass
class ConnectorConfig:
    base_url: str
    timeout_seconds: int
    max_retries: int
    model: str


class VaultAuthProvider:
    def __init__(self, env_key: str = "PV_OPENAI_API_KEY"):
        self.env_key = env_key

    def get_credentials(self) -> Dict[str, str]:
        token = os.getenv(self.env_key)
        if not token:
            raise RuntimeError("OPENAI_API_KEY_MISSING")
        return {"api_key": token}


class OpenAIConnector:
    id = "pv.ai.openai"
    domain = "ai"
    version = "1.0.0"

    def __init__(
        self,
        config: Optional[ConnectorConfig] = None,
        auth_provider: Optional[VaultAuthProvider] = None,
        audit_hook: Optional[AuditHook] = None,
    ):
        self.config = config or self._load_config()
        self.auth_provider = auth_provider or VaultAuthProvider()
        self.audit_hook = audit_hook

    def capabilities(self):
        return ["model_invoke", "tool_call"]

    def validate(self, context: Dict[str, Any], action: str) -> None:
        if not context.get("tenant_id"):
            raise ValueError("TENANT_REQUIRED")
        if not context.get("actor_id"):
            raise ValueError("ACTOR_REQUIRED")
        if action not in self.capabilities():
            raise ValueError("ACTION_NOT_SUPPORTED")

    def execute(self, context: Dict[str, Any], action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.validate(context, action)
        self._audit("request", {"action": action, "tenant_id": context.get("tenant_id")})

        if not context.get("quorum"):
            self._audit("error", {"error": "QUORUM_REQUIRED"})
            raise RuntimeError("QUORUM_REQUIRED")

        credentials = self.auth_provider.get_credentials()
        headers = {
            "Authorization": f"Bearer {credentials['api_key']}",
            "Content-Type": "application/json",
        }
        data = dict(payload)
        if "model" not in data:
            data["model"] = self.config.model

        url = f"{self.config.base_url}/chat/completions"
        response = self._request_with_retry(url, headers, data)
        if not response.ok:
            self._audit("error", {"status": response.status_code, "body": response.text})
            response.raise_for_status()

        result = response.json()
        self._audit("execution", {"status": response.status_code})
        return result

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "connector": self.id}

    def _request_with_retry(self, url: str, headers: Dict[str, str], payload: Dict[str, Any]):
        last_exc = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=self.config.timeout_seconds,
                )
                if response.status_code in (429, 500, 502, 503, 504) and attempt < self.config.max_retries:
                    time.sleep(0.25 * (2 ** (attempt - 1)))
                    continue
                return response
            except requests.RequestException as exc:
                last_exc = exc
                if attempt >= self.config.max_retries:
                    raise
                time.sleep(0.25 * (2 ** (attempt - 1)))
        if last_exc:
            raise last_exc

    def _audit(self, event: str, payload: Dict[str, Any]) -> None:
        if self.audit_hook:
            self.audit_hook(event, payload)

    @staticmethod
    def _load_config() -> ConnectorConfig:
        defaults_path = os.path.join(
            os.path.dirname(__file__), "config", "openai.defaults.json"
        )
        with open(defaults_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return ConnectorConfig(
            base_url=raw.get("base_url"),
            timeout_seconds=int(raw.get("timeout_seconds", 30)),
            max_retries=int(raw.get("max_retries", 3)),
            model=raw.get("model", "gpt-4o-mini"),
        )
