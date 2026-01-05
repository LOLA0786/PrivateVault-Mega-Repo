import uuid, time, secrets
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Galani Stable Node", version="9.0.0-STABLE")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- STATE ---
# We use simple globals to avoid complexity crashes
velocity_db = {}
audit_log = {}
PANIC_MODE = False

class TransactionRequest(BaseModel):
    action: str
    amount: float
    recipient: str
    agent_id: str

class PanicRequest(BaseModel):
    confirm: bool

# --- ENDPOINTS ---

@app.get("/health")
def health_check():
    # If this endpoint works, the server is ALIVE
    return {"status": "healthy", "version": "Galani_v9_Stable"}

@app.get("/api/v1/audit/{tx_id}")
def get_audit(tx_id: str):
    return audit_log.get(tx_id, {"error": "Not Found"})

@app.post("/api/v1/panic")
def set_panic(req: PanicRequest):
    global PANIC_MODE
    if req.confirm:
        PANIC_MODE = True
        return {"status": "LOCKED", "msg": "KILL SWITCH ACTIVE"}
    return {"status": "IGNORED"}

@app.post("/api/v1/resolve")
def resolve_panic():
    global PANIC_MODE
    PANIC_MODE = False
    return {"status": "RESOLVED", "msg": "Normal Traffic Resumed"}

@app.post("/api/v1/shadow_verify")
def verify(req: TransactionRequest):
    tx_id = str(uuid.uuid4())
    
    # 1. KILL SWITCH
    if PANIC_MODE:
        decision = {"status": "BLOCK", "reason": "KILL SWITCH", "tx_id": tx_id}
        audit_log[tx_id] = decision
        return decision

    # 2. VELOCITY
    count = velocity_db.get(req.agent_id, 0)
    if count >= 3:
        decision = {"status": "BLOCK", "reason": "Velocity Limit", "tx_id": tx_id}
        audit_log[tx_id] = decision
        return decision
    velocity_db[req.agent_id] = count + 1

    # 3. AMOUNT
    if req.amount > 10000:
        decision = {"status": "BLOCK", "reason": "Amount Limit", "tx_id": tx_id}
        audit_log[tx_id] = decision
        return decision

    # 4. ALLOW
    decision = {
        "status": "ALLOW",
        "reason": "Safe",
        "tx_id": tx_id,
        "metadata": {"merkle": "0x" + secrets.token_hex(16)}
    }
    audit_log[tx_id] = decision
    return decision

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
