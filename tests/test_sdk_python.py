import hashlib
import hmac
import os
import sys

SDK_ROOT = os.path.join(os.path.dirname(__file__), "..", "sdk", "python")
sys.path.insert(0, os.path.realpath(SDK_ROOT))

from privatevault_sdk.context import compute_request_hash, sign_context
from privatevault_sdk.approvals import create_approval
from privatevault_sdk.verify import verify_manifest


def test_context_signing():
    context = {"actor_id": "user", "nonce": "1"}
    signature = sign_context(context, "secret")
    assert isinstance(signature, str)


def test_request_hash():
    h = compute_request_hash("GET", "/status", b"")
    assert len(h) == 64


def test_create_approval():
    approval = create_approval(
        approver_id="a1",
        role="CRO",
        region="US",
        intent_hash="ih",
        key_id="k1",
        secret="secret",
    )
    assert approval["signature"] == hmac.new(b"secret", b"ih", hashlib.sha256).hexdigest()


def test_verify_manifest_missing(tmp_path):
    ok, errors = verify_manifest(str(tmp_path))
    assert ok is False
    assert "MANIFEST_MISSING" in errors
