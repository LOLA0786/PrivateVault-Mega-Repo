import pytest
from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.adapters.crewai_adapter import build_crewai_tools

def test_crewai_privatevault_blocks_shell():
    vault = PrivateVault()
    policy = Policy()
    tools = build_crewai_tools(vault, policy)
    with pytest.raises(RuntimeError):
        tools["shell"](cmd="rm -rf /")

def test_crewai_privatevault_allows_add():
    vault = PrivateVault()
    policy = Policy()
    tools = build_crewai_tools(vault, policy)
    assert tools["add"](a=1, b=2) == 3
