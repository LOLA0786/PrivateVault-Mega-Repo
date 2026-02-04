import argparse
import json
import sys

from evidence_export import export_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="PrivateVault compliance evidence export")
    parser.add_argument("--tenant", required=True, help="Tenant identifier")
    parser.add_argument("--from", dest="start", required=True, help="Start time (ISO8601)")
    parser.add_argument("--to", dest="end", required=True, help="End time (ISO8601)")
    parser.add_argument("--bundle-name", dest="bundle_name", help="Optional bundle name")
    args = parser.parse_args()

    try:
        result = export_bundle(
            tenant_id=args.tenant,
            start_iso=args.start,
            end_iso=args.end,
            bundle_name=args.bundle_name,
        )
    except Exception as exc:
        print(f"export failed: {exc}", file=sys.stderr)
        return 1

    payload = {
        "bundle_id": result.bundle_id,
        "bundle_path": result.bundle_path,
        "manifest_hash": result.manifest_hash,
        "verified": result.verified,
        "warnings": result.warnings,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
