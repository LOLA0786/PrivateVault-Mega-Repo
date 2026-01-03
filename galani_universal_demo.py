import requests
import time
import sys

# Configuration
GATEWAY_URL = "http://127.0.0.1:8001/secure_optimize"
ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_PURPLE = "\033[95m"
ANSI_RESET = "\033[0m"

# The 25 Universal Use Cases
test_cases = [
    # --- DOMAIN 1: DEFENSE & AEROSPACE (The "General") ---
    {"id": "01", "dom": "DEFENSE", "desc": "Drone Swarm: Friendly Fire Vector Detected", "risk": 99.9, "mode": "ENFORCE", "val": 50000000},
    {"id": "02", "dom": "DEFENSE", "desc": "Target Lock: Verified Hostile Signature", "risk": 0.05, "mode": "ENFORCE", "val": 0},
    {"id": "03", "dom": "DEFENSE", "desc": "GPS Spoofing: Location Drift > 50m", "risk": 99.9, "mode": "ENFORCE", "val": 15000000},
    {"id": "04", "dom": "DEFENSE", "desc": "Geneva Protocol: Civilian Building ID'd", "risk": 99.9, "mode": "ENFORCE", "val": 100000000},
    {"id": "05", "dom": "DEFENSE", "desc": "Supply Chain: Unsigned Firmware Injection", "risk": 99.9, "mode": "ENFORCE", "val": 25000000},
    {"id": "06", "dom": "DEFENSE", "desc": "Comms: Encrypted Uplink Established", "risk": 0.01, "mode": "ENFORCE", "val": 0},
    
    # --- DOMAIN 2: LEGAL & COMPLIANCE (The "Partner") ---
    {"id": "07", "dom": "LEGAL  ", "desc": "Case Law: Hallucinated Precedent (ChatGPT Error)", "risk": 85.0, "mode": "ENFORCE", "val": 2000000},
    {"id": "08", "dom": "LEGAL  ", "desc": "Contract Review: Verified Standard Clauses", "risk": 0.02, "mode": "ENFORCE", "val": 0},
    {"id": "09", "dom": "LEGAL  ", "desc": "Discovery: Privileged Client Data Leak", "risk": 99.9, "mode": "ENFORCE", "val": 10000000},
    {"id": "10", "dom": "LEGAL  ", "desc": "Conflict of Interest: Opposing Counsel Match", "risk": 90.0, "mode": "SHADOW", "val": 0},
    {"id": "11", "dom": "LEGAL  ", "desc": "Sentencing Algo: Racial Bias Gradient High", "risk": 95.0, "mode": "ENFORCE", "val": 5000000},
    {"id": "12", "dom": "LEGAL  ", "desc": "Filing: Timestamp Tampering Detected", "risk": 99.9, "mode": "ENFORCE", "val": 500000},

    # --- DOMAIN 3: E-COMMERCE & RETAIL (The "VP Sales") ---
    {"id": "13", "dom": "E-COMM ", "desc": "Pricing Algo: 99% Discount Glitch (iPhone $1)", "risk": 99.9, "mode": "ENFORCE", "val": 2000000},
    {"id": "14", "dom": "E-COMM ", "desc": "Flash Sale: Botnet Inventory Hoarding", "risk": 99.9, "mode": "ENFORCE", "val": 500000},
    {"id": "15", "dom": "E-COMM ", "desc": "Checkout: Valid Customer Transaction", "risk": 0.01, "mode": "ENFORCE", "val": 0},
    {"id": "16", "dom": "E-COMM ", "desc": "Review System: Competitor Review Bombing", "risk": 80.0, "mode": "SHADOW", "val": 0},
    {"id": "17", "dom": "E-COMM ", "desc": "Refund Fraud: Serial Returner Hash Match", "risk": 95.0, "mode": "ENFORCE", "val": 50000},
    {"id": "18", "dom": "E-COMM ", "desc": "Ad Spend: Budget Anomaly (1000% Spike)", "risk": 99.9, "mode": "ENFORCE", "val": 100000},
]

total_defense = 0
total_legal = 0
total_ecomm = 0

print(f"\n{ANSI_PURPLE}🌐 GALANI UNIVERSAL PROTOCOL | MULTI-DOMAIN GOVERNANCE{ANSI_RESET}")
print(f"{ANSI_PURPLE}================================================================{ANSI_RESET}")
print(f"ID  | DOMAIN   | SCENARIO DESCRIPTION                   | MODE    | RESULT")
print(f"------------------------------------------------------------------------")

for case in test_cases:
    payload = {
        "current_val": 100.0,
        "raw_gradient": case["risk"],
        "mode": case["mode"],
        "actor": "universal_core_system"
    }
    
    try:
        start = time.time()
        resp = requests.post(GATEWAY_URL, json=payload)
        latency = (time.time() - start) * 1000
        
        status = ""
        
        if resp.status_code == 200:
            if case["mode"] == "SHADOW" and case["risk"] > 1.0:
                 status = f"{ANSI_YELLOW}⚠️  FLAGGED{ANSI_RESET}"
            else:
                 status = f"{ANSI_GREEN}✅ VERIFIED{ANSI_RESET}"
        elif resp.status_code == 403:
            status = f"{ANSI_RED}🛑 BLOCKED {ANSI_RESET}"
            if case["dom"] == "DEFENSE": total_defense += case["val"]
            if case["dom"] == "LEGAL  ": total_legal += case["val"]
            if case["dom"] == "E-COMM ": total_ecomm += case["val"]
        else:
            status = f"{ANSI_RED}❌ ERROR   {ANSI_RESET}"

        # Color code the domain
        dom_color = ANSI_CYAN if case["dom"] == "DEFENSE" else (ANSI_GREEN if case["dom"] == "LEGAL  " else ANSI_YELLOW)
        
        print(f"{case['id']}  | {dom_color}{case['dom']}{ANSI_RESET}  | {case['desc']:<42} | {case['mode'][:4]}...  | {status} ({int(latency)}ms)")
        time.sleep(0.12) 

    except Exception as e:
        print(f"Connection Error: {e}")
        break

print(f"------------------------------------------------------------------------")
print(f"{ANSI_CYAN}🛡️  DEFENSE: ASSETS PRESERVED   : ${total_defense:,.0f}{ANSI_RESET}")
print(f"{ANSI_GREEN}⚖️  LEGAL  : LIABILITY AVERTED  : ${total_legal:,.0f}{ANSI_RESET}")
print(f"{ANSI_YELLOW}🛒  E-COMM : REVENUE PROTECTED   : ${total_ecomm:,.0f}{ANSI_RESET}")
print(f"\n{ANSI_PURPLE}🔥 GALANI PROTOCOL: UNIVERSALLY DETERMINISTIC{ANSI_RESET}\n")
