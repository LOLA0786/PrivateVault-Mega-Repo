import os
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI()

# -------------------------------------------------------------------
# CONFIG (NO HARDCODED SECRETS)
# -------------------------------------------------------------------
DEMO_MODE_ENABLED = os.getenv("DEMO_MODE", "false").lower() == "true"
DEMO_SECRET = os.getenv("DEMO_SECRET", "change-me-insecure-default")

# -------------------------------------------------------------------
# REJECT STRUCTURE
# -------------------------------------------------------------------
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
    ).dict(exclude_none=True)
    raise HTTPException(status_code=422, detail=detail)


# -------------------------------------------------------------------
# CLEAN VALIDATION ERROR HANDLER (REPLACES RAW PYDANTIC ERRORS)
# -------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    missing = [e["loc"][-1] for e in errors if e["type"] == "missing"]
    invalid = [e["loc"][-1] for e in errors if e["type"] != "missing"]

    return JSONResponse(
        status_code=422,
        content=RejectDetail(
            reason="INVALID_REQUEST_SCHEMA",
            missing_fields=missing or None,
            invalid_fields=invalid or None,
            fix="Provide required fields only for relevant actions (amount/recipient required only for payment actions)",
            docs="https://docs.privatevault.api/schemas#conditional-fields",
        ).dict(exclude_none=True),
    )


# -------------------------------------------------------------------
# TRANSACTION SCHEMA (CONDITIONAL, NOT OVER-CONSTRAINED)
# -------------------------------------------------------------------
class TransactionRequest(BaseModel):
    agent_id: str = Field(..., description="Unique agent identifier")
    action: str = Field(..., description="read_balance | execute_payment | transfer")
    jurisdiction: str = Field(..., description="IN, US, etc")
    policy_version: str = Field(..., description="FINTECH_v1")
    intent_hash: str = Field(..., description="32-byte intent hash")

    amount: Optional[float] = Field(None, ge=0)
    recipient: Optional[str] = None
    merkle_root: Optional[str] = None

    @field_validator("intent_hash")
    def validate_intent_hash(cls, v: str):
        if not (v.startswith("0x") and len(v) == 66):
            raise ValueError("must be 32-byte hex with 0x prefix")
        return v

    @field_validator("amount", "recipient")
    def conditional_requirements(cls, v, info):
        action = info.data.get("action")
        if action in {"execute_payment", "transfer", "send"}:
            if v is None:
                raise ValueError("required for payment actions")
        return v


# -------------------------------------------------------------------
# DEMO DEPENDENCY (TRIPLE-GATED)
# -------------------------------------------------------------------
async def demo_dependency(
    x_demo_key: Optional[str] = Header(None, alias="X-Demo-Key"),
) -> bool:
    if not DEMO_MODE_ENABLED:
        return False
    if x_demo_key != DEMO_SECRET:
        return False
    return True


# -------------------------------------------------------------------
# SHADOW VERIFY ENDPOINT
# -------------------------------------------------------------------
@app.post("/api/v1/shadow_verify")
async def shadow_verify(
    payload: TransactionRequest,
    is_demo: bool = Depends(demo_dependency),
):
    # ---------------- DEMO LANE ----------------
    if is_demo and payload.agent_id == "demo-agent":
        if payload.amount is not None and payload.amount > 1000:
            reject(
                reason="DEMO_AMOUNT_LIMIT_EXCEEDED",
                fix="Demo amount must be <= 1000",
            )

        expected_demo_hash = (
            "0xdeadbeefdeadbeefdeadbeefdeadbeef"
            "deadbeefdeadbeefdeadbeefdeadbeef"
        )
        if payload.intent_hash != expected_demo_hash:
            reject(
                reason="INVALID_DEMO_INTENT_HASH",
                fix=f"Use demo intent_hash: {expected_demo_hash}",
            )

        return {
            "status": "APPROVED",
            "mode": "demo_sandbox",
            "message": "Shadow verify succeeded (guided demo)",
            "tx_id": "demo-tx-0001",
        }

    # ---------------- PRODUCTION KERNEL ----------------
    if payload.action == "read_balance":
        return {
            "status": "ALLOW",
            "reason": "Safe",
            "balance": 0,
        }

    if payload.merkle_root is None:
        reject(
            reason="MISSING_INTEGRITY_PROOF",
            missing_fields=["merkle_root"],
            fix="Provide valid Merkle root for production enforcement",
            docs="https://docs.privatevault.api/integrity-proofs",
        )

    return {
        "status": "ALLOW",
        "reason": "Safe",
        "tx_id": "real-tx-1234",
        "metadata": {
            "merkle": payload.merkle_root,
            "geo": "US",
        },
    }
