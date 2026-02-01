# Envoy + OPA Governance Demo (GKE)

Runtime governance enforcement using:
- Envoy `ext_authz`
- OPA policy engine
- deny + approval-required workflows

## Behavior
- GET `/` -> 200 OK
- POST `/delete` -> 403 Forbidden (denied)
- POST `/deploy` -> 403 Forbidden + `x-approval-required: true`

## Run
```bash
bash in-cluster-test.sh
bash in-cluster-bench-allow.sh
bash in-cluster-bench-deny.sh

