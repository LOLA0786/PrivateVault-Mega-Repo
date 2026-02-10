import yaml
from pathlib import Path
from datetime import datetime
from deepdiff import DeepDiff


def find_repo_root(start: Path) -> Path:
    current = start
    while current != current.parent:
        if (current / ".git").exists() or (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Repo root not found")


BASE_DIR = find_repo_root(Path(__file__).resolve())

POLICY_STORE = BASE_DIR / "policy_store" / "tenants"
AUDIT_LOG = BASE_DIR / "policy_store" / "policy_audit.log"


def _load_yaml(path: Path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def record_policy_change(old_policy: str, new_policy: str):
    old_path = POLICY_STORE / old_policy
    new_path = POLICY_STORE / new_policy

    if not old_path.exists():
        raise FileNotFoundError(f"Missing old policy: {old_path}")
    if not new_path.exists():
        raise FileNotFoundError(f"Missing new policy: {new_path}")

    diff = DeepDiff(
        _load_yaml(old_path),
        _load_yaml(new_path),
        ignore_order=True,
    ).to_dict()

    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "old_policy": old_policy,
        "new_policy": new_policy,
        "diff": diff,
    }

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

    with open(AUDIT_LOG, "a") as f:
        f.write(yaml.dump(record, sort_keys=False))
        f.write("\n---\n")

    return record

# -------------------------------
# Public read API
# -------------------------------

def read_policy_audit_log(limit: int = 100):
    """
    Read recent policy change audit events.
    """
    if not AUDIT_LOG.exists():
        return []

    events = []
    with open(AUDIT_LOG, "r") as f:
        for line in f.readlines()[-limit:]:
            try:
                events.append(json.loads(line))
            except Exception:
                continue

    return events
