from privatevault_sdk.client import Client


def validate_quorum(client: Client, action: str, payload: dict, approvals: list, tenant_id: str | None = None):
    body = {"action": action, "payload": payload, "approvals": approvals}
    if tenant_id:
        body["tenant_id"] = tenant_id
    resp = client.request("POST", "/quorum/validate", json_body=body)
    resp.raise_for_status()
    return resp.json()
