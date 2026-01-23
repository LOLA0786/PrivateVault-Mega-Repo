"""
Example: How to use structured logging
"""

from monitoring.logging.logger import get_logger

logger = get_logger(__name__)


def process_credit_check(applicant_id: str, amount: float):
    """Example function with logging"""

    # Log start
    logger.info("credit_check_started", applicant_id=applicant_id, amount=amount)

    try:
        # Do processing
        risk_score = calculate_risk(applicant_id, amount)

        # Log success
        logger.info(
            "credit_check_completed",
            applicant_id=applicant_id,
            amount=amount,
            risk_score=risk_score,
            decision="approved",
        )

        return {"status": "approved", "risk_score": risk_score}

    except Exception as e:
        # Log error with context
        logger.error(
            "credit_check_failed",
            applicant_id=applicant_id,
            amount=amount,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


def calculate_risk(applicant_id: str, amount: float) -> float:
    """Dummy risk calculation"""
    return 0.3


# Output will be JSON (easy to search in logs):
"""
{
  "timestamp": "2026-01-14T10:30:00.123Z",
  "level": "info",
  "name": "__main__",
  "event": "credit_check_started",
  "applicant_id": "APP123",
  "amount": 50000.0
}
"""
