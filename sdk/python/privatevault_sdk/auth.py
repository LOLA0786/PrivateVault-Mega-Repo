from privatevault_sdk.client import Client


def auth_me(client: Client) -> dict:
    resp = client.request("GET", "/auth/me")
    resp.raise_for_status()
    return resp.json()
