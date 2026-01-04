import datetime
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Galani Governance Node", version="3.2.0-CLEAN")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TransactionRequest(BaseModel):
    action: str
    amount: float
    recipient: str
    agent_id: str

@app.get("/")
def root():
    return {"system": "Galani Governance Node", "status": "ONLINE", "mode": "SHADOW_VERIFY"}

# The Critical Endpoint (ALB looks here)
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "galani-node-v3.2"}

@app.post("/api/v1/shadow_verify")
def shadow_verify(request: TransactionRequest):
    tx_id = str(uuid.uuid4())
    # Hardcoded Logic for Demo
    if request.amount > 10000:
        return {"status": "BLOCK", "reason": "Amount > 10k Limit", "tx_id": tx_id}
    return {"status": "ALLOW", "reason": "Safe", "tx_id": tx_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
