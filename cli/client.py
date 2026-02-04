import json
from typing import Any, Optional

import requests

from cli.config import CLIConfig


class APIClient:
    def __init__(self, config: CLIConfig):
        self.config = config

    def request(self, method: str, path: str, json_body: Optional[dict] = None, params=None):
        if not path.startswith("/"):
            path = "/" + path
        url = self.config.api_url.rstrip("/") + path
        headers = {"Accept": "application/json"}
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        response = requests.request(method, url, json=json_body, params=params, headers=headers, timeout=30)
        return response
