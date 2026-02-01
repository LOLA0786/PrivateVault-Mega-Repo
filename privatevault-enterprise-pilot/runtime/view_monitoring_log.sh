#!/bin/bash

LOG_FILE="uaal_monitoring.log"

echo "--------------------------------------------------"
echo "UAAL — LIVE INTENT MONITORING (SHADOW MODE)"
echo "--------------------------------------------------"

printf "%-20s %-10s %-28s %-7s %-6s %s\n" "TIME" "DOMAIN" "INTENT" "ALLOW" "RISK" "REASON"
echo "---------------------------------------------------------------------------------------------"

python3 <<'PYEOF'
import json

with open("uaal_monitoring.log") as f:
    for line in f:
        e = json.loads(line)
        print(
            f"{e['timestamp']:<20} "
            f"{e['domain']:<10} "
            f"{e['intent']:<28} "
            f"{('YES' if e['decision'] else 'NO'):<7} "
            f"{e['risk']:<6} "
            f"{e['reason']}"
        )
PYEOF
