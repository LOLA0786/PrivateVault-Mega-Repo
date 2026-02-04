import json
import os
from dataclasses import dataclass
from typing import Optional


DEFAULT_API_URL = "http://localhost:8000/api/v1"
CONFIG_ENV = "PV_CLI_CONFIG"


@dataclass
class CLIConfig:
    api_url: str
    token: Optional[str]


def _config_path() -> str:
    override = os.getenv(CONFIG_ENV)
    if override:
        return override
    home = os.path.expanduser("~")
    return os.path.join(home, ".privatevault", "credentials.json")


def load_config() -> CLIConfig:
    path = _config_path()
    if not os.path.exists(path):
        return CLIConfig(api_url=os.getenv("PV_API_URL", DEFAULT_API_URL), token=None)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    api_url = data.get("api_url") or os.getenv("PV_API_URL", DEFAULT_API_URL)
    token = data.get("token")
    return CLIConfig(api_url=api_url, token=token)


def save_config(config: CLIConfig) -> str:
    path = _config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"api_url": config.api_url, "token": config.token}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass
    return path
