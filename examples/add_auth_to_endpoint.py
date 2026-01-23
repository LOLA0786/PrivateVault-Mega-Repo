"""
Example: How to add authentication to your endpoints
"""

from fastapi import FastAPI, Depends
from security.auth.jwt_auth import get_current_user, require_permission, AuthManager

app = FastAPI()


# ============================================================================
# PUBLIC ENDPOINT (No auth required)
# ============================================================================
@app.post("/api/v1/auth/login")
def login(username: str, password: str):
    """Public endpoint to get JWT token"""
    # TODO: Verify username/password against database
    # For now, just return token

    token = AuthManager.create_token(
        user_id=username,
        agent_id=f"agent_{username}",
        permissions=["credit_check", "fraud_detect"],
    )

    return {"access_token": token, "token_type": "bearer"}


# ============================================================================
# PROTECTED ENDPOINT (Requires valid token)
# ============================================================================
@app.get("/api/v1/profile")
def get_profile(user: dict = Depends(get_current_user)):
    """Protected endpoint - requires authentication"""
    return {
        "user_id": user["user_id"],
        "agent_id": user["agent_id"],
        "permissions": user["permissions"],
    }


# ============================================================================
# PERMISSION-BASED ENDPOINT (Requires specific permission)
# ============================================================================
@app.post("/api/v1/credit/check")
async def credit_check(
    amount: float, user: dict = Depends(require_permission("credit_check"))
):
    """Requires 'credit_check' permission"""
    return {"user_id": user["user_id"], "amount": amount, "status": "approved"}


# How to call these endpoints:
"""
# 1. Get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"username": "john", "password": "secret"}'

# Response: {"access_token": "eyJ0eXAiOi...", "token_type": "bearer"}

# 2. Use token to call protected endpoint
curl http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer eyJ0eXAiOi..."

# 3. Call permission-based endpoint
curl -X POST http://localhost:8000/api/v1/credit/check \
  -H "Authorization: Bearer eyJ0eXAiOi..." \
  -d '{"amount": 50000}'
"""
