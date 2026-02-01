import os, glob, hashlib, time

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def nowstamp():
    return time.strftime("%Y%m%d_%H%M%SZ", time.gmtime())

def main():
    outdir = "reports/vv"
    os.makedirs(outdir, exist_ok=True)
    ts = nowstamp()
    manifest_path = os.path.join(outdir, f"evidence_manifest_{ts}.txt")
    sha_path = manifest_path + ".sha256"

    # Collect evidence files: all pv_trace jsonl + any reports
    files = sorted(
        glob.glob("privatevault/reports/evidence/*.jsonl") +
        glob.glob("reports/vv/*.txt")
    )

    chain = "GENESIS"
    lines = []
    lines.append("==============================================================================")
    lines.append("PrivateVault Verify - Tamper-Proof Evidence Manifest (Hash-Chain)")
    lines.append("==============================================================================")
    lines.append(f"UTC Timestamp: {ts}")
    lines.append(f"Evidence Count: {len(files)}")
    lines.append("")
    lines.append("FORMAT: index | file | sha256(file) | chain_hash")
    lines.append("------------------------------------------------------------------------------")

    for i, fpath in enumerate(files, start=1):
        fh = sha256_file(fpath)
        chain = sha256_text(chain + fh)
        rel = fpath
        lines.append(f"{i:03d} | {rel} | {fh} | {chain}")

    lines.append("------------------------------------------------------------------------------")
    lines.append(f"FINAL_CHAIN_HASH: {chain}")
    lines.append("==============================================================================")

    content = "\n".join(lines) + "\n"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(content)

    mhash = sha256_file(manifest_path)
    with open(sha_path, "w", encoding="utf-8") as f:
        f.write(f"{mhash}  {manifest_path}\n")

    print(content)
    print(f"SHA256(manifest) written to: {sha_path}")

if __name__ == "__main__":
    main()
