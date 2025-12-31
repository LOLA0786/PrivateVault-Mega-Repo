#!/bin/bash

LOG="uaal_medtech_monitoring.log"

if [ ! -f "$LOG" ]; then
  echo "ERROR: $LOG not found"
  exit 1
fi

echo "--------------------------------------------------"
echo "UAAL — MEDTECH PRESCRIPTION MONITORING (SHADOW MODE)"
echo "--------------------------------------------------"

printf "%-20s %-18s %-6s %-7s %-6s %s\n" "TIME" "MEDICINE" "AGE" "ALLOW" "RISK" "REASON"
echo "---------------------------------------------------------------------------------------------"

python3 <<'PYEOF'
import json

with open("uaal_medtech_monitoring.log") as f:
    for line in f:
        e = json.loads(line)
        print(
            f"{e['timestamp']:<20} "
            f"{e['medicine']:<18} "
            f"{e['patient_age']:<6} "
            f"{('YES' if e['decision'] else 'NO'):<7} "
            f"{e['risk']:<6} "
            f"{e['reason']}"
        )
PYEOF
