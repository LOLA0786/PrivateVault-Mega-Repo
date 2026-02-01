import pytest
from privatevault.core.vault import PrivateVault
from privatevault.core.policy import Policy
from privatevault.adapters.google_adk_adapter import build_google_adk_tools

def test_google_adk_privatevault_blocks_shell():
    vault = PrivateVault()
    policy = Policy()
    tools = build_google_adk_tools(vault, policy)
    with pytest.raises(RuntimeError):
        tools["shell"](cmd="rm -rf /")

def test_google_adk_privatevault_allows_add():
    vault = PrivateVault()
    policy = Policy()
    tools = build_google_adk_tools(vault, policy)
    assert tools["add"](a=11, b=22) == 33
