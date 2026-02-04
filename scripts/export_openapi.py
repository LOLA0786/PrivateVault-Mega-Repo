import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from services.api.app import create_app


def main():
    app = create_app()
    spec = app.openapi()
    out_path = os.path.join("sdk", "openapi", "openapi.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, sort_keys=True)
        f.write("\n")
    print(out_path)


if __name__ == "__main__":
    main()
