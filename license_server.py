from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime

app = FastAPI(title="Galani License Authority")

# 📝 THE LEDGER OF PAID CLIENTS (In prod, use a Database)
VALID_LICENSES = {
    "LICENSE_STRIPE_001": {
        "client": "Stripe",
        "expires": "2030-01-01",
        "status": "ACTIVE",
    },
    "LICENSE_HEDGE_FUND_X": {
        "client": "HedgeFundX",
        "expires": "2026-12-31",
        "status": "ACTIVE",
    },
    "LICENSE_TEST_TRIAL": {
        "client": "TrialUser",
        "expires": "2026-02-01",
        "status": "ACTIVE",
    },
}


class LicenseCheck(BaseModel):
    license_key: str


@app.post("/verify_license")
def verify(data: LicenseCheck):
    key = data.license_key

    # 1. Check if key exists
    if key not in VALID_LICENSES:
        raise HTTPException(status_code=403, detail="INVALID LICENSE KEY")

    info = VALID_LICENSES[key]

    # 2. Check Expiry
    expiry_date = datetime.datetime.strptime(info["expires"], "%Y-%m-%d")
    if datetime.datetime.now() > expiry_date:
        raise HTTPException(status_code=403, detail="LICENSE EXPIRED - PLEASE RENEW")

    # 3. Check Status
    if info["status"] != "ACTIVE":
        raise HTTPException(status_code=403, detail="LICENSE REVOKED")

    return {"status": "VALID", "client": info["client"], "valid_until": info["expires"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
