import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Tuple

from fastapi import HTTPException, Request


DEFAULT_MAX_SKEW_SECONDS = 300


def _load_context_keys() -> Dict[str, str]:
    raw = os.getenv("PV_CONTEXT_KEYS", "")
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=500, detail="CONTEXT_KEYSTORE_INVALID")
    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail="CONTEXT_KEYSTORE_INVALID")
    return {str(k): str(v) for k, v in data.items()}


def _get_context_key(key_id: str) -> str:
    keys = _load_context_keys()
    secret = keys.get(key_id)
    if not secret:
        raise HTTPException(status_code=401, detail="CONTEXT_KEY_NOT_FOUND")
    return secret


def compute_request_hash(method: str, path_with_query: str, body: bytes) -> str:
    hasher = hashlib.sha256()
    hasher.update(method.upper().encode("utf-8"))
    hasher.update(b"\n")
    hasher.update(path_with_query.encode("utf-8"))
    hasher.update(b"\n")
    hasher.update(body or b"")
    return hasher.hexdigest()


def _verify_signature(secret: str, context_raw: str, signature: str) -> None:
    expected = hmac.new(secret.encode("utf-8"), context_raw.encode("utf-8"), hashlib.sha256)
    if not hmac.compare_digest(expected.hexdigest(), signature):
        raise HTTPException(status_code=401, detail="CONTEXT_SIGNATURE_INVALID")


def _parse_context(context_raw: str) -> Dict[str, Any]:
    try:
        return json.loads(context_raw)
    except Exception:
        raise HTTPException(status_code=400, detail="CONTEXT_INVALID")


def _assert_required_fields(context: Dict[str, Any]) -> None:
    required = ["actor_id", "tenant_id", "timestamp", "nonce", "request_hash", "key_id"]
    for field in required:
        if not context.get(field):
            raise HTTPException(status_code=401, detail="CONTEXT_MISSING_FIELDS")


def _assert_timestamp_valid(timestamp: Any) -> None:
    try:
        ts = int(timestamp)
    except Exception:
        raise HTTPException(status_code=401, detail="CONTEXT_TIMESTAMP_INVALID")

    max_skew = int(os.getenv("PV_CONTEXT_MAX_SKEW_SECONDS", DEFAULT_MAX_SKEW_SECONDS))
    now = int(time.time())
    if abs(now - ts) > max_skew:
        raise HTTPException(status_code=401, detail="CONTEXT_TIMESTAMP_SKEW")


async def require_signed_context(request: Request) -> Dict[str, Any]:
    context_raw = request.headers.get("X-PV-Context")
    signature = request.headers.get("X-PV-Signature")
    if not context_raw or not signature:
        raise HTTPException(status_code=401, detail="SIGNED_CONTEXT_REQUIRED")

    context = _parse_context(context_raw)
    _assert_required_fields(context)
    _assert_timestamp_valid(context.get("timestamp"))

    secret = _get_context_key(str(context.get("key_id")))
    _verify_signature(secret, context_raw, signature)

    body = await request.body()
    path_with_query = request.url.path
    if request.url.query:
        path_with_query = f"{path_with_query}?{request.url.query}"
    expected_hash = compute_request_hash(request.method, path_with_query, body)
    if context.get("request_hash") != expected_hash:
        raise HTTPException(status_code=401, detail="REQUEST_HASH_MISMATCH")

    request.state.pv_context = context
    return context
