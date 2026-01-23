import json, hmac, hashlib, os


def get_key():
    if os.path.exists("sovereign.env"):
        with open("sovereign.env", "r") as f:
            for line in f:
                if "SOVEREIGN_KERNEL_KEY=" in line:
                    return line.split("=")[1].strip().encode()
    return os.getenv("SOVEREIGN_KERNEL_KEY", "GALANI_FORCE_2026").encode()


KEY = get_key()


def verify(entry):
    try:
        msg = (
            f"{entry['actor']}|{entry['mode']}|{float(entry['gradient']):.6f}".encode()
        )
        expected = hmac.new(KEY, msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, entry["hash"])
    except:
        return False


def scan():
    print(f"\n🔍 [SOVEREIGN AUDIT VIEW] | Privacy-First Verification")
    print("-" * 115)
    if not os.path.exists("audits.worm"):
        return print("❌ EMPTY")
    with open("audits.worm", "r") as f:
        for i, line in enumerate(f):
            e = json.loads(line.strip())
            v = "✅ VERIFIED" if verify(e) else "⚠️  TAMPERED"
            p = e.get("privacy", "🔓 TRANSPARENT")
            print(
                f"[{i:03}] {v:12} | {p:15} | Actor: {e['actor']:14} | Hash: {e['hash'][:10]}..."
            )
    print("-" * 115)


if __name__ == "__main__":
    scan()
