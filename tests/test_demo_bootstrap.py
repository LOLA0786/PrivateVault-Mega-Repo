import importlib.util
import os


def _load_bootstrap_module():
    module_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "demo_bootstrap.py"
    )
    module_path = os.path.realpath(module_path)
    spec = importlib.util.spec_from_file_location("demo_bootstrap", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module


def test_demo_bootstrap_creates_env(tmp_path):
    module = _load_bootstrap_module()
    env_path = module.bootstrap(str(tmp_path), demo_mode=True)

    assert os.path.exists(env_path)
    with open(env_path, "r", encoding="utf-8") as f:
        env_contents = f.read()

    assert "PV_DEMO_MODE='1'" in env_contents
    assert os.path.exists(os.path.join(tmp_path, "audit.log"))
    assert os.path.exists(os.path.join(tmp_path, "policies.json"))
