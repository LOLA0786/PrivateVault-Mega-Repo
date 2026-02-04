import importlib.util
import os
from typing import Optional


def run_demo_bootstrap(root: Optional[str], demo_mode: bool) -> str:
    module_path = os.path.join(
        os.path.dirname(__file__), "..", "scripts", "demo_bootstrap.py"
    )
    module_path = os.path.realpath(module_path)
    spec = importlib.util.spec_from_file_location("demo_bootstrap", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module.bootstrap(root or os.path.join(os.getcwd(), ".demo"), demo_mode)
