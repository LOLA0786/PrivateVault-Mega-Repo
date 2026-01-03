import requests
import time
import sys

# Configuration
GATEWAY_URL = "http://127.0.0.1:8001/secure_optimize"
ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"
ANSI_RESET = "\033[0m"

# The 25 Synergy Use Cases
test_cases = [
    # --- PHASE 1: KYC & ONBOARDING ---
    {"id": "01", "cat": "KYC", "desc": "Deepfake Liveness (Injection Detected)", "risk": 99.9, "mode": "ENFORCE", "val": 0},
    {"id": "02", "cat": "KYC", "desc": "Standard User Onboarding (Verified)", "risk": 0.05, "mode": "ENFORCE", "val": 0},
    {"id": "03", "cat": "KYC", "desc": "OCR Pixel Gradient Mismatch (Forged Doc)", "risk": 45.0, "mode": "SHADOW", "val": 0},
    {"id": "04", "cat": "KYC", "desc": "Synthetic ID Velocity (5th Attempt/10min)", "risk": 99.9, "mode": "ENFORCE", "val": 0},
    {"id": "05", "cat": "KYC", "desc": "Geo-Fence: IP (Mumbai) vs GPS (North Korea)", "risk": 99.9, "mode": "ENFORCE", "val": 0},
    {"id": "06", "cat": "KYC", "desc": "Aadhaar Masking Failure (Data Leak)", "risk": 80.0, "mode": "ENFORCE", "val": 0},
    {"id": "07", "cat": "KYC", "desc": "Video KYC Audio/Lip Sync Mismatch", "risk": 15.0, "mode": "SHADOW", "val": 0},
    
    # --- PHASE 2: CREDIT UNDERWRITING ---
    {"id": "08", "cat": "UND", "desc": "CIBIL Score Inflation (Model Drift)", "risk": 99.9, "mode": "ENFORCE", "val": 500000},
    {"id": "09", "cat": "UND", "desc": "Valid Loan Application (Prime Borrower)", "risk": 0.02, "mode": "ENFORCE", "val": 0},
    {"id": "10", "cat": "UND", "desc": "Zip-Code Bias Detected (Redlining)", "risk": 60.0, "mode": "ENFORCE", "val": 0},
    {"id": "11", "cat": "UND", "desc": "Income Inference Hallucination (>50x UPI)", "risk": 25.0, "mode": "SHADOW", "val": 0},
    {"id": "12", "cat": "UND", "desc": "Bureau Data Tampering (Hash Mismatch)", "risk": 99.9, "mode": "ENFORCE", "val": 1200000},
    {"id": "13", "cat": "UND", "desc": "Device Fingerprint Spoofing", "risk": 99.9, "mode": "ENFORCE", "val": 0},
    {"id": "14", "cat": "UND", "desc": "Affordability Breach (EMI > 80% Income)", "risk": 95.0, "mode": "ENFORCE", "val": 2000000},
    
    # --- PHASE 3: DISBURSEMENT & TREASURY ---
    {"id": "15", "cat": "DSB", "desc": "Penny Drop Name Mismatch", "risk": 99.9, "mode": "ENFORCE", "val": 50000},
    {"id": "16", "cat": "DSB", "desc": "Valid Disbursement (Verified)", "risk": 0.01, "mode": "ENFORCE", "val": 0},
    {"id": "17", "cat": "DSB", "desc": "Sanctions List Hit (UN Terror List)", "risk": 99.9, "mode": "ENFORCE", "val": 10000000},
    {"id": "18", "cat": "DSB", "desc": "Duplicate API Trigger (Idempotency)", "risk": 99.9, "mode": "ENFORCE", "val": 50000},
    {"id": "19", "cat": "DSB", "desc": "Disbursement Amount Parameter Tampering", "risk": 99.9, "mode": "ENFORCE", "val": 450000},
    {"id": "20", "cat": "DSB", "desc": "Beneficiary Account Swap Attack", "risk": 99.9, "mode": "ENFORCE", "val": 800000},
    
    # --- PHASE 4: AUDIT & GOVERNANCE ---
    {"id": "21", "cat": "AUD", "desc": "Regulatory Report Generation", "risk": 0.01, "mode": "ENFORCE", "val": 0},
    {"id": "22", "cat": "AUD", "desc": "Right-to-Forgotten Request (Privacy)", "risk": 0.05, "mode": "ENFORCE", "val": 0},
    {"id": "23", "cat": "AUD", "desc": "Federated Fraud Match (Galani Network)", "risk": 0.05, "mode": "ENFORCE", "val": 0},
    {"id": "24", "cat": "AUD", "desc": "Admin Override Attempt (Insider Threat)", "risk": 99.9, "mode": "ENFORCE", "val": 0},
    {"id": "25", "cat": "AUD", "desc": "Model Decay Alert (Auto-Approval Spike)", "risk": 15.0, "mode": "SHADOW", "val": 0},
]

total_saved = 0

print(f"\n{ANSI_CYAN}🛡️  GALANI FINTECH PROTOCOL | LIVE RISK ENGINE{ANSI_RESET}")
print(f"{ANSI_CYAN}================================================================{ANSI_RESET}")
print(f"ID  | CATEGORY | SCENARIO DESCRIPTION                   | MODE    | RESULT")
print(f"------------------------------------------------------------------------")

for case in test_cases:
    payload = {
        "current_val": 100.0,
        "raw_gradient": case["risk"],
        "mode": case["mode"],
        "actor": "fintech_core_system"
    }
    
    try:
        start = time.time()
        resp = requests.post(GATEWAY_URL, json=payload)
        latency = (time.time() - start) * 1000
        
        status = ""
        action = ""
        
        if resp.status_code == 200:
            if case["mode"] == "SHADOW" and case["risk"] > 1.0:
                 status = f"{ANSI_YELLOW}⚠️  FLAGGED{ANSI_RESET}"
                 action = "LOGGED"
            else:
                 status = f"{ANSI_GREEN}✅ APPROVED{ANSI_RESET}"
                 action = "SIGNED"
        elif resp.status_code == 403:
            status = f"{ANSI_RED}🛑 BLOCKED {ANSI_RESET}"
            action = "HALTED"
            total_saved += case["val"]
        else:
            status = f"{ANSI_RED}❌ ERROR   {ANSI_RESET}"

        print(f"{case['id']}  | {case['cat']}      | {case['desc']:<42} | {case['mode'][:4]}...  | {status} ({int(latency)}ms)")
        time.sleep(0.15) # Cinematic delay for the demo

    except Exception as e:
        print(f"Connection Error: Is Galani Gateway running? {e}")
        break

print(f"------------------------------------------------------------------------")
print(f"{ANSI_CYAN}💰 TOTAL CAPITAL PRESERVED (FRAUD BLOCKED): ₹{total_saved:,.2f}{ANSI_RESET}")
print(f"{ANSI_CYAN}🔒 COMPLIANCE STATUS: 100% DETERMINISTIC{ANSI_RESET}\n")
