import json
import base64

def generate_token(actor, scope):
    payload = {"actor": actor, "scope": scope, "vault_id": "PV-MEGA-01"}
    token = base64.b64encode(json.dumps(payload).encode()).decode()
    print(json.dumps({"actor": actor, "capability_token": token, "scope": scope}, indent=2))

if __name__ == "__main__":
    generate_token("governed_gateway", "OPTIMIZE")
