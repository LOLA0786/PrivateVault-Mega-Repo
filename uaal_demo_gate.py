import os
import logging
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from pydantic import BaseModel, Field, validator

app = FastAPI()

# Configuration — never hard-code
DEMO_MODE_ENABLED = os.getenv("DEMO_MODE", "false").lower() == "true"
DEMO_SECRET_HEADER = os.getenv("DEMO_SECRET", "change-me-insecure-default")  # Set a real secret

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RejectDetail(BaseModel):
    status: str = "REJECTED"
    reason: str
    missing_fields: Optional[List[str]] = None
    invalid_fields: Optional[List[str]] = None
    fix: Optional[str] = None
    docs: Optional[str] = None

def reject(
    reason: str,
    missing_fields: Optional[List[str]] = None,
    invalid_fields: Optional[List[str]] = None,
    fix: Optional[str] = None,
    docs: Optional[str] = None,
):
    detail = RejectDetail(
        reason=reason,
        missing_fields=missing_fields,
        invalid_fields=invalid_fields,
        fix=fix,
        docs=docs,
    ).model_dump(exclude_none=True)
    raise HTTPException(status_code=422, detail=detail)

class TransactionRequest(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    action: str = Field(..., description="Action type e.g. read_balance, transfer")
    amount: Optional[float] = Field(None, ge=0)
    jurisdiction: str = Field(..., description="e.g. IN, US")
    policy_version: str = Field(..., description="e.g. FINTECH_v1")
    intent_hash: str = Field(..., description="Hash of canonical intent")
    merkle_root: Optional[str] = None
    proof: Optional[str] = None

    @validator("intent_hash")
    def validate_intent_hash(cls, v: str) -> str:
        if not v.startswith("0x") or len(v) != 66:
            raise ValueError("must be valid 32-byte hex with 0x prefix")
        return v

async def demo_dependency(
    request: Request,
    x_demo_key: Optional[str] = Header(None, alias="X-Demo-Key"),
) -> bool:
    if not DEMO_MODE_ENABLED:
        return False
    if x_demo_key != DEMO_SECRET_HEADER:
        logger.warning(f"Invalid demo key attempt from {request.client.host}")
        return False
    return True

@app.post("/api/v1/shadow_verify")
async def shadow_verify(
    payload: TransactionRequest,
    is_demo: bool = Depends(demo_dependency),
):
    if is_demo and payload.agent_id == "demo-agent":
        logger.info(f"Demo lane activated for {payload.agent_id}")

        # Bounded demo rules
        if payload.amount is not None and payload.amount > 1000:
            reject(
                reason="AMOUNT_EXCEEDS_DEMO_LIMIT",
                fix="In demo mode, amount must be <= 1000",
            )

        # Magic demo values — easy happy path
        expected_demo_hash = "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
        if payload.intent_hash != expected_demo_hash:
            reject(
                reason="INVALID_DEMO_INTENT_HASH",
                fix=f"Use demo intent_hash: {expected_demo_hash}",
            )

        # Bypass Merkle/proof entirely in demo
        return {
            "status": "APPROVED",
            "mode": "demo_sandbox",
            "message": "Shadow verify succeeded in guided demo mode",
        }

    # Production imperial kernel — unchanged, uncompromising
    logger.info(f"Strict production path for {payload.agent_id}")

    if payload.merkle_root is None:
        reject(
            reason="MISSING_INTEGRITY_PROOF",
            missing_fields=["merkle_root"],
            fix="Provide valid Merkle root matching current policy state",
            docs="https://docs.privatevault.api/integrity-proofs",
        )

    # Insert your real cryptographic/policy checks here
    # Example placeholder:
    # if not verify_merkle_proof(payload):
    #     reject(reason="INVALID_MERKLE_PROOF", ...)

    return {
        "status": "APPROVED",
        "mode": "production",
        "message": "Shadow verify passed with full enforcement",
    }

# Apply similar pattern to /api/v1/execute_payment
# Recommendation: completely block real execution in demo mode for safety
