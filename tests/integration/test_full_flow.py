import requests
import json

def test_full_fintech_flow():
    ctx = {
        "id": "int-1",
        "source": "crm",
        "user_id": "u1",
        "data": {
            "customer_value": 80000,
            "deal_stage": "negotiation",
            "manager_approved": True
        },
        "policy_version": "v1.0",
        "risk_profile": "medium"
    }

    r1 = requests.post("http://localhost:8001/context", json=ctx)
    assert r1.status_code == 200

    r2 = requests.post("http://localhost:8001/authorize", json={
        "context_id": "int-1",
        "action": "send_discount"
    })

    assert "allowed" in r2.json()
