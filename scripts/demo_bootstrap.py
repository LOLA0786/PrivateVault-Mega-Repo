import argparse
import json
import os
import shutil
from typing import Dict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_DIR = os.path.join(REPO_ROOT, "demo")

ASSETS = {
    "tenant-configs": "tenant-configs/tenant-demo.json",
    "quorum-rules": "quorum-rules/demo-quorum.json",
    "context-keys": "context-keys/demo-context-keys.json",
    "policies": "policies/demo-policies.json",
    "audit-events": "audit-events/audit-demo.jsonl",
    "approvals": "approvals/demo-approvals.jsonl",
    "decision-ledger": "decision-ledger/demo-ledger.jsonl",
}


def _read_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write_env(path: str, env: Dict[str, str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for key, value in env.items():
            f.write(f"{key}='{value}'\n")


def bootstrap(root: str, demo_mode: bool) -> str:
    root = os.path.realpath(root)
    os.makedirs(root, exist_ok=True)

    # Copy assets into demo root
    shutil.copyfile(
        os.path.join(DEMO_DIR, ASSETS["tenant-configs"]),
        os.path.join(root, "tenant-demo.json"),
    )
    shutil.copyfile(
        os.path.join(DEMO_DIR, ASSETS["quorum-rules"]),
        os.path.join(root, "quorum-rules.json"),
    )
    shutil.copyfile(
        os.path.join(DEMO_DIR, ASSETS["context-keys"]),
        os.path.join(root, "context-keys.json"),
    )
    shutil.copyfile(
        os.path.join(DEMO_DIR, ASSETS["policies"]),
        os.path.join(root, "policies.json"),
    )
    shutil.copyfile(
        os.path.join(DEMO_DIR, ASSETS["audit-events"]),
        os.path.join(root, "audit.log"),
    )
    shutil.copyfile(
        os.path.join(DEMO_DIR, ASSETS["approvals"]),
        os.path.join(root, "approvals.jsonl"),
    )
    shutil.copyfile(
        os.path.join(DEMO_DIR, ASSETS["decision-ledger"]),
        os.path.join(root, "decision-ledger.jsonl"),
    )

    os.makedirs(os.path.join(root, "exports"), exist_ok=True)

    context_keys = _read_text(os.path.join(root, "context-keys.json")).strip()
    quorum_rules = _read_text(os.path.join(root, "quorum-rules.json")).strip()

    env = {
        "PV_DEMO_ROOT": root,
        "PV_AUDIT_LOG_PATH": os.path.join(root, "audit.log"),
        "PV_AUDIT_LOG_PATHS": os.path.join(root, "audit.log"),
        "PV_CONTEXT_KEYS": context_keys,
        "PV_QUORUM_RULES_V2": quorum_rules,
        "PV_EXPORT_ROOT": os.path.join(root, "exports"),
        "PV_DECISION_LEDGER_PATH": os.path.join(root, "decision-ledger.jsonl"),
    }
    if demo_mode:
        env["PV_DEMO_MODE"] = "1"

    env_path = os.path.join(root, ".env.demo")
    _write_env(env_path, env)
    return env_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap PrivateVault demo assets")
    parser.add_argument(
        "--root",
        default=os.path.join(REPO_ROOT, ".demo"),
        help="Demo root directory (default: .demo in repo)",
    )
    parser.add_argument(
        "--demo-mode",
        action="store_true",
        help="Include PV_DEMO_MODE=1 in generated env",
    )
    args = parser.parse_args()

    env_path = bootstrap(args.root, args.demo_mode)
    print("Demo bootstrap complete.")
    print(f"Env file: {env_path}")
    print("Next:")
    print("  1) source the env file")
    print("  2) run the control plane from the repo root or demo root")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
