"""
Generate SHA256 hashes for model artifacts used by the API.

Usage:
  python scripts/generate_model_hashes.py

It prints PowerShell-friendly environment variable commands for:
  - SCALER_SHA256
  - RANDOM_FOREST_SHA256
  - GRADIENT_BOOSTING_SHA256 (if present)
  - NEURAL_NETWORK_SHA256 (if present)
"""

from __future__ import annotations

from pathlib import Path
import hashlib


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    outputs_dir = repo_root / "src" / "models" / "outputs"

    mapping = {
        "SCALER_SHA256": outputs_dir / "scaler.pkl",
        "RANDOM_FOREST_SHA256": outputs_dir / "random_forest_model.pkl",
        "GRADIENT_BOOSTING_SHA256": outputs_dir / "gradient_boosting_model.pkl",
        "NEURAL_NETWORK_SHA256": outputs_dir / "neural_network_model.h5",
    }

    print(f"# Model outputs dir: {outputs_dir}")
    for env_name, path in mapping.items():
        if not path.exists():
            print(f"# {env_name} (missing): {path.name}")
            continue
        digest = sha256_file(path)
        # PowerShell-friendly
        print(f"$env:{env_name}=\"{digest}\"")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

