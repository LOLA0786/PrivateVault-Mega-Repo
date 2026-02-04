from privatevault_sdk import Client, create_approval, validate_quorum, export_evidence

client = Client(base_url="http://localhost:8000/api/v1", token="YOUR_TOKEN")

payload = {"amount": 100, "recipient": "acct-1"}
intent_hash = "<hash>"
approval = create_approval(
    approver_id="approver-1",
    role="CRO",
    region="US",
    intent_hash=intent_hash,
    key_id="k1",
    secret="secret-1",
)

validate_quorum(client, "POST /api/emit/fintech", payload, [approval])

export_evidence(
    client,
    tenant_id="tenant-demo",
    start="2026-02-01T00:00:00Z",
    end="2026-02-28T23:59:59Z",
)
