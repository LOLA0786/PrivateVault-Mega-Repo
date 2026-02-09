from services.api.governance.normalizer import normalize_ai_output, GovernanceMode


def test_strict_mode_blocks_garbage():
    raw = "approve loan pls"
    out = normalize_ai_output(raw, GovernanceMode.STRICT)

    assert out["decision"] == "BLOCK"
    assert out["raw_valid"] is False


def test_relaxed_mode_reviews_garbage():
    raw = {"decision": "YES", "confidence": "high"}
    out = normalize_ai_output(raw, GovernanceMode.RELAXED)

    assert out["decision"] == "REVIEW"
    assert out["raw_valid"] is False


def test_valid_output_passes():
    raw = {"decision": "ALLOW", "confidence": 0.87}
    out = normalize_ai_output(raw, GovernanceMode.STRICT)

    assert out["decision"] == "ALLOW"
    assert out["raw_valid"] is True


def test_demo_mode_is_deterministic():
    raw = {"decision": "ALLOW", "confidence": 0.9}
    out = normalize_ai_output(raw, GovernanceMode.DEMO)

    assert out["decision"] == "BLOCK"
    assert out["reason"] == "DEMO_MODE_ENFORCED"
