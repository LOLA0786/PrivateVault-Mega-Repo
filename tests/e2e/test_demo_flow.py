import requests

def test_demo_discount_flow():

    ctx = {
        "id": "e2e-1",
        "source": "salesforce",
        "user_id": "demo-user",
        "data": {
            "customer_value": 100000,
            "deal_stage": "negotiation",
            "manager_approved": True
        },
        "policy_version": "v1.0",
        "risk_profile": "medium"
    }

    r1 = requests.post("http://localhost:8001/context", json=ctx)
    assert r1.status_code == 200

    # CRO approval
    requests.post("http://localhost:8001/approve", json={
        "context_id": "e2e-1",
        "role": "CRO",
        "user": "raj"
    })

    # LEGAL approval
    requests.post("http://localhost:8001/approve", json={
        "context_id": "e2e-1",
        "role": "LEGAL",
        "user": "anita"
    })

    r2 = requests.post("http://localhost:8001/authorize", json={
        "context_id": "e2e-1",
        "action": "send_discount"
    })

    assert r2.json()["allowed"] is True
