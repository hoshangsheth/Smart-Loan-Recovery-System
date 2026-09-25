"""
Centralized ML artifact loader.

All pickle files are loaded exactly once, at application startup, and held
in memory for the lifetime of the process. No service or route ever opens a
pickle file directly — they all go through `get_ml_artifacts()`.

Unpickling executes code, so every file is checked against the SHA-256
hashes in `manifest.json` before it is loaded.
"""
import hashlib
import json
import logging
import pickle
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from config.settings import settings

logger = logging.getLogger(__name__)


class ArtifactIntegrityError(RuntimeError):
    pass


@dataclass(frozen=True)
class MLArtifacts:
    """Bundle of every ML artifact the app needs, loaded once."""

    xgb_model: Any
    calibrator: Any
    scaler: Any
    kmeans: Any
    segment_profiles: dict[int, dict]
    model_version: str


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_manifest() -> dict[str, str]:
    path = settings.artifact_manifest_path
    if not path.exists():
        raise ArtifactIntegrityError(f"Artifact manifest missing: {path}")
    return json.loads(path.read_text())["sha256"]


def _load_verified_pickle(path: Path, manifest: dict[str, str]) -> Any:
    expected = manifest.get(path.name)
    if expected is None:
        raise ArtifactIntegrityError(f"{path.name} is not listed in the artifact manifest")
    if sha256_of(path) != expected:
        raise ArtifactIntegrityError(f"{path.name} does not match its manifest hash; refusing to unpickle")
    with open(path, "rb") as f:
        return pickle.load(f)


@lru_cache
def get_ml_artifacts() -> MLArtifacts:
    """Load, verify, and cache all ML artifacts (effectively a singleton)."""
    logger.info("Loading ML artifacts from %s", settings.ml_artifacts_dir)
    manifest = _load_manifest()

    xgb_model = _load_verified_pickle(settings.xgb_model_path, manifest)
    calibrator = _load_verified_pickle(settings.calibrator_path, manifest)
    scaler = _load_verified_pickle(settings.scaler_path, manifest)
    kmeans = _load_verified_pickle(settings.kmeans_path, manifest)
    segment_profiles = _load_verified_pickle(settings.segment_profiles_path, manifest)
    model_version = manifest[settings.xgb_model_path.name][:12]

    logger.info(
        "ML artifacts loaded: model=%s version=%s, kmeans(k=%s), %d segments",
        type(xgb_model).__name__,
        model_version,
        getattr(kmeans, "n_clusters", "?"),
        len(segment_profiles),
    )

    return MLArtifacts(
        xgb_model=xgb_model,
        scaler=scaler,
        calibrator=calibrator,
        kmeans=kmeans,
        segment_profiles=segment_profiles,
        model_version=model_version,
    )
