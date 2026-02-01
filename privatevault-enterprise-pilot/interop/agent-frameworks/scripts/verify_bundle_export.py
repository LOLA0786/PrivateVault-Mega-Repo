import os, tarfile, hashlib, time

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def nowstamp():
    return time.strftime("%Y%m%d_%H%M%SZ", time.gmtime())

def main():
    outdir = "reports/vv"
    os.makedirs(outdir, exist_ok=True)
    ts = nowstamp()

    bundle = os.path.join(outdir, f"verify_bundle_{ts}.tar.gz")
    sha_file = os.path.join(outdir, f"verify_bundle_{ts}.sha256")

    include = [
        "privatevault/reports/evidence",
        "reports/vv",
        "tests",
        "privatevault",
    ]

    with tarfile.open(bundle, "w:gz") as tar:
        for p in include:
            if os.path.exists(p):
                tar.add(p)

    digest = sha256_file(bundle)
    with open(sha_file, "w", encoding="utf-8") as f:
        f.write(f"{digest}  {bundle}\n")

    print("==============================================================================")
    print("PrivateVault Verify - Evidence Bundle Export + Integrity Hash")
    print("==============================================================================")
    print(f"UTC Timestamp: {ts}")
    print(f"Bundle: {bundle}")
    print(f"Bundle SHA256: {digest}")
    print(f"SHA file: {sha_file}")
    print("")
    print("To verify integrity later:")
    print(f"  sha256sum -c {sha_file}")
    print("==============================================================================")

if __name__ == "__main__":
    main()
