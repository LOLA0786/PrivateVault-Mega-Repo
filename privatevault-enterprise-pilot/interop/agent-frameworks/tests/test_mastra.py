import pytest
from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.adapters.mastra_adapter import build_mastra_tools

def test_mastra_privatevault_blocks_shell():
    vault = PrivateVault()
    policy = Policy()
    tools = build_mastra_tools(vault, policy)
    with pytest.raises(RuntimeError):
        tools["shell"](cmd="rm -rf /")

def test_mastra_privatevault_allows_add():
    vault = PrivateVault()
    policy = Policy()
    tools = build_mastra_tools(vault, policy)
    assert tools["add"](a=3, b=9) == 12
