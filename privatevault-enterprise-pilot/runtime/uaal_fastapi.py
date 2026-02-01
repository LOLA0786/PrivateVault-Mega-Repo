from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"service": "galani", "status": "running"}


# ============================
# Pilot API Key Authentication
# ============================
from fastapi import Header, HTTPException, Depends
import inspect, os

PILOT_API_KEYS = {
    "pilot_acme_001",
    "pilot_kaggle_002",
    "pilot_demo_003",
}


def require_api_key(x_api_key: str = Header(None)):
    if x_api_key not in PILOT_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/__whoami")
def whoami():
    return {"file": inspect.getfile(whoami), "cwd": os.getcwd()}


# ============================
# Shadow Verify (mounted explicitly)
# ============================
from governance import verify as shadow_verify

app.post("/api/v1/shadow_verify", dependencies=[Depends(require_api_key)])(
    shadow_verify
)
