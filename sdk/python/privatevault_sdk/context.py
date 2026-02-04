import hashlib
import hmac
import json
from typing import Dict


def compute_request_hash(method: str, path_with_query: str, body: bytes) -> str:
    hasher = hashlib.sha256()
    hasher.update(method.upper().encode("utf-8"))
    hasher.update(b"\n")
    hasher.update(path_with_query.encode("utf-8"))
    hasher.update(b"\n")
    hasher.update(body or b"")
    return hasher.hexdigest()


def sign_context(context: Dict, secret: str) -> str:
    payload = json.dumps(context, sort_keys=True, separators=(",", ":"))
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
