"""
Policy Engine
-------------
Deterministic governance rules.
NO randomness. NO external models.
"""

from datetime import datetime


def evaluate_policy(normalized: dict) -> dict:
    """
    Evaluate input against governance policies.
    Returns a deterministic decision + evidence.
    """

    text = normalized.get("text", "").lower()

    # GDPR / PII
    if any(keyword in text for keyword in ["aadhaar", "ssn", "passport", "credit card"]):
        return {
            "blocked": True,
            "policy": "GDPR_PII_RESTRICTION",
            "evidence_hash": "0xabc123",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    # Healthcare (HIPAA)
    if any(keyword in text for keyword in ["patient", "diagnosis", "medical record", "insulin"]):
        return {
            "blocked": True,
            "policy": "HIPAA_PHI_RESTRICTION",
            "evidence_hash": "0xdef456",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    # Fintech
    if any(keyword in text for keyword in ["transfer", "bank account", "routing number"]):
        return {
            "blocked": True,
            "policy": "FINANCIAL_TRANSACTION_RESTRICTION",
            "evidence_hash": "0xfin789",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    # Default allow
    return {
        "blocked": False,
        "policy": None,
        "evidence_hash": None,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
