def verify(req: TransactionRequestIn):
    tx_id = str(uuid.uuid4())

    def decide(status, reason):
        decision = {
            "status": status,
            "reason": reason,
            "tx_id": tx_id,
            "metadata": {
                "merkle": "0x" + secrets.token_hex(16),
                "geo": req.country,
            },
        }
        audit_log[tx_id] = decision
        return decision

    # KILL SWITCH
    if PANIC_MODE:
        return decide("BLOCK", "KILL SWITCH ACTIVE")

    # SANCTIONS
    if req.country in SANCTIONED_COUNTRIES:
        return decide("BLOCK", f"Sanctioned: {req.country}")

    # VELOCITY
    count = velocity_db.get(req.agent_id, 0)
    if count >= 3:
        return decide("BLOCK", "Velocity Limit")
    velocity_db[req.agent_id] = count + 1

    # PAYMENT ACTIONS → STRICT KERNEL
    if req.action in {"execute_payment", "transfer"}:
        if req.amount is None or req.recipient is None:
            raise HTTPException(
                status_code=422,
                detail="amount and recipient required for payment actions",
            )

        kernel_req = TransactionRequest(
            action=req.action,
            amount=req.amount,
            recipient=req.recipient,
            agent_id=req.agent_id,
            country=req.country,
        )

        if kernel_req.amount > 10000:
            return decide("BLOCK", "Amount Limit")

    return decide("ALLOW", "Safe")

# ============================
# Health check endpoint
# ============================
from datetime import datetime

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "galani-api",
        "mode": "pilot",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# ============================
# Pilot API Key Authentication
# ============================
from fastapi import Header, HTTPException

PILOT_API_KEYS = {
    "pilot_acme_001",
    "pilot_kaggle_002",
    "pilot_demo_003",
}

def require_api_key(x_api_key: str = Header(None)):
    if x_api_key not in PILOT_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
@app.post("/api/v1/shadow_verify")
def verify(
    req: TransactionRequestIn,
    x_api_key: str = Header(None)
):
    require_api_key(x_api_key)

    tx_id = str(uuid.uuid4())

    def decide(status, reason):
        decision = {
            "status": status,
            "reason": reason,
            "tx_id": tx_id,
            "metadata": {
                "merkle": "0x" + secrets.token_hex(16),
                "geo": req.country,
            },
        }
        audit_log[tx_id] = decision
        return decision

    # KILL SWITCH
    if PANIC_MODE:
        return decide("BLOCK", "KILL SWITCH ACTIVE")

    # SANCTIONS
    if req.country in SANCTIONED_COUNTRIES:
        return decide("BLOCK", f"Sanctioned: {req.country}")

    # VELOCITY
    count = velocity_db.get(req.agent_id, 0)
    if count >= 3:
        return decide("BLOCK", "Velocity Limit")
    velocity_db[req.agent_id] = count + 1

    # PAYMENT ACTIONS → STRICT KERNEL
    if req.action in {"execute_payment", "transfer"}:
        if req.amount is None or req.recipient is None:
            raise HTTPException(
                status_code=422,
                detail="amount and recipient required for payment actions",
            )

        kernel_req = TransactionRequest(
            action=req.action,
            amount=req.amount,
            recipient=req.recipient,
            agent_id=req.agent_id,
            country=req.country,
        )

        if kernel_req.amount > 10000:
            return decide("BLOCK", "Amount Limit")

    return decide("ALLOW", "Safe")
