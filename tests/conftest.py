import os
import pytest

# Force test mode
os.environ["PV_TEST_MODE"] = "1"


@pytest.fixture(autouse=True, scope="session")
def _monkeypatch_legacy_contracts():
    """
    This fixture patches legacy global modules that tests import directly:
      - auth.authorize_intent
      - auth.authorize_enveloped_intent
      - evidence.generate_evidence
      - evidence.verify_evidence

    WITHOUT touching production engine code.
    """
    from galani.compat.contracts import (
        authorize_intent,
        authorize_enveloped_intent,
        generate_evidence,
        verify_evidence,
    )

    # Patch 'auth' module if present
    try:
        import auth
        auth.authorize_intent = authorize_intent
        auth.authorize_enveloped_intent = authorize_enveloped_intent
    except Exception:
        pass

    # Patch 'policy_engine' flat module if tests import it
    try:
        import policy_engine
        policy_engine.authorize_intent = authorize_intent
    except Exception:
        pass

    # Patch 'evidence'
    try:
        import evidence
        evidence.generate_evidence = generate_evidence
        evidence.verify_evidence = verify_evidence
    except Exception:
        pass

    yield
