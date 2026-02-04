import argparse
import json
import sys

from cli.client import APIClient
from cli.config import CLIConfig, load_config, save_config
from cli.demo import run_demo_bootstrap
from cli.output import print_json, print_table


def _require_token(config: CLIConfig):
    if not config.token:
        print("not logged in: run pv login --token <token>", file=sys.stderr)
        raise SystemExit(1)


def cmd_login(args):
    config = load_config()
    api_url = args.api_url or config.api_url
    config = CLIConfig(api_url=api_url, token=args.token)
    path = save_config(config)
    if args.format == "json":
        print_json({"status": "ok", "config_path": path, "api_url": api_url})
    else:
        print(f"logged in. config saved: {path}")


def cmd_status(args):
    config = load_config()
    client = APIClient(config)
    resp = client.request("GET", "/status")
    payload = resp.json()
    if args.format == "json":
        print_json(payload)
    else:
        print(f"status: {payload.get('status')}")
        print(f"version: {payload.get('version')}")


def cmd_tenant_create(args):
    config = load_config()
    _require_token(config)
    client = APIClient(config)
    payload = {"tenant_id": args.tenant_id, "name": args.name, "region": args.region}
    resp = client.request("POST", "/tenants", json_body=payload)
    data = resp.json()
    if args.format == "json":
        print_json(data)
    else:
        print(f"created tenant: {data.get('tenant_id')}")


def cmd_tenant_list(args):
    config = load_config()
    _require_token(config)
    client = APIClient(config)
    resp = client.request("GET", "/tenants")
    data = resp.json()
    if args.format == "json":
        print_json(data)
    else:
        print_table(data, ["tenant_id", "name", "region"])


def cmd_quorum_get(args):
    config = load_config()
    _require_token(config)
    client = APIClient(config)
    resp = client.request("GET", "/quorum/rules")
    data = resp.json()
    if args.format == "json":
        print_json(data)
    else:
        print_json(data)


def cmd_quorum_set(args):
    config = load_config()
    _require_token(config)
    client = APIClient(config)
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            rules = json.load(f)
    else:
        rules = json.loads(args.json)
    resp = client.request("PUT", "/quorum/rules", json_body={"rules": rules})
    data = resp.json()
    if args.format == "json":
        print_json(data)
    else:
        print("quorum rules updated")


def cmd_approvals_list(args):
    config = load_config()
    _require_token(config)
    client = APIClient(config)
    params = {}
    if args.tenant_id:
        params["tenant_id"] = args.tenant_id
    if args.start:
        params["start"] = args.start
    if args.end:
        params["end"] = args.end
    resp = client.request("GET", "/approvals", params=params)
    data = resp.json()
    if args.format == "json":
        print_json(data)
    else:
        print_table(data, ["approval_id", "approver_id", "role", "region", "intent_hash", "timestamp"])


def cmd_evidence_export(args):
    config = load_config()
    _require_token(config)
    client = APIClient(config)
    payload = {
        "tenant_id": args.tenant_id,
        "start": args.start,
        "end": args.end,
        "bundle_name": args.bundle_name,
    }
    resp = client.request("POST", "/evidence/export", json_body=payload)
    data = resp.json()
    if args.format == "json":
        print_json(data)
    else:
        print(f"bundle_id: {data.get('bundle_id')}")
        print(f"bundle_path: {data.get('bundle_path')}")
        print(f"manifest_hash: {data.get('manifest_hash')}")


def cmd_demo_up(args):
    env_path = run_demo_bootstrap(args.root, args.demo_mode)
    if args.format == "json":
        print_json({"status": "ok", "env_path": env_path})
    else:
        print(f"demo ready. env file: {env_path}")


def build_parser():
    parser = argparse.ArgumentParser(prog="pv", description="PrivateVault CLI v1")
    parser.add_argument("--format", choices=["human", "json"], default="human")

    sub = parser.add_subparsers(dest="command")

    login = sub.add_parser("login")
    login.add_argument("--token", required=True)
    login.add_argument("--api-url")
    login.set_defaults(func=cmd_login)

    status = sub.add_parser("status")
    status.set_defaults(func=cmd_status)

    tenant = sub.add_parser("tenant")
    tenant_sub = tenant.add_subparsers(dest="tenant_cmd")

    tenant_create = tenant_sub.add_parser("create")
    tenant_create.add_argument("--tenant-id", required=True)
    tenant_create.add_argument("--name", required=True)
    tenant_create.add_argument("--region")
    tenant_create.set_defaults(func=cmd_tenant_create)

    tenant_list = tenant_sub.add_parser("list")
    tenant_list.set_defaults(func=cmd_tenant_list)

    quorum = sub.add_parser("quorum")
    quorum_sub = quorum.add_subparsers(dest="quorum_cmd")

    quorum_get = quorum_sub.add_parser("get")
    quorum_get.set_defaults(func=cmd_quorum_get)

    quorum_set = quorum_sub.add_parser("set")
    group = quorum_set.add_mutually_exclusive_group(required=True)
    group.add_argument("--file")
    group.add_argument("--json")
    quorum_set.set_defaults(func=cmd_quorum_set)

    approvals = sub.add_parser("approvals")
    approvals_sub = approvals.add_subparsers(dest="approvals_cmd")

    approvals_list = approvals_sub.add_parser("list")
    approvals_list.add_argument("--tenant-id")
    approvals_list.add_argument("--start")
    approvals_list.add_argument("--end")
    approvals_list.set_defaults(func=cmd_approvals_list)

    evidence = sub.add_parser("evidence")
    evidence_sub = evidence.add_subparsers(dest="evidence_cmd")

    evidence_export = evidence_sub.add_parser("export")
    evidence_export.add_argument("--tenant-id", required=True)
    evidence_export.add_argument("--start", required=True)
    evidence_export.add_argument("--end", required=True)
    evidence_export.add_argument("--bundle-name")
    evidence_export.set_defaults(func=cmd_evidence_export)

    demo = sub.add_parser("demo")
    demo_sub = demo.add_subparsers(dest="demo_cmd")

    demo_up = demo_sub.add_parser("up")
    demo_up.add_argument("--root")
    demo_up.add_argument("--demo-mode", action="store_true")
    demo_up.set_defaults(func=cmd_demo_up)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
