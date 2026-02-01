import pytest
from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.adapters.langgraph_adapter import build_langgraph_tools

def test_langgraph_privatevault_blocks_shell():
    vault = PrivateVault()
    policy = Policy()
    tools = build_langgraph_tools(vault, policy)
    with pytest.raises(RuntimeError):
        tools["shell"](cmd="rm -rf /")

def test_langgraph_privatevault_allows_add():
    vault = PrivateVault()
    policy = Policy()
    tools = build_langgraph_tools(vault, policy)
    assert tools["add"](a=10, b=5) == 15
