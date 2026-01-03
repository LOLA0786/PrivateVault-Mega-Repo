class ZKProver:
    """
    Interface only. Production implementation may use zk-SNARKs / Bulletproofs.
    """
    def prove_compliance(self, value, limits):
        raise NotImplementedError("ZKP backend not configured")
