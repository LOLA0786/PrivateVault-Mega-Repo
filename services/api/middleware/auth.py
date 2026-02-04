import json
import os
from typing import List, Optional

from fastapi import HTTPException, Request


class AuthContext:
    def __init__(self, token: str, scopes: List[str], tenant_id: Optional[str]):
        self.token = token
        self.scopes = scopes
        self.tenant_id = tenant_id


def _load_tokens():
    raw = os.getenv("PV_SERVICE_TOKENS", "")
    if not raw:
        return []
    try:
        tokens = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=500, detail="SERVICE_TOKENS_INVALID")
    if not isinstance(tokens, list):
        raise HTTPException(status_code=500, detail="SERVICE_TOKENS_INVALID")
    return tokens


def _find_token(token_value: str):
    for token in _load_tokens():
        if isinstance(token, dict) and token.get("token") == token_value:
            return token
    return None


def require_auth(request: Request) -> AuthContext:
    existing = getattr(request.state, "auth", None)
    if existing:
        return existing

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="AUTH_REQUIRED")
    token_value = auth_header.split(" ", 1)[1].strip()
    token = _find_token(token_value)
    if not token:
        raise HTTPException(status_code=401, detail="AUTH_INVALID")
    scopes = token.get("scopes") or []
    if not isinstance(scopes, list):
        raise HTTPException(status_code=500, detail="AUTH_SCOPES_INVALID")
    tenant_id = token.get("tenant_id")
    return AuthContext(token=token_value, scopes=scopes, tenant_id=tenant_id)


def require_scope(auth: AuthContext, scope: str) -> None:
    if scope not in auth.scopes:
        raise HTTPException(status_code=403, detail="SCOPE_REQUIRED")
