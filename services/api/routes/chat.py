from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime

from services.api.governance.normalizer import normalize
from services.api.governance.policy_loader import load_policy
from services.api.governance.policy_engine import evaluate_policy

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    request_id: str
    message: str | None = ""


@router.post("/respond")
def chat_respond(payload: ChatRequest, request: Request):
    """
    Internal Chat API (used by UI, agents, tests)
    """
    tenant_id = getattr(request.state, "tenant_id", "default")

    normalized = normalize(payload.message or "")
    policy = load_policy(tenant_id)
    decision = evaluate_policy(normalized, policy)

    if decision["decision"] == "BLOCK":
        return {
            "message": (
                "❌ Decision: BLOCKED\n"
                f"📜 Policy: {decision['policy_id']}\n"
                "🧠 Reason: Policy enforcement\n"
                "🔐 Evidence Hash: 0xabc123\n"
                f"⏱ Timestamp: {datetime.utcnow().isoformat()}Z"
            )
        }

    return {
        "message": "✅ Allowed",
        "decision": decision,
    }


@router.post("/webhook/cometchat")
async def cometchat_webhook(request: Request):
    """
    Webhook endpoint for CometChat
    """
    body = await request.json()

    text = body.get("data", {}).get("text", "")
    tenant_id = getattr(request.state, "tenant_id", "default")

    normalized = normalize(text)
    policy = load_policy(tenant_id)
    decision = evaluate_policy(normalized, policy)

    if decision["decision"] == "BLOCK":
        return {
            "response": {
                "text": "⚠️ Message blocked by governance policy."
            }
        }

    return {
        "response": {
            "text": text
        }
    }

import hmac
import hashlib
from fastapi import Header, HTTPException

def verify_cometchat_signature(
    payload: bytes,
    signature: str,
    secret: str,
):
    expected = hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="INVALID_WEBHOOK_SIGNATURE")

@router.post("/webhook/cometchat")
async def cometchat_webhook(
    request: Request,
    x_cometchat_signature: str = Header(None),
):
    raw_body = await request.body()

    if not x_cometchat_signature:
        raise HTTPException(status_code=400, detail="SIGNATURE_REQUIRED")

    # load from env or vault later
    COMETCHAT_SECRET = "demo-secret"

    verify_cometchat_signature(
        payload=raw_body,
        signature=x_cometchat_signature,
        secret=COMETCHAT_SECRET,
    )

    event = await request.json()

    # normalize + evaluate just like chat/respond
    normalized = normalize_input(event.get("message", ""))
    decision = evaluate_policy(
        tenant_id=getattr(request.state, "tenant_id", "default"),
        normalized_input=normalized,
    )

    return {
        "status": "processed",
        "decision": decision,
    }

import hmac
import hashlib
import time
from fastapi import Header, HTTPException

REPLAY_WINDOW_SECONDS = 300  # 5 minutes
USED_NONCES = set()

def verify_signature(payload: bytes, signature: str, secret: str):
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="INVALID_SIGNATURE")

def prevent_replay(timestamp: int, nonce: str):
    now = int(time.time())
    if abs(now - timestamp) > REPLAY_WINDOW_SECONDS:
        raise HTTPException(status_code=401, detail="STALE_REQUEST")

    key = f"{timestamp}:{nonce}"
    if key in USED_NONCES:
        raise HTTPException(status_code=401, detail="REPLAY_ATTACK")

    USED_NONCES.add(key)

@router.post("/webhook/cometchat")
async def cometchat_webhook(
    request: Request,
    x_cometchat_signature: str = Header(...),
    x_cometchat_timestamp: int = Header(...),
    x_cometchat_nonce: str = Header(...),
):
    raw = await request.body()

    COMETCHAT_SECRET = "demo-secret"  # move to env later

    verify_signature(raw, x_cometchat_signature, COMETCHAT_SECRET)
    prevent_replay(x_cometchat_timestamp, x_cometchat_nonce)

    payload = await request.json()

    normalized = normalize_input(payload.get("message", ""))
    decision = evaluate_policy(
        tenant_id=getattr(request.state, "tenant_id", "default"),
        normalized_input=normalized,
    )

    return {
        "status": "processed",
        "decision": decision,
    }
