"""Configuration and runtime paths for the utilities pipeline."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class PipelinePaths:
    """Filesystem locations used by the pipeline."""

    data: Path
    reports: Path
    checkpoint: Path

    @property
    def raw(self) -> Path:
        return self.data / "raw"

    @property
    def bronze(self) -> Path:
        return self.data / "bronze"

    @property
    def silver(self) -> Path:
        return self.data / "silver"

    @property
    def gold(self) -> Path:
        return self.data / "gold"


def get_pipeline_paths() -> PipelinePaths:
    """Return paths, allowing containers to override the data directory."""
    data_dir = Path(os.getenv("PIPELINE_DATA_DIR", PROJECT_ROOT / "data"))
    checkpoint_dir = Path(os.getenv("PIPELINE_STATE_DIR", data_dir / "state"))
    return PipelinePaths(
        data=data_dir,
        reports=Path(os.getenv("PIPELINE_REPORTS_DIR", PROJECT_ROOT / "reports")),
        checkpoint=checkpoint_dir / "cdc_checkpoint.json",
    )


PATHS = get_pipeline_paths()
