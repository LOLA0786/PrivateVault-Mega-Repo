from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.adapters.haystack_adapter import build_haystack_retriever

def test_haystack_privatevault_retrieval():
    vault = PrivateVault()
    policy = Policy()
    retrieve = build_haystack_retriever(vault, policy)

    out = retrieve("What does PrivateVault do?")
    assert "documents" in out
    assert len(out["documents"]) >= 1
