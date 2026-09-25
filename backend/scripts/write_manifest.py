"""Regenerate ml_artifacts/manifest.json. Run after any artifact changes."""
import json
import sys
from pathlib import Path

ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "ml_artifacts"
sys.path.insert(0, str(ARTIFACTS_DIR.parent))

from models.loader import sha256_of  # noqa: E402


def write_manifest() -> dict[str, str]:
    hashes = {p.name: sha256_of(p) for p in sorted(ARTIFACTS_DIR.glob("*.pkl"))}
    (ARTIFACTS_DIR / "manifest.json").write_text(json.dumps({"sha256": hashes}, indent=2) + "\n")
    return hashes


if __name__ == "__main__":
    for name, digest in write_manifest().items():
        print(f"{digest[:12]}  {name}")
