#!/usr/bin/env python3
"""
Galani Protocol - Main Entry Point (Vault Integrated)
"""
import os
import sys
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add security modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from security.secrets.secrets_manager import get_secrets_manager
from security.auth.jwt_auth import get_current_user, AuthManager
from monitoring.logging.logger import get_logger
from monitoring.metrics.metrics import (
    track_request_metrics,
    record_risk_decision,
    active_agents,
)
from monitoring.health.health_check import add_health_endpoints
from prometheus_client import make_asgi_app

# Initialize
app = FastAPI(
    title="Galani Protocol v2.0",
    description="Production-Grade AI Governance System",
    version="2.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logger = get_logger(__name__)

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Add health checks
add_health_endpoints(app)

# ============================================================================
# Startup Event
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("galani_starting", version="2.0.0")

    # Test Vault connection
    try:
        secrets = get_secrets_manager()
        logger.info("vault_connected", status="ok")
    except Exception as e:
        logger.error("vault_connection_failed", error=str(e))
        raise

    # Update active agents metric
    active_agents.set(0)  # Will be updated by actual agent count

    logger.info("galani_started", status="ready")


# ============================================================================
# Public Endpoints (No Auth Required)
# ============================================================================


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Galani Protocol",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.post("/api/v1/auth/login")
def login(username: str, password: str):
    """
    Login endpoint - returns JWT token

    In production, verify against database
    For now, accepts any credentials
    """
    logger.info("login_attempt", username=username)

    # TODO: Verify against database
    # For demo, just return token

    token = AuthManager.create_token(
        user_id=username,
        agent_id=f"agent_{username}",
        permissions=["credit_check", "fraud_detect", "kyc_verify"],
    )

    logger.info("login_success", username=username)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": 86400,  # 24 hours
    }


# ============================================================================
# Protected Endpoints (Auth Required)
# ============================================================================


@app.get("/api/v1/profile")
def get_profile(user: dict = Depends(get_current_user)):
    """Get current user profile"""
    logger.info("profile_accessed", user_id=user["user_id"])
    return {
        "user_id": user["user_id"],
        "agent_id": user["agent_id"],
        "permissions": user["permissions"],
    }


@app.post("/api/v1/credit/check")
@track_request_metrics("credit_check")
async def credit_check(
    applicant_id: str,
    amount: float,
    term_months: int,
    user: dict = Depends(get_current_user),
):
    """
    Credit check endpoint

    Requires: credit_check permission
    """
    logger.info(
        "credit_check_started",
        applicant_id=applicant_id,
        amount=amount,
        user_id=user["user_id"],
    )

    # Check permission
    if "credit_check" not in user.get("permissions", []):
        logger.warning("permission_denied", user_id=user["user_id"])
        raise HTTPException(status_code=403, detail="Missing permission: credit_check")

    # Calculate risk score (simplified)
    risk_score = calculate_risk_score(applicant_id, amount, term_months)

    # Record metric
    record_risk_decision("credit_check", risk_score)

    # Determine decision
    if risk_score < 0.3:
        decision = "approved"
    elif risk_score < 0.7:
        decision = "manual_review"
    else:
        decision = "rejected"

    logger.info(
        "credit_check_completed",
        applicant_id=applicant_id,
        risk_score=risk_score,
        decision=decision,
    )

    return {
        "applicant_id": applicant_id,
        "amount": amount,
        "term_months": term_months,
        "risk_score": risk_score,
        "decision": decision,
        "timestamp": "2026-01-14T10:00:00Z",
    }


def calculate_risk_score(applicant_id: str, amount: float, term_months: int) -> float:
    """
    Calculate risk score

    In production, this would use ML models, credit bureau data, etc.
    For demo, returns a simple calculation
    """
    import random

    # Simplified risk calculation
    base_risk = 0.3

    # Higher amounts = higher risk
    amount_risk = min(amount / 1_000_000, 0.3)

    # Longer terms = higher risk
    term_risk = min(term_months / 360, 0.2)

    # Add some randomness
    random_risk = random.uniform(-0.1, 0.1)

    total_risk = base_risk + amount_risk + term_risk + random_risk

    return max(0.0, min(1.0, total_risk))


@app.post("/api/v1/fraud/detect")
@track_request_metrics("fraud_detect")
async def fraud_detect(
    transaction_id: str,
    amount: float,
    merchant: str,
    card_last4: str,
    user: dict = Depends(get_current_user),
):
    """
    Fraud detection endpoint

    Requires: fraud_detect permission
    """
    logger.info(
        "fraud_check_started",
        transaction_id=transaction_id,
        amount=amount,
        user_id=user["user_id"],
    )

    # Check permission
    if "fraud_detect" not in user.get("permissions", []):
        raise HTTPException(status_code=403, detail="Missing permission: fraud_detect")

    # Simple fraud detection (in production, use ML model)
    import random

    fraud_score = random.uniform(0.0, 1.0)

    is_fraud = fraud_score > 0.8

    logger.info(
        "fraud_check_completed",
        transaction_id=transaction_id,
        fraud_score=fraud_score,
        is_fraud=is_fraud,
    )

    return {
        "transaction_id": transaction_id,
        "fraud_score": fraud_score,
        "is_fraud": is_fraud,
        "recommendation": "block" if is_fraud else "allow",
    }


# ============================================================================
# Admin Endpoints (Debug only - remove in production)
# ============================================================================


@app.get("/api/v1/debug/vault-test")
async def test_vault_connection():
    """Test Vault connection and retrieve a secret"""
    try:
        secrets = get_secrets_manager()

        # Try to get OpenAI key
        openai_secret = secrets.get_secret("openai/api_key")

        if openai_secret:
            api_key = openai_secret["data"]["data"]["api_key"]
            return {
                "status": "success",
                "vault_connected": True,
                "secret_exists": True,
                "api_key_preview": api_key[:10] + "..." if len(api_key) > 10 else "***",
            }
        else:
            return {
                "status": "warning",
                "vault_connected": True,
                "secret_exists": False,
                "message": "Secret not found",
            }
    except Exception as e:
        return {"status": "error", "vault_connected": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(
        "main_vault_integrated:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
