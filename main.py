import datetime
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- CONFIGURATION ---
app = FastAPI(
    title="Galani Protocol Governance Node",
    description="Deterministic Policy Oracle & Shadow Verifier",
    version="3.1.0",
)

# Allow all origins for the demo phase (So your local Agents can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- DATA MODELS ---
class TransactionRequest(BaseModel):
    action: str  # e.g., "transfer", "access_data", "deploy_contract"
    amount: float  # e.g., 50000.00
    recipient: str  # e.g., "0xWalletAddress" or "VendorID"
    agent_id: str  # Which AI agent is asking?
    context: Optional[dict] = None


class VerificationResponse(BaseModel):
    status: str  # "ALLOW" or "BLOCK"
    reason: str  # Human readable explanation
    transaction_id: str  # The immutable log reference
    timestamp: str
    node_version: str


# --- SHADOW POLICY LOGIC (The Brain) ---
def check_policy(request: TransactionRequest) -> tuple[str, str]:
    """
    Deterministic rules engine.
    In production, this would query a database or evaluating a smart contract.
    """
    # RULE 1: Cap on unverified automated transfers
    if request.amount > 10000:
        return (
            "BLOCK",
            "Amount exceeds automated authorization limit (k). Human Approval Required.",
        )

    # RULE 2: Block known risky recipients
    if "unknown" in request.recipient.lower() or "anon" in request.recipient.lower():
        return "BLOCK", "Recipient identity cannot be verified (KYC Failure)."

    # RULE 3: Action Whitelist
    valid_actions = ["transfer", "pay_invoice", "query_balance"]
    if request.action not in valid_actions:
        return (
            "BLOCK",
            f"Action '{request.action}' is not in the approved capabilities list.",
        )

    # Otherwise, safe
    return "ALLOW", "Transaction within safe parameters."


# --- ENDPOINTS ---


@app.get("/")
def root():
    """Proof of Life for the browser"""
    return {
        "system": "Galani Governance Node",
        "status": "ONLINE",
        "mode": "SHADOW_VERIFY",
        "docs_url": "/docs",
    }


@app.get("/health")
def health_check():
    """AWS ALB Heartbeat"""
    return {"status": "healthy", "service": "galani-node"}


@app.post("/api/v1/shadow_verify", response_model=VerificationResponse)
async def shadow_verify(request: TransactionRequest):
    """
    The Shadow Endpoint.
    Agents send their intent here. We return ALLOW/BLOCK.
    We do NOT execute the trade. We only validate the intent.
    """
    # A. Generate a trace ID (The "Proof")
    tx_id = str(uuid.uuid4())

    # B. Run the Policy
    status, reason = check_policy(request)

    # C. Log it (Simulating immutable audit log write)
    # In real deployment, this goes to CloudWatch or a Ledger
    log_entry = f"[{datetime.datetime.now()}] TX:{tx_id} | AGENT:{request.agent_id} | AMT:{request.amount} | STATUS:{status}"
    print(log_entry)

    # D. Return the verdict
    return VerificationResponse(
        status=status,
        reason=reason,
        transaction_id=tx_id,
        timestamp=datetime.datetime.now().isoformat(),
        node_version="3.1.0-shadow",
    )


if __name__ == "__main__":
    import uvicorn

    # Local dev runner
    uvicorn.run(app, host="0.0.0.0", port=8000)
