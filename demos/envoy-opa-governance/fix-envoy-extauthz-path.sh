#!/usr/bin/env bash
set -euo pipefail
NS=governance

kubectl -n $NS get cm envoy-config -o jsonpath='{.data.envoy\.yaml}' > /tmp/envoy.yaml

# inject path_prefix under http_service (only if missing)
python3 - <<'PY'
import re, pathlib
p = pathlib.Path("/tmp/envoy.yaml")
s = p.read_text()

if "path_prefix:" in s:
    print("path_prefix already present, no change")
    exit(0)

# add path_prefix right after timeout line
s2 = re.sub(
    r'(timeout:\s*1\.0s\s*\n)',
    r'\1                path_prefix: "/authz"\n',
    s,
    count=1
)

if s2 == s:
    raise SystemExit("FAILED: could not inject path_prefix (pattern not found).")

p.write_text(s2)
print("✅ injected path_prefix: /authz")
PY

kubectl -n $NS create cm envoy-config --from-file=envoy.yaml=/tmp/envoy.yaml -o yaml --dry-run=client | kubectl apply -f -
kubectl -n $NS rollout restart deploy/envoy
kubectl -n $NS rollout status deploy/envoy
