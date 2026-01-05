import uuid, time, secrets, random
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Galani Emperor Node", version="10.0.0-EMPEROR")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# CONFIG
ADMIN_KEY = "galani-emperor-secret-999"
SANCTIONED_COUNTRIES = ["NORTH_KOREA", "UNKNOWN_ISLAND"]

# STATE
velocity_db = {}
audit_log = {}
PANIC_MODE = False

# MODELS
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

# AUTH
async def verify_admin(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="⛔ ACCESS DENIED: Invalid Command Key")
    return x_admin_key

# ENDPOINTS
@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "Galani_v10_Emperor"}

@app.get("/api/v1/audit/{tx_id}")
def get_audit(tx_id: str):
    return audit_log.get(tx_id, {"error": "Not Found"})

@app.post("/api/v1/panic")
def set_panic(req: PanicRequest, authorized: str = Depends(verify_admin)):
    global PANIC_MODE
    if req.confirm:
        PANIC_MODE = True
        return {"status": "LOCKED", "msg": "KILL SWITCH ACTIVE"}
    return {"status": "IGNORED"}

@app.post("/api/v1/resolve")
def resolve_panic(authorized: str = Depends(verify_admin)):
    global PANIC_MODE
    PANIC_MODE = False
    return {"status": "RESOLVED", "msg": "Normal Traffic Resumed"}

@app.post("/api/v1/execute_payment")
def execute_payment(req: PaymentRequest):
    if PANIC_MODE: raise HTTPException(status_code=403, detail="PAYMENT DECLINED: LOCKDOWN")
    time.sleep(0.1) # Simulate bank
    if req.amount > 5000: return {"status": "DECLINED", "reason": "Insufficient Funds"}
    return {"status": "APPROVED", "bank_tx_id": "bnk_"+secrets.token_hex(8), "fee": req.amount*0.02}

@app.post("/api/v1/shadow_verify")
def verify(req: TransactionRequest):
    tx_id = str(uuid.uuid4())
    def decide(status, reason):
        decision = {"status": status, "reason": reason, "tx_id": tx_id, "metadata": {"merkle": "0x"+secrets.token_hex(16), "geo": req.country}}
        audit_log[tx_id] = decision
        return decision

    if PANIC_MODE: return decide("BLOCK", "KILL SWITCH ACTIVE")
    if req.country in SANCTIONED_COUNTRIES: return decide("BLOCK", f"Sanctioned: {req.country}")
    
    count = velocity_db.get(req.agent_id, 0)
    if count >= 3: return decide("BLOCK", "Velocity Limit")
    velocity_db[req.agent_id] = count + 1
    
    if req.amount > 10000: return decide("BLOCK", "Amount Limit")
    return decide("ALLOW", "Safe")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
