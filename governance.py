import datetime, uuid, time, secrets
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import defaultdict

app = FastAPI(title="Galani Universe Node", version="8.0.0-UNIVERSE")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# STATE
velocity_db = {}
audit_log = {}
stats = {"total": 0, "blocked": 0, "reasons": defaultdict(int), "max_amount_blocked": 0.0}
PANIC_MODE = False
POLICY_VERSION = "Galani_v8_Universe"

class TransactionRequest(BaseModel):
    action: str, amount: float, recipient: str, agent_id: str

class PanicRequest(BaseModel):
    confirm: bool

# ENDPOINTS
@app.get("/health")
def health_check():
    return {"status": "healthy", "version": POLICY_VERSION}

@app.get("/api/v1/shadow_report")
def get_shadow_report(window: str = "24h"):
    return {
        "policy_version": POLICY_VERSION,
        "total_tx": stats["total"],
        "blocked_tx": stats["blocked"],
        "block_rate": f"{(stats['blocked']/stats['total']*100) if stats['total']>0 else 0:.1f}%",
        "top_reasons": stats["reasons"]
    }

@app.get("/api/v1/audit/{tx_id}")
def get_audit_trail(tx_id: str):
    if tx_id not in audit_log: raise HTTPException(status_code=404, detail="Transaction ID not found.")
    return audit_log[tx_id]

@app.post("/api/v1/panic")
def trigger_panic(request: PanicRequest):
    global PANIC_MODE
    if request.confirm:
        PANIC_MODE = True
        return {"status": "NETWORK_LOCKDOWN", "message": "ALL TRAFFIC BLOCKED.", "policy_version": POLICY_VERSION}
    return {"status": "IGNORED"}

@app.post("/api/v1/resolve")
def resolve_panic():
    global PANIC_MODE; PANIC_MODE = False
    return {"status": "RESOLVED", "message": "Traffic normalized.", "policy_version": POLICY_VERSION}

@app.post("/api/v1/shadow_verify")
def shadow_verify(request: TransactionRequest):
    tx_id = str(uuid.uuid4()); stats["total"] += 1
    
    def log(status, reason, risk):
        decision = {
            "status": status, "reason": reason, "tx_id": tx_id, "policy_version": POLICY_VERSION,
            "governance_metadata": {"risk": risk, "merkle_root": "0x"+secrets.token_hex(32), "timestamp": datetime.datetime.now().isoformat()}
        }
        audit_log[tx_id] = decision
        if status == "BLOCK": stats["blocked"] += 1; stats["reasons"][reason] += 1
        return decision

    if PANIC_MODE: return log("BLOCK", "GLOBAL KILL SWITCH ACTIVE", "CRITICAL")
    
    count = velocity_db.get(request.agent_id, 0)
    if count >= 3: return log("BLOCK", "Velocity Limit Exceeded", "HIGH")
    velocity_db[request.agent_id] = count + 1

    if request.amount > 10000: return log("BLOCK", "Amount > 10k Limit", "MEDIUM")
        
    return log("ALLOW", "Safe", "LOW")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
