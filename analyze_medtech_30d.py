#!/usr/bin/env python3

import json

high_risk = 0
ema_violations = 0
missing_consent = 0
total = 0

with open("uaal_medtech_30d.log") as f:
    for lineno, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            continue  # skip empty lines safely

        try:
            e = json.loads(line)
        except json.JSONDecodeError as err:
            raise RuntimeError(f"Invalid JSON at line {lineno}: {err}")

        total += 1

        if e.get("risk") == "HIGH":
            high_risk += 1

        if e.get("ema_violation") is True:
            ema_violations += 1

        if e.get("reason") == "MISSING_EXPLICIT_CONSENT":
            missing_consent += 1

print("\nUAAL — MEDTECH 30-DAY COMPLIANCE SUMMARY")
print("--------------------------------------")
print(f"Records analyzed : {total}")
print(f"• {high_risk} high-risk prescriptions flagged")
print(f"• {ema_violations} would violate EMA guidance")
print(f"• {missing_consent} lacked explicit consent logging\n")
