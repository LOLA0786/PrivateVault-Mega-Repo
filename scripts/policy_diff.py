import yaml
import sys
from deepdiff import DeepDiff
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_STORE = BASE_DIR / "policy_store" / "tenants"

def load_yaml(path: Path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def diff_policies(old_name: str, new_name: str):
    old_path = POLICY_STORE / old_name
    new_path = POLICY_STORE / new_name

    if not old_path.exists():
        raise FileNotFoundError(f"Missing policy: {old_path}")
    if not new_path.exists():
        raise FileNotFoundError(f"Missing policy: {new_path}")

    old_policy = load_yaml(old_path)
    new_policy = load_yaml(new_path)

    diff = DeepDiff(old_policy, new_policy, ignore_order=True)

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "old_policy": old_name,
        "new_policy": new_name,
        "diff": diff.to_dict(),
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: policy_diff.py <old_policy.yaml> <new_policy.yaml>")
        sys.exit(1)

    result = diff_policies(sys.argv[1], sys.argv[2])
    print(yaml.dump(result, sort_keys=False))
