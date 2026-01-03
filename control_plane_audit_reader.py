import json
import os

DEFAULT_LOG_FILES = [
    "audit.log",
    "logs.json",
    "logs-test.json",
    "logs-medtech.json",
]

def read_recent_audits(limit=50):
    entries = []

    for path in DEFAULT_LOG_FILES:
        if not os.path.exists(path):
            continue

        try:
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        continue
        except Exception:
            continue

    # newest first
    return entries[-limit:]
