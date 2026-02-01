# Failure Modes — PrivateVault Mega Repo

## Data Plane (Envoy/ext_authz/OPA)
- Check ext_authz stats:
  curl http://localhost:9901/stats | grep -i ext_authz
- Check adapter logs:
  kubectl -n governance logs deploy/authz-adapter --tail=200
- Check envoy crash reason:
  kubectl -n governance logs deploy/envoy --tail=200

## Governance Plane (Relay/Redis/Authority)
- Relay logs:
  kubectl -n governance logs deploy/governance-relay --tail=200
- Resolver logs:
  kubectl -n governance logs deploy/pv-authority-resolver --tail=200
- Redis health:
  kubectl -n governance logs deploy/redis-state --tail=80

## IP Leakage Prevention
- Always run:
  ./scripts/security-guard.sh
