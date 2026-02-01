from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.adapters.llamaindex_adapter import build_llamaindex_query_engine

def test_llamaindex_privatevault_logs_query():
    vault = PrivateVault()
    policy = Policy()
    qe = build_llamaindex_query_engine(vault, policy)

    resp = qe.query("What is PrivateVault?")
    assert resp is not None
