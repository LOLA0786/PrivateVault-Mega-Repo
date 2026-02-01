#!/usr/bin/env bash
set -euo pipefail
NS=governance

kubectl -n "$NS" get cm envoy-config -o jsonpath='{.data.envoy\.yaml}' > /tmp/envoy.yaml

python3 - <<'PY'
from pathlib import Path
import re
p = Path("/tmp/envoy.yaml")
s = p.read_text()

# Force ALL route clusters to demo_service
s = re.sub(r'route:\s*\{\s*cluster:\s*[^}]+\}', 'route: { cluster: demo_service }', s)

# Force demo_service endpoint EXACTLY to demo:9000 (simple hard replace block)
s = re.sub(
    r'- name:\s*demo_service.*?- name:\s*authz_adapter',
    lambda m: re.sub(
        r'socket_address:\s*\{\s*address:\s*[^,}]+\s*,\s*port_value:\s*\d+\s*\}',
        'socket_address: { address: demo, port_value: 9000 }',
        m.group(0),
        count=1
    ),
    s,
    flags=re.S
)

p.write_text(s)
print("✅ patched envoy.yaml: route->demo_service, demo_service->demo:9000")
PY

kubectl -n "$NS" create cm envoy-config --from-file=envoy.yaml=/tmp/envoy.yaml -o yaml --dry-run=client | kubectl apply -f -
kubectl -n "$NS" rollout restart deploy/envoy
kubectl -n "$NS" rollout status deploy/envoy
