from privatevault_sdk.client import Client


def export_evidence(
    client: Client,
    tenant_id: str,
    start: str,
    end: str,
    bundle_name: str | None = None,
    idempotency_key: str | None = None,
):
    body = {"tenant_id": tenant_id, "start": start, "end": end}
    if bundle_name:
        body["bundle_name"] = bundle_name
    resp = client.request(
        "POST",
        "/evidence/export",
        json_body=body,
        idempotency_key=idempotency_key,
    )
    resp.raise_for_status()
    return resp.json()
