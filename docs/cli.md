# PrivateVault CLI v1

The `pv` CLI is a thin operator interface built directly on API v1.

## Installation (Local)
```bash
python cli/pv.py --help
```

## Login
```bash
python cli/pv.py login --token <SERVICE_TOKEN> --api-url http://localhost:8000/api/v1
```

Credentials are stored at `~/.privatevault/credentials.json` with restrictive file permissions.

## Commands
- `pv status`
- `pv tenant create --tenant-id <id> --name <name> [--region <region>]`
- `pv tenant list`
- `pv quorum get`
- `pv quorum set --file <rules.json>` or `pv quorum set --json '{...}'`
- `pv approvals list [--tenant-id <id>] [--start <iso>] [--end <iso>]`
- `pv evidence export --tenant-id <id> --start <iso> --end <iso> [--bundle-name <name>]`
- `pv demo up [--root <path>] [--demo-mode]`

## Output Formats
Use `--format json` for machine-readable output.

## Autocomplete

**bash**
```bash
source cli/completions/pv.bash
```

**zsh**
```zsh
source cli/completions/pv.zsh
```

## Notes
- The CLI uses service tokens and scopes enforced by API v1.
- All operations are tenant-scoped when the token is tenant-bound.
