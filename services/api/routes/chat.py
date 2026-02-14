from services.api.security.replay_guard import guard_replay

from fastapi import Request

from services.api.security.cometchat_verify import verify_cometchat_signature


from services.api.governance.policy_engine import evaluate_policy

from services.api.governance.policy_loader import load_policy_for_tenant
from services.ai_client import classify_message


from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime

from services.api.governance.normalizer import normalize
from services.api.governance.policy_loader import load_policy
from services.ai_client import classify_message
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

    # --- AI Governance Layer (Pre-check) ---
    try:
        ai_result = classify_message(
            message=payload.message or "",
            tenant_id=tenant_id,
            user_id="unknown"
        )

        if ai_result["governance"]["policy"]["action"] == "BLOCK":
            return {
                "message": "❌ BLOCKED by AI Governance Layer",
                "ai_decision": ai_result
            }
    except Exception:
        # Fail-open (AI outage should not break Mega)
        pass

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

    # --- AI Governance Layer (Pre-check) ---
    try:
        ai_result = classify_message(
            message=payload.message or "",
            tenant_id=tenant_id,
            user_id="unknown"
        )

        if ai_result["governance"]["policy"]["action"] == "BLOCK":
            return {
                "message": "❌ BLOCKED by AI Governance Layer",
                "ai_decision": ai_result
            }
    except Exception:
        # Fail-open (AI outage should not break Mega)
        pass

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

@router.post("/chat/respond")
async def chat_respond(request: Request, payload: dict):
    tenant_id = getattr(request.state, "tenant_id", "default")

    # --- AI Governance Layer (Pre-check) ---
    try:
        ai_result = classify_message(
            message=payload.message or "",
            tenant_id=tenant_id,
            user_id="unknown"
        )

        if ai_result["governance"]["policy"]["action"] == "BLOCK":
            return {
                "message": "❌ BLOCKED by AI Governance Layer",
                "ai_decision": ai_result
            }
    except Exception:
        # Fail-open (AI outage should not break Mega)
        pass

    policy = load_policy_for_tenant(tenant_id)
    decision = evaluate_policy(
        message=payload.get("message", ""),
        policy=policy,
        context={"request_id": payload.get("request_id")}
    )

    # SHADOW / MONITOR MODE
    if decision["action"] == "BLOCK" and policy["mode"] in ("monitor", "shadow"):
        return {
            "message": "⚠️ Policy violation (not enforced)",
            "decision": decision,
            "shadow": True
        }

    # STRICT MODE
    if decision["action"] == "BLOCK":
        return {
            "message": "❌ Message blocked by governance policy",
            "decision": decision,
            "shadow": False
        }

    return {
        "message": "✅ Allowed",
        "decision": decision
    }

@router.post("/chat/webhook/cometchat")
async def cometchat_webhook(request: Request):
    body = await request.body()

    # 🔐 Verify CometChat signature
    verify_cometchat_signature(request, body)


    event = await request.json()

    message = event.get("data", {}).get("text", "")

    tenant_id = event.get("data", {}).get("receiver", "default")
    policy = load_policy_for_tenant(tenant_id)

    decision = evaluate_policy(
        message=message,
        policy=policy,
        context={"source": "cometchat"}
    )

    return {
        "status": "processed",
        "decision": decision
    }

@router.post("/chat/webhook/cometchat")
async def cometchat_webhook(request: Request):
    body = await request.body()

    # 🔐 Verify CometChat signature
    verify_cometchat_signature(request, body)

    event = await request.json()

    # 🔁 Replay protection
    event_id = event.get("id") or event.get("data", {}).get("id")
    if event_id:
        guard_replay(event_id)

    message = event.get("data", {}).get("text", "")
    tenant_id = event.get("data", {}).get("receiver", "default")

    policy = load_policy_for_tenant(tenant_id)
    decision = evaluate_policy(
        message=message,
        policy=policy,
        context={"source": "cometchat"}
    )

    return {
        "status": "processed",
        "decision": decision
    }
