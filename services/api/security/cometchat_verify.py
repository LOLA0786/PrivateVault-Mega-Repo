import hmac
import hashlib
import os
from fastapi import HTTPException, Request

COMETCHAT_WEBHOOK_SECRET = os.getenv("COMETCHAT_WEBHOOK_SECRET", "dev-secret")

def verify_cometchat_signature(request: Request, body: bytes):
    signature = request.headers.get("X-CometChat-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="MISSING_SIGNATURE")

    expected = hmac.new(
        COMETCHAT_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="INVALID_SIGNATURE")
