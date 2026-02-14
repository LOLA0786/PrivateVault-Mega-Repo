import os
import requests

AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8000")

def classify_message(message: str, tenant_id: str, user_id: str):
    response = requests.post(
        f"{AI_SERVICE_URL}/ai/classify",
        json={
            "tenant_id": tenant_id,
            "user_id": user_id,
            "input_text": message,
        },
        timeout=3,
    )
    response.raise_for_status()
    return response.json()
