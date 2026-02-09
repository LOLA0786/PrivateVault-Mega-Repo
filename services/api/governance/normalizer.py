"""
Normalizer
---------
Single, stable normalization entrypoint for ALL inputs:
- Chat
- API
- Agents
- Webhooks
"""

from typing import Dict


def normalize(payload: Dict) -> Dict:
    """
    Normalize incoming data into a canonical governance format.
    This function MUST remain stable.
    """

    if not isinstance(payload, dict):
        return {"text": str(payload)}

    # Common fields
    text = (
        payload.get("text")
        or payload.get("message")
        or payload.get("input")
        or ""
    )

    return {
        "source": payload.get("source", "unknown"),
        "sender": payload.get("sender", "unknown"),
        "text": text.strip(),
    }
