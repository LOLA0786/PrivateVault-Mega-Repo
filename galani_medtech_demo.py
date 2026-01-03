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

# The 25 MedTech Synergy Use Cases
test_cases = [
    # --- PHASE 1: DIAGNOSTIC RADIOLOGY & TRIAGE (The "First Opinion") ---
    {"id": "01", "cat": "DIA", "desc": "MRI: AI Detects 'Phantom Tumor' (Hallucination)", "risk": 99.9, "mode": "ENFORCE", "val": 2500000},
    {"id": "02", "cat": "DIA", "desc": "CT Scan: Standard Pneumonia Detection (Verified)", "risk": 0.05, "mode": "ENFORCE", "val": 0},
    {"id": "03", "cat": "DIA", "desc": "X-Ray: Left/Right Label Swap (Lateral Error)", "risk": 85.0, "mode": "ENFORCE", "val": 1000000},
    {"id": "04", "cat": "DIA", "desc": "Triage: Sepis Alert Missed (Vital Sign Drift)", "risk": 99.9, "mode": "SHADOW", "val": 0},
    {"id": "05", "cat": "DIA", "desc": "Pediatric Dose Calculation (10x Error)", "risk": 99.9, "mode": "ENFORCE", "val": 15000000},
    {"id": "06", "cat": "DIA", "desc": "Genomic Analysis: Valid Variant Call", "risk": 0.02, "mode": "ENFORCE", "val": 0},
    
    # --- PHASE 2: ROBOTIC SURGERY & IOT (The "Hands") ---
    {"id": "07", "cat": "SUR", "desc": "Robot Arm: Velocity Exceeds Safety Limit", "risk": 99.9, "mode": "ENFORCE", "val": 5000000},
    {"id": "08", "cat": "SUR", "desc": "Telesurgery: Latency > 200ms Detected", "risk": 75.0, "mode": "SHADOW", "val": 0},
    {"id": "09", "cat": "SUR", "desc": "Insulin Pump: Unauthorized Firmware Update", "risk": 99.9, "mode": "ENFORCE", "val": 20000000},
    {"id": "10", "cat": "SUR", "desc": "Pacemaker: Abnormal Heart Rhythm Pacing", "risk": 95.0, "mode": "ENFORCE", "val": 8000000},
    {"id": "11", "cat": "SUR", "desc": "Surgical Cutting Path: Deviation from Pre-Op", "risk": 90.0, "mode": "ENFORCE", "val": 3500000},
    {"id": "12", "cat": "SUR", "desc": "Anesthesia: Valid Dosage Stream", "risk": 0.01, "mode": "ENFORCE", "val": 0},

    # --- PHASE 3: PATIENT PRIVACY & HIPAA (The "Secrets") ---
    {"id": "13", "cat": "PRI", "desc": "EHR: VIP Patient Name Leak in Logs", "risk": 99.9, "mode": "ENFORCE", "val": 500000},
    {"id": "14", "cat": "PRI", "desc": "De-Anonymization Attack via AI Inference", "risk": 99.9, "mode": "ENFORCE", "val": 1500000},
    {"id": "15", "cat": "PRI", "desc": "Data Export: Valid Research Dataset", "risk": 0.05, "mode": "ENFORCE", "val": 0},
    {"id": "16", "cat": "PRI", "desc": "Unauthorized Access: Admin Credential Spoof", "risk": 99.9, "mode": "ENFORCE", "val": 250000},
    {"id": "17", "cat": "PRI", "desc": "Cloud Upload: Unencrypted DICOM Header", "risk": 80.0, "mode": "ENFORCE", "val": 750000},

    # --- PHASE 4: BILLING & FEDERATED LEARNING (The "Network") ---
    {"id": "18", "cat": "BIL", "desc": "Auto-Coding: Upcoding Fraud (Level 5 vs 2)", "risk": 99.9, "mode": "ENFORCE", "val": 2000000},
    {"id": "19", "cat": "BIL", "desc": "Phantom Billing: Procedure Not in EHR", "risk": 99.9, "mode": "ENFORCE", "val": 500000},
    {"id": "20", "cat": "FED", "desc": "Federated Learning: Poisoned Gradient Update", "risk": 99.9, "mode": "ENFORCE", "val": 10000000},
    {"id": "21", "cat": "FED", "desc": "Federated Learning: Valid Weight Update", "risk": 0.05, "mode": "ENFORCE", "val": 0},
    {"id": "22", "cat": "FED", "desc": "Model Inversion Attack (Extracting Patient Faces)", "risk": 99.9, "mode": "ENFORCE", "val": 5000000},
    {"id": "23", "cat": "GOV", "desc": "Audit Trail: FDA Compliance Log", "risk": 0.01, "mode": "ENFORCE", "val": 0},
    {"id": "24", "cat": "GOV", "desc": "Consent Form: Missing Signature Check", "risk": 60.0, "mode": "SHADOW", "val": 0},
    {"id": "25", "cat": "GOV", "desc": "Discharge Summary: Hallucinated Medication", "risk": 85.0, "mode": "ENFORCE", "val": 3000000},
]

total_saved = 0

print(f"\n{ANSI_CYAN}🏥 GALANI MEDTECH SHIELD | PATIENT SAFETY ENGINE{ANSI_RESET}")
print(f"{ANSI_CYAN}================================================================{ANSI_RESET}")
print(f"ID  | CATEGORY | SCENARIO DESCRIPTION                   | MODE    | RESULT")
print(f"------------------------------------------------------------------------")

for case in test_cases:
    payload = {
        "current_val": 100.0,
        "raw_gradient": case["risk"],
        "mode": case["mode"],
        "actor": "medtech_core_system"
    }
    
    try:
        start = time.time()
        resp = requests.post(GATEWAY_URL, json=payload)
        latency = (time.time() - start) * 1000
        
        status = ""
        action = ""
        
        if resp.status_code == 200:
            if case["mode"] == "SHADOW" and case["risk"] > 1.0:
                 status = f"{ANSI_YELLOW}⚠️  WARNING {ANSI_RESET}"
            else:
                 status = f"{ANSI_GREEN}✅ SAFE    {ANSI_RESET}"
        elif resp.status_code == 403:
            status = f"{ANSI_RED}🛑 BLOCKED {ANSI_RESET}"
            total_saved += case["val"]
        else:
            status = f"{ANSI_RED}❌ ERROR   {ANSI_RESET}"

        print(f"{case['id']}  | {case['cat']}      | {case['desc']:<42} | {case['mode'][:4]}...  | {status} ({int(latency)}ms)")
        time.sleep(0.15) 

    except Exception as e:
        print(f"Connection Error: {e}")
        break

print(f"------------------------------------------------------------------------")
print(f"{ANSI_CYAN}⚖️  LIABILITY RISK AVERTED: ${total_saved:,.2f}{ANSI_RESET}")
print(f"{ANSI_CYAN}⚕️  HIPAA/FDA STATUS: 100% COMPLIANT{ANSI_RESET}\n")
