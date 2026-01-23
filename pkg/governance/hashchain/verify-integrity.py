import hashlib, json, sys


def verify_chain(logfile):
    prev_hash = "0000000000"
    line_count = 0
    with open(logfile, "r") as f:
        for line in f:
            data = json.loads(line)
            # Recompute what the hash SHOULD be
            check_string = f"{data['action']}{data['user']}{data['nonce']}{prev_hash}"
            expected_hash = hashlib.sha256(check_string.encode()).hexdigest()

            if data["hash"] != expected_hash:
                print(f"❌ TAMPERING DETECTED at Line {line_count}!")
                return False

            prev_hash = data["hash"]
            line_count += 1
    print(f"✅ INTEGRITY VERIFIED: {line_count} decisions checked.")
    return True


if __name__ == "__main__":
    verify_chain(sys.argv[1])
