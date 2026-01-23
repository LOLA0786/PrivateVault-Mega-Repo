import os


class KeyManager:
    """
    Abstracts key access.
    Local → in-memory
    Prod → AWS KMS / GCP KMS / HSM
    """

    def __init__(self):
        self.backend = self._detect_backend()

    def _detect_backend(self):
        if os.getenv("AWS_KMS_KEY_ID"):
            return "aws-kms"
        if os.getenv("GCP_KMS_KEY_ID"):
            return "gcp-kms"
        return "local"

    def sign(self, payload: bytes) -> bytes:
        if self.backend == "local":
            return payload  # placeholder
        raise NotImplementedError("KMS signing not wired yet")

    def rotate(self):
        return {"backend": self.backend, "rotation": "scheduled"}
