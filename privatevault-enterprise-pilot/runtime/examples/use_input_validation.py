"""
Example: How to use input validation in your endpoints
"""

from fastapi import FastAPI, HTTPException
from security.validation.validators import (
    CreditCheckRequest,
    FraudDetectRequest,
    SafeQueryBuilder,
    PromptSanitizer,
)

app = FastAPI()


# ============================================================================
# EXAMPLE 1: Validate request body
# ============================================================================
@app.post("/api/v1/credit/check")
def credit_check(request: CreditCheckRequest):
    """Pydantic automatically validates the request"""

    # If we get here, validation passed
    return {
        "applicant_id": request.applicant_id,
        "amount": request.amount,
        "status": "approved",
    }


# Try calling with invalid data:
"""
# This will fail validation (amount too large):
curl -X POST http://localhost:8000/api/v1/credit/check \
  -H "Content-Type: application/json" \
  -d '{"applicant_id": "test", "amount": 99999999, "term_months": 60}'

# Response: {"detail": [{"loc": ["body", "amount"], "msg": "ensure this value is less than 10000000"}]}
"""


# ============================================================================
# EXAMPLE 2: Safe database queries
# ============================================================================
@app.get("/api/v1/agents/{agent_id}")
def get_agent(agent_id: str):
    """Safely query database"""

    # WRONG WAY (SQL Injection vulnerability):
    # query = f"SELECT * FROM agents WHERE agent_id = '{agent_id}'"

    # RIGHT WAY (Parameterized query):
    query, params = SafeQueryBuilder.build_query("agents", {"agent_id": agent_id})

    # Execute with parameters
    # result = db.execute(query, params)

    return {"query": query, "params": params}


# ============================================================================
# EXAMPLE 3: Sanitize AI prompts
# ============================================================================
@app.post("/api/v1/ai/analyze")
def analyze_with_ai(user_prompt: str):
    """Sanitize prompt before sending to AI"""

    # Sanitize to prevent prompt injection
    safe_prompt = PromptSanitizer.sanitize(user_prompt)

    # Now safe to send to AI
    # response = openai.ChatCompletion.create(
    #     messages=[{"role": "user", "content": safe_prompt}]
    # )

    return {"original": user_prompt, "sanitized": safe_prompt}
