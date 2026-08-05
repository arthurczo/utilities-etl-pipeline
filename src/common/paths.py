"""Backward-compatible path exports. Prefer :mod:`common.config` in new code."""
from pathlib import Path

from common.config import PATHS, get_pipeline_paths

DATA_DIR: Path = PATHS.data


def get_data_dir() -> Path:
    """Return the configured data directory."""
    return get_pipeline_paths().data
