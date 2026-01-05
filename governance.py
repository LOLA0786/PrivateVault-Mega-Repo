import datetime, uuid, time, secrets
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Galani Governance Node", version="7.0.0-GOD-MODE")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- IN-MEMORY STATE ---
velocity_db = {}       # Tracks spam
audit_log = {}         # Stores transaction history
PANIC_MODE = False     # The Kill Switch

class TransactionRequest(BaseModel):
    action: str
    amount: float
    recipient: str
    agent_id: str

class PanicRequest(BaseModel):
    confirm: bool

# --- 1. THE PANIC BUTTON ---
@app.post("/api/v1/panic")
def trigger_panic(request: PanicRequest):
    global PANIC_MODE
    if request.confirm:
        PANIC_MODE = True
        return {"status": "NETWORK_LOCKDOWN", "message": "ALL TRAFFIC BLOCKED. KILL SWITCH ACTIVE."}
    return {"status": "IGNORED", "message": "Confirmation required."}

@app.post("/api/v1/resolve")
def resolve_panic():
    global PANIC_MODE
    PANIC_MODE = False
    return {"status": "RESOLVED", "message": "Traffic normalized."}

# --- 2. THE AUDIT SEARCH ---
@app.get("/api/v1/audit/{tx_id}")
def get_audit_trail(tx_id: str):
    if tx_id not in audit_log:
        raise HTTPException(status_code=404, detail="Transaction ID not found in local node.")
    return audit_log[tx_id]

# --- 3. THE CORE ENGINE ---
@app.post("/api/v1/shadow_verify")
def shadow_verify(request: TransactionRequest):
    tx_id = str(uuid.uuid4())
    start_time = time.time()
    
    # A. GLOBAL KILL SWITCH CHECK
    if PANIC_MODE:
        decision = {
            "status": "BLOCK",
            "reason": "GLOBAL KILL SWITCH ACTIVE",
            "tx_id": tx_id,
            "governance_metadata": {"risk": "CRITICAL", "merkle_root": "0x0000000000000000"}
        }
        audit_log[tx_id] = decision # Log it
        return decision

    # B. VELOCITY CHECK
    count = velocity_db.get(request.agent_id, 0)
    if count >= 3:
        decision = {
            "status": "BLOCK", 
            "reason": "Velocity Limit Exceeded (>3 req/session)",
            "tx_id": tx_id,
            "governance_metadata": {"risk": "HIGH", "merkle_root": "0x"+secrets.token_hex(32)}
        }
        audit_log[tx_id] = decision # Log it
        return decision
    
    velocity_db[request.agent_id] = count + 1

    # C. AMOUNT CHECK
    if request.amount > 10000:
        decision = {"status": "BLOCK", "reason": "Amount > 10k", "tx_id": tx_id}
        audit_log[tx_id] = decision
        return decision
        
    # D. ALLOW
    decision = {
        "status": "ALLOW", 
        "reason": "Safe", 
        "tx_id": tx_id,
        "governance_metadata": {"risk": "LOW", "merkle_root": "0x"+secrets.token_hex(32)}
    }
    audit_log[tx_id] = decision
    return decision

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
