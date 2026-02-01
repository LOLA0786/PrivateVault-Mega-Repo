"""
AI Firewall REST API
Production-ready Flask wrapper with auth, rate limiting, metrics
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from functools import wraps
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

from ai_firewall_orchestrator_dual_drift import AIFirewallOrchestrator

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
CORS(app, origins=allowed_origins)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri=os.getenv("RATELIMIT_STORAGE_URL", "memory://"),
    default_limits=["100 per hour", "20 per minute"],
)

# Logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.getenv("LOG_FILE", "ai_firewall_api.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Prometheus metrics
request_counter = Counter(
    "ai_firewall_requests_total", "Total API requests", ["endpoint", "status"]
)
request_duration = Histogram(
    "ai_firewall_request_duration_seconds", "Request duration", ["endpoint"]
)
blocked_inputs = Counter(
    "ai_firewall_blocked_inputs_total", "Total blocked inputs", ["reason"]
)
drift_detections = Counter(
    "ai_firewall_drift_detections_total", "Total drift detections", ["mode", "blocked"]
)
pii_redactions = Counter(
    "ai_firewall_pii_redactions_total", "Total PII redactions", ["pii_type"]
)

# Initialize AI Firewall
firewall = AIFirewallOrchestrator()


# API key authentication
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        expected_key = os.getenv("API_KEY")

        if not expected_key:
            logger.warning("API_KEY not configured - allowing all requests")
        elif api_key != expected_key:
            request_counter.labels(
                endpoint=request.endpoint, status="unauthorized"
            ).inc()
            return (
                jsonify(
                    {"error": "Unauthorized", "message": "Invalid or missing API key"}
                ),
                401,
            )

        return f(*args, **kwargs)

    return decorated_function


# ============================================
# API ENDPOINTS
# ============================================


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
            }
        ),
        200,
    )


@app.route("/api/v1/filter/input", methods=["POST"])
@require_api_key
@limiter.limit("50 per minute")
def filter_input():
    """
    Filter incoming prompt for injection/jailbreak attempts

    Request:
    {
        "user_id": "user_123",
        "role": "analyst",
        "prompt": "What is the weather?"
    }

    Response:
    {
        "status": "allowed|blocked",
        "filtered_prompt": "...",
        "threat_detected": false,
        "threat_reason": ""
    }
    """
    with request_duration.labels(endpoint="filter_input").time():
        try:
            data = request.get_json()

            # Validate input
            if not data or "prompt" not in data:
                request_counter.labels(endpoint="filter_input", status="error").inc()
                return jsonify({"error": "Missing 'prompt' field"}), 400

            user_id = data.get("user_id", "anonymous")
            role = data.get("role", "guest")
            prompt = data.get("prompt")

            # Process request
            result = firewall.process_request(user_id, role, prompt)

            # Update metrics
            if result["status"] == "blocked":
                blocked_inputs.labels(reason=result.get("reason", "unknown")).inc()
                request_counter.labels(endpoint="filter_input", status="blocked").inc()
            else:
                request_counter.labels(endpoint="filter_input", status="allowed").inc()

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in filter_input: {str(e)}", exc_info=True)
            request_counter.labels(endpoint="filter_input", status="error").inc()
            return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/authorize/tool", methods=["POST"])
@require_api_key
@limiter.limit("30 per minute")
def authorize_tool():
    """
    Authorize tool execution with JWT signing

    Request:
    {
        "user_id": "user_123",
        "role": "analyst",
        "tool_name": "file_system_read",
        "parameters": {"path": "/data/file.txt"}
    }

    Response:
    {
        "authorized": true,
        "executed": true,
        "signature": "eyJ...",
        "result": {...}
    }
    """
    with request_duration.labels(endpoint="authorize_tool").time():
        try:
            data = request.get_json()

            # Validate input
            required = ["user_id", "role", "tool_name", "parameters"]
            if not all(field in data for field in required):
                request_counter.labels(endpoint="authorize_tool", status="error").inc()
                return jsonify({"error": f"Missing required fields: {required}"}), 400

            # Process tool execution
            result = firewall.process_tool_execution(
                data["user_id"], data["role"], data["tool_name"], data["parameters"]
            )

            # Update metrics
            status = "authorized" if result["authorized"] else "denied"
            request_counter.labels(endpoint="authorize_tool", status=status).inc()

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in authorize_tool: {str(e)}", exc_info=True)
            request_counter.labels(endpoint="authorize_tool", status="error").inc()
            return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/filter/output", methods=["POST"])
@require_api_key
@limiter.limit("50 per minute")
def filter_output():
    """
    Filter LLM response for PII and drift detection

    Request:
    {
        "user_id": "user_123",
        "response": "Contact me at john@example.com",
        "original_prompt": "What is your email?",
        "actions_taken": [
            {"tool_name": "database_query", "parameters": {...}}
        ]
    }

    Response:
    {
        "status": "allowed|blocked",
        "filtered_response": "Contact me at [REDACTED_EMAIL]",
        "pii_redacted": ["email"],
        "drift_score": 0.85,
        "shadow_drift_score": 0.85
    }
    """
    with request_duration.labels(endpoint="filter_output").time():
        try:
            data = request.get_json()

            # Validate input
            required = ["user_id", "response", "original_prompt"]
            if not all(field in data for field in required):
                request_counter.labels(endpoint="filter_output", status="error").inc()
                return jsonify({"error": f"Missing required fields: {required}"}), 400

            # Process response
            result = firewall.process_response(
                data["user_id"],
                data["response"],
                data["original_prompt"],
                data.get("actions_taken"),
            )

            # Update metrics
            for pii_type in result.get("pii_redacted", []):
                pii_redactions.labels(pii_type=pii_type).inc()

            if result.get("drift_score") is not None:
                drift_blocked = result["status"] == "blocked"
                drift_detections.labels(mode="production", blocked=drift_blocked).inc()

            status = result["status"]
            request_counter.labels(endpoint="filter_output", status=status).inc()

            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Error in filter_output: {str(e)}", exc_info=True)
            request_counter.labels(endpoint="filter_output", status="error").inc()
            return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/stats", methods=["GET"])
@require_api_key
def get_stats():
    """Get firewall statistics"""
    try:
        stats = firewall.get_stats()
        comparison = firewall.get_policy_comparison_report()

        return (
            jsonify(
                {
                    "stats": stats,
                    "policy_comparison": comparison,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Error in get_stats: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/audit/export", methods=["GET"])
@require_api_key
def export_audit():
    """Export audit trail"""
    try:
        # Get ledger data
        audit_data = {
            "total_logs": len(firewall.ledger.chain),
            "chain_valid": firewall.ledger.verify_chain_integrity(),
            "logs": firewall.ledger.chain,
            "exported_at": datetime.utcnow().isoformat(),
        }

        return jsonify(audit_data), 200

    except Exception as e:
        logger.error(f"Error in export_audit: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    """Prometheus metrics endpoint"""
    if not os.getenv("ENABLE_METRICS", "true").lower() == "true":
        return jsonify({"error": "Metrics disabled"}), 404

    return generate_latest(REGISTRY), 200, {"Content-Type": "text/plain"}


@app.errorhandler(429)
def ratelimit_handler(e):
    """Rate limit exceeded"""
    request_counter.labels(endpoint=request.endpoint, status="ratelimited").inc()
    return jsonify({"error": "Rate limit exceeded", "message": str(e.description)}), 429


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    logger.info(f"🔥 Starting AI Firewall API on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(
        f"Drift production threshold: {os.getenv('DRIFT_PRODUCTION_THRESHOLD', '0.40')}"
    )
    logger.info(
        f"Drift shadow threshold: {os.getenv('DRIFT_SHADOW_THRESHOLD', '0.65')}"
    )

    app.run(host="0.0.0.0", port=port, debug=debug)
