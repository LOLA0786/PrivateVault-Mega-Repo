import datetime, uuid, time, secrets
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Galani Governance Node", version="5.0.0-SUPER")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# IN-MEMORY DATABASE (The Trap)
velocity_db = {}

class TransactionRequest(BaseModel):
    action: str
    amount: float
    recipient: str
    agent_id: str

@app.post("/api/v1/shadow_verify")
def shadow_verify(request: TransactionRequest):
    # 1. VELOCITY CHECK
    count = velocity_db.get(request.agent_id, 0)
    if count >= 3:
        return {
            "status": "BLOCK", 
            "reason": "Velocity Limit Exceeded (>3 req/session)",
            "governance_metadata": {"risk": "HIGH", "merkle_root": "0x"+secrets.token_hex(32)}
        }
    velocity_db[request.agent_id] = count + 1

    # 2. AMOUNT CHECK
    if request.amount > 10000:
        return {"status": "BLOCK", "reason": "Amount > 10k"}
        
    return {
        "status": "ALLOW", 
        "reason": "Safe", 
        "tx_id": str(uuid.uuid4()),
        "governance_metadata": {"risk": "LOW", "merkle_root": "0x"+secrets.token_hex(32)}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
