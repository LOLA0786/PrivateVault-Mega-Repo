from fastapi import APIRouter, Request
from services.api.governance.normalizer import normalize
from services.api.governance.policy_engine import evaluate_policy

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/respond")
async def chat_respond(payload: dict):
    """
    Internal chat governance endpoint
    """
    normalized = normalize(payload)
    decision = evaluate_policy(normalized)

    if decision["blocked"]:
        return {
            "message": (
                "❌ Decision: BLOCKED\n"
                f"📜 Policy: {decision['policy']}\n"
                "🧠 Reason: Policy enforcement\n"
                f"🔐 Evidence Hash: {decision['evidence_hash']}\n"
                f"⏱ Timestamp: {decision['timestamp']}"
            )
        }

    return {"message": "✅ Allowed"}


@router.post("/webhook/cometchat")
async def cometchat_webhook(request: Request):
    """
    CometChat → PrivateVault governance webhook
    """
    payload = await request.json()

    message = payload.get("data", {}).get("text", "")
    sender = payload.get("data", {}).get("sender", "unknown")

    normalized = normalize({
        "source": "cometchat",
        "sender": sender,
        "text": message,
    })

    decision = evaluate_policy(normalized)

    if decision["blocked"]:
        return {
            "action": "BLOCK",
            "policy": decision["policy"],
            "evidence_hash": decision["evidence_hash"],
            "message": "Message blocked by governance policy"
        }

    return {
        "action": "ALLOW",
        "message": message
    }
