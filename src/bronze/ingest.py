"""Bronze layer: immutable source copy plus ingestion metadata."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.common.config import PATHS
from src.common.io import require_file, write_parquet_atomic

LOGGER = logging.getLogger(__name__)
REQUIRED_COLUMNS = frozenset({"id_unidade_consumidora", "regiao", "data_leitura", "consumo_kwh"})


def ingest_csv(filename: str) -> Path:
    """Ingest a CSV without business transformations and return its artifact."""
    source_path = PATHS.raw / filename
    require_file(source_path)
    frame = pd.read_csv(source_path)
    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)
    if missing_columns:
        raise ValueError(f"Required columns missing from {filename}: {sorted(missing_columns)}")

    frame["_ingested_at"] = datetime.now(timezone.utc).isoformat()
    frame["_source_file"] = filename
    output_path = PATHS.bronze / f"bronze_{source_path.stem}.parquet"
    write_parquet_atomic(frame, output_path)
    LOGGER.info("Bronze ingestion completed: source=%s rows=%s", filename, len(frame))
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingest_csv("consumo_energia.csv")
