import json
import os

from audit_logger import get_audit_log_paths


def read_recent_audits(limit=50):
    entries = []

    for path in get_audit_log_paths():
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
