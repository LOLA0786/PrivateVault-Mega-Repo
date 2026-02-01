import sys, requests, time
from fastapi import FastAPI
from contextlib import asynccontextmanager

# 🔒 CONFIGURATION (Injected via Environment Variables in Prod)
LICENSE_KEY = "LICENSE_TEST_TRIAL"
LICENSE_SERVER_URL = "http://localhost:9000/verify_license"  # Points to YOUR server


# 🛡️ THE PHONE HOME PROTOCOL
def validate_license():
    print(f"📡 CONNECTING TO MOTHER_SHIP: Verifying License {LICENSE_KEY}...")
    try:
        response = requests.post(
            LICENSE_SERVER_URL, json={"license_key": LICENSE_KEY}, timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ LICENSE VERIFIED: Welcome, {data['client']}!")
            return True
        else:
            print(f"❌ LICENSE DENIED: {response.text}")
            sys.exit(1)  # KILL THE SERVER
    except Exception as e:
        print(f"⚠️ CONNECTION FAILED: Could not reach License Server. {e}")
        sys.exit(1)  # FAIL SECURE


# Startup Event
@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_license()  # Check on startup
    yield


app = FastAPI(lifespan=lifespan, title="Galani Enterprise [PROTECTED]")


@app.get("/system_status")
def status():
    return {"status": "OPERATIONAL", "license": "VERIFIED"}


if __name__ == "__main__":
    import uvicorn

    # Only runs if license check passes
    uvicorn.run(app, host="0.0.0.0", port=8080)
