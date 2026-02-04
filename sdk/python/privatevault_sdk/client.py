from typing import Optional

import requests

from privatevault_sdk.retries import RetryConfig, backoff_sleep


class Client:
    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        retry: Optional[RetryConfig] = None,
        timeout_seconds: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self._token = token
        self.retry = retry or RetryConfig()
        self.timeout_seconds = timeout_seconds

    def set_token(self, token: str) -> None:
        self._token = token

    def _headers(self, idempotency_key: Optional[str] = None) -> dict:
        headers = {"Accept": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def request(
        self,
        method: str,
        path: str,
        json_body: Optional[dict] = None,
        params: Optional[dict] = None,
        idempotency_key: Optional[str] = None,
    ):
        url = f"{self.base_url}/{path.lstrip('/')}"
        last_exc = None
        for attempt in range(1, self.retry.attempts + 1):
            try:
                response = requests.request(
                    method,
                    url,
                    json=json_body,
                    params=params,
                    headers=self._headers(idempotency_key),
                    timeout=self.timeout_seconds,
                )
                if response.status_code in self.retry.retry_statuses and attempt < self.retry.attempts:
                    backoff_sleep(attempt, self.retry.backoff_seconds)
                    continue
                return response
            except requests.RequestException as exc:
                last_exc = exc
                if attempt >= self.retry.attempts:
                    raise
                backoff_sleep(attempt, self.retry.backoff_seconds)
        if last_exc:
            raise last_exc
