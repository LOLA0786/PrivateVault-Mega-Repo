import subprocess
import json
from .interfaces import ZKProver

class ExternalZKProver(ZKProver):
    """
    Calls an external prover (Circom / Halo2 / SnarkJS).
    Keeps Python layer audit-safe.
    """
    def prove_range(self, value, min_v, max_v):
        payload = json.dumps({
            "value": value,
            "min": min_v,
            "max": max_v
        })
        # Placeholder – wire real prover here
        return {
            "proof": "zk-proof-bytes",
            "public": {"min": min_v, "max": max_v},
            "valid": min_v <= value <= max_v
        }
