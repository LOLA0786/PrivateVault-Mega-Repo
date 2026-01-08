import uuid, time, secrets
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Galani Emperor Node", version="10.0.0-EMPEROR")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CONFIG
ADMIN_KEY = "galani-emperor-secret-999"
SANCTIONED_COUNTRIES = ["NORTH_KOREA", "UNKNOWN_ISLAND"]

# STATE
velocity_db = {}
audit_log = {}
PANIC_MODE = False

# ───────── INPUT SCHEMA (API ONLY) ─────────
class TransactionRequestIn(BaseModel):
    action: str
    agent_id: str
    country: Optional[str] = "US"
    amount: Optional[float] = None
    recipient: Optional[str] = None


# ───────── KERNEL SCHEMA (STRICT) ─────────
class TransactionRequest(BaseModel):
    action: str
    amount: float
    recipient: str
    agent_id: str
    country: Optional[str] = "US"


class PanicRequest(BaseModel):
    confirm: bool


class PaymentRequest(BaseModel):
    amount: float
    currency: str
    card_last4: str
    agent_id: str


async def verify_admin(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="ACCESS DENIED")
    return x_admin_key


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "Galani_v10_Emperor"}


@app.post("/api/v1/shadow_verify")
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
