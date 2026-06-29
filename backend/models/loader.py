"""
Centralized ML artifact loader.

All pickle files are loaded exactly once, at application startup, and held
in memory for the lifetime of the process. No service or route ever opens a
pickle file directly — they all go through `get_ml_artifacts()`.
"""
import logging
import pickle
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MLArtifacts:
    """Bundle of every ML artifact the app needs, loaded once."""

    xgb_model: Any
    scaler: Any
    kmeans: Any
    segment_names: dict[int, str]
    gender_map: dict[str, int]


def _load_pickle(path) -> Any:
    with open(path, "rb") as f:
        return pickle.load(f)


@lru_cache
def get_ml_artifacts() -> MLArtifacts:
    """
    Load and cache all ML artifacts.

    Cached with lru_cache so this is effectively a singleton: the first
    call (triggered from the FastAPI startup hook) does the real disk I/O,
    every subsequent call across the app just returns the same objects.
    """
    logger.info("Loading ML artifacts from %s", settings.ml_artifacts_dir)

    xgb_model = _load_pickle(settings.xgb_model_path)
    scaler = _load_pickle(settings.scaler_path)
    kmeans = _load_pickle(settings.kmeans_path)
    segment_names = _load_pickle(settings.segment_names_path)
    gender_map = _load_pickle(settings.gender_map_path)

    logger.info(
        "ML artifacts loaded: model=%s, scaler=%s, kmeans(k=%s), %d segments",
        type(xgb_model).__name__,
        type(scaler).__name__,
        getattr(kmeans, "n_clusters", "?"),
        len(segment_names),
    )

    return MLArtifacts(
        xgb_model=xgb_model,
        scaler=scaler,
        kmeans=kmeans,
        segment_names=segment_names,
        gender_map=gender_map,
    )
