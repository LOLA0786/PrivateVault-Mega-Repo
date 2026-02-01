import hashlib


class SovereignLedger:
    def __init__(self, tenant_id, secret_salt):
        self.tenant_id = tenant_id
        self.secret_salt = secret_salt  # This makes every chain unique per customer
        self.prev_hash = "0000000000"

    def sign_decision(self, data):
        # We mix the secret salt into the hash
        content = f"{data}{self.tenant_id}{self.secret_salt}{self.prev_hash}"
        current_hash = hashlib.sha256(content.encode()).hexdigest()
        self.prev_hash = current_hash
        return current_hash
