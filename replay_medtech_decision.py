#!/usr/bin/env python3

import json
import argparse
import sys

LOG_FILE = "uaal_medtech_monitoring.log"

parser = argparse.ArgumentParser(description="UAAL Medtech Decision Replay")
parser.add_argument("--intent-hash", required=True, help="Intent hash to replay")
args = parser.parse_args()

found = False

try:
    with open(LOG_FILE) as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("intent_hash") == args.intent_hash:
                found = True
                print("\nUAAL — MEDTECH DECISION REPLAY")
                print("----------------------------------")
                print(f"Intent Hash   : {entry['intent_hash']}")
                print(f"Timestamp     : {entry['timestamp']}")
                print(f"Medicine      : {entry['medicine']}")
                print(f"Patient Age   : {entry['patient_age']}")
                print(f"Decision      : {'ALLOW' if entry['decision'] else 'BLOCK'}")
                print(f"Risk Level    : {entry['risk']}")
                print(f"Reason        : {entry['reason']}")
                print(f"Policy        : {entry['policy']}")
                print(f"Shadow Mode   : {entry['shadow']}")
                print("----------------------------------\n")
                break
except FileNotFoundError:
    print(f"ERROR: {LOG_FILE} not found")
    sys.exit(1)

if not found:
    print(f"ERROR: Intent hash {args.intent_hash} not found in log")
    sys.exit(2)
