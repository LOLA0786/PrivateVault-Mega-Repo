from fastapi import APIRouter, HTTPException
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parents[2]
POLICY_DIR = BASE_DIR / "policy_store" / "tenants"

router = APIRouter(prefix="/gateway/admin", tags=["gateway-admin"])

VALID_MODES = {"monitor", "shadow", "strict"}

@router.post("/set-mode")
def set_mode(tenant_id: str, mode: str):
    if mode not in VALID_MODES:
        raise HTTPException(status_code=400, detail="INVALID_MODE")

    policy_path = POLICY_DIR / f"{tenant_id}.yaml"

    if not policy_path.exists():
        raise HTTPException(status_code=404, detail="TENANT_POLICY_NOT_FOUND")

    with open(policy_path, "r") as f:
        policy = yaml.safe_load(f)

    policy["mode"] = mode

    with open(policy_path, "w") as f:
        yaml.safe_dump(policy, f)

    return {
        "tenant_id": tenant_id,
        "new_mode": mode,
        "status": "updated"
    }
