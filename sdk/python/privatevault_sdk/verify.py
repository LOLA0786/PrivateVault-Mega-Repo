import hashlib
import os
from typing import List, Tuple


def verify_manifest(bundle_path: str) -> Tuple[bool, List[str]]:
    manifest_path = os.path.join(bundle_path, "hashes", "sha256sum.txt")
    if not os.path.exists(manifest_path):
        return False, ["MANIFEST_MISSING"]

    mismatches = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:
        expected, relpath = line.split("  ", 1)
        file_path = os.path.join(bundle_path, relpath)
        if not os.path.exists(file_path):
            mismatches.append(relpath)
            continue
        digest = hashlib.sha256()
        with open(file_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                digest.update(chunk)
        if digest.hexdigest() != expected:
            mismatches.append(relpath)

    return len(mismatches) == 0, mismatches
