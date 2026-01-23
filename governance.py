from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid, secrets, inspect, os

app = FastAPI()

# ============================
# API KEY (PILOT)
# ============================
PILOT_API_KEYS = {
    "pilot_acme_001",
    "pilot_kaggle_002",
    "pilot_demo_003",
}


def require_api_key(x_api_key: str = Header(None)):
    if x_api_key not in PILOT_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ============================
# MODELS
# ============================
class TransactionRequestIn(BaseModel):
    action: str
    amount: Optional[int] = None
    recipient: Optional[str] = None
    agent_id: str
    country: str


# ============================
# HEALTH + WHOAMI
# ============================
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/__whoami")
def whoami():
    return {"file": inspect.getfile(whoami), "cwd": os.getcwd()}


# ============================
# SHADOW VERIFY (ENFORCED)
# ============================
@app.post("/api/v1/shadow_verify", dependencies=[Depends(require_api_key)])
def verify(req: TransactionRequestIn):
    tx_id = str(uuid.uuid4())

    decision = {
        "status": "ALLOW",
        "reason": "Safe",
        "tx_id": tx_id,
        "metadata": {
            "merkle": "0x" + secrets.token_hex(16),
            "geo": req.country,
        },
    }
    return decision
