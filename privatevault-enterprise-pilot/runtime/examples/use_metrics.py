"""
Example: How to add metrics to your endpoints
"""

from fastapi import FastAPI
from prometheus_client import make_asgi_app
from monitoring.metrics.metrics import (
    track_request_metrics,
    record_risk_decision,
    active_agents,
)

app = FastAPI()

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


# ============================================================================
# Example: Track endpoint metrics
# ============================================================================
@app.post("/api/v1/credit/check")
@track_request_metrics("credit_check")
async def credit_check(applicant_id: str, amount: float):
    """Endpoint with automatic metrics tracking"""

    # Process request
    risk_score = 0.4

    # Record business metric
    record_risk_decision("credit_check", risk_score)

    return {"status": "approved", "risk_score": risk_score}


# ============================================================================
# Example: Update gauge metrics
# ============================================================================
@app.on_event("startup")
async def startup():
    """Update system metrics on startup"""
    # Count active agents
    # active_count = db.query("SELECT COUNT(*) FROM agents WHERE status='active'")
    active_agents.set(10)


# ============================================================================
# View metrics
# ============================================================================
# Visit: http://localhost:8000/metrics
# You'll see:
"""
# HELP galani_requests_total Total requests processed
# TYPE galani_requests_total counter
galani_requests_total{endpoint="credit_check",method="POST",status="success"} 1234.0

# HELP galani_request_duration_seconds Request duration in seconds
# TYPE galani_request_duration_seconds histogram
galani_request_duration_seconds_bucket{endpoint="credit_check",le="0.01"} 450.0
galani_request_duration_seconds_bucket{endpoint="credit_check",le="0.025"} 890.0
galani_request_duration_seconds_sum{endpoint="credit_check"} 15.3
galani_request_duration_seconds_count{endpoint="credit_check"} 1234.0

# HELP galani_risk_decisions_total Risk decisions made
# TYPE galani_risk_decisions_total counter
galani_risk_decisions_total{decision_type="credit_check",risk_level="medium"} 567.0
"""
