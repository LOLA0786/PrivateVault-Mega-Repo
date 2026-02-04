import json
from typing import Any, Iterable


def print_json(payload: Any):
    print(json.dumps(payload, indent=2, sort_keys=True))


def print_table(rows: Iterable[dict], columns: list[str]):
    rows = list(rows)
    if not rows:
        print("(empty)")
        return
    widths = {col: max(len(col), *(len(str(row.get(col, ""))) for row in rows)) for col in columns}
    header = "  ".join(col.ljust(widths[col]) for col in columns)
    print(header)
    print("  ".join("-" * widths[col] for col in columns))
    for row in rows:
        print("  ".join(str(row.get(col, "")).ljust(widths[col]) for col in columns))
