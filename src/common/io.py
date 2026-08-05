"""Small, reusable I/O helpers with predictable failure modes."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

LOGGER = logging.getLogger(__name__)


def require_file(path: Path) -> None:
    """Raise an actionable error when a pipeline input is unavailable."""
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")


def write_parquet_atomic(frame: pd.DataFrame, destination: Path) -> Path:
    """Write a parquet artifact atomically to avoid partially written outputs."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(f"{destination.suffix}.tmp")
    try:
        frame.to_parquet(temporary, index=False)
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    LOGGER.info("Wrote %s rows to %s", len(frame), destination)
    return destination
