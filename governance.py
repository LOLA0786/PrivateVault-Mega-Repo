import uuid, time, secrets
import uuid, time, secrets
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pydantic import BaseModel
from typing import Optional
from typing import Optional


app = FastAPI(title="Galani Emperor Node", version="10.0.0-EMPEROR")
app = FastAPI(title="Galani Emperor Node", version="10.0.0-EMPEROR")
app.add_middleware(
app.add_middleware(
    CORSMiddleware,
    CORSMiddleware,
    allow_origins=["*"],
    allow_origins=["*"],
    allow_methods=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_headers=["*"],
)
)


# CONFIG
# CONFIG
ADMIN_KEY = "galani-emperor-secret-999"
ADMIN_KEY = "galani-emperor-secret-999"
SANCTIONED_COUNTRIES = ["NORTH_KOREA", "UNKNOWN_ISLAND"]
SANCTIONED_COUNTRIES = ["NORTH_KOREA", "UNKNOWN_ISLAND"]


# STATE
# STATE
velocity_db = {}
velocity_db = {}
audit_log = {}
audit_log = {}
PANIC_MODE = False
PANIC_MODE = False


# ───────── INPUT SCHEMA (API ONLY) ─────────
# ───────── INPUT SCHEMA (API ONLY) ─────────
class TransactionRequestIn(BaseModel):
class TransactionRequestIn(BaseModel):
    action: str
    action: str
    agent_id: str
    agent_id: str
    country: Optional[str] = "US"
    country: Optional[str] = "US"
    amount: Optional[float] = None
    amount: Optional[float] = None
    recipient: Optional[str] = None
    recipient: Optional[str] = None




# ───────── KERNEL SCHEMA (STRICT) ─────────
# ───────── KERNEL SCHEMA (STRICT) ─────────
class TransactionRequest(BaseModel):
class TransactionRequest(BaseModel):
    action: str
    action: str
    amount: float
    amount: float
    recipient: str
    recipient: str
    agent_id: str
    agent_id: str
    country: Optional[str] = "US"
    country: Optional[str] = "US"




class PanicRequest(BaseModel):
class PanicRequest(BaseModel):
    confirm: bool
    confirm: bool




class PaymentRequest(BaseModel):
class PaymentRequest(BaseModel):
    amount: float
    amount: float
    currency: str
    currency: str
    card_last4: str
    card_last4: str
    agent_id: str
    agent_id: str




async def verify_admin(x_admin_key: str = Header(None)):
async def verify_admin(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_KEY:
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="ACCESS DENIED")
        raise HTTPException(status_code=401, detail="ACCESS DENIED")
    return x_admin_key
    return x_admin_key




@app.get("/health")
@app.get("/health")
def health_check():
def health_check():
    return {"status": "healthy", "version": "Galani_v10_Emperor"}
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
