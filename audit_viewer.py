import json, hmac, hashlib, os

def get_kernel_key():
    if os.path.exists("sovereign.env"):
        with open("sovereign.env", "r") as f:
            for line in f:
                if "SOVEREIGN_KERNEL_KEY=" in line:
                    return line.split("=")[1].strip().encode()
    return os.getenv("SOVEREIGN_KERNEL_KEY", "MUMBAI_FORCE_2026").encode()

KERNEL_KEY = get_kernel_key()

def verify_log_integrity(entry):
    try:
        # 🎯 MATCH THE STRING NORMALIZATION EXACTLY
        msg = f"{entry['actor']}|{entry['mode']}|{float(entry['gradient']):.6f}".encode()
        expected_hash = hmac.new(KERNEL_KEY, msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_hash, entry["hash"])
    except:
        return False

def scan_audit_trail():
    print(f"\n🔍 [SOVEREIGN AUDIT VIEW] | Key: {KERNEL_KEY.decode()[:4]}****")
    print("-" * 95)
    if not os.path.exists("audits.worm"):
        print("❌ ERROR: No audit trail found.")
        return
    with open("audits.worm", "r") as f:
        for i, line in enumerate(f):
            entry = json.loads(line.strip())
            is_valid = verify_log_integrity(entry)
            status = "✅ VERIFIED" if is_valid else "⚠️  UNVERIFIABLE"
            risk = "⚠️ HIGH" if entry["gradient"] > 1.0 else "🟢 SAFE"
            print(f"[{i:03}] {status:12} | {entry['timestamp']} | Actor: {entry['actor']:12} | Risk: {risk:7} | Hash: {entry['hash'][:12]}...")
    print("-" * 95)
    print("✅ ANALYSIS COMPLETE.")

if __name__ == "__main__":
    scan_audit_trail()
