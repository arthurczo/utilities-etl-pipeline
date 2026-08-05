"""File-based CDC simulation with an atomic, data-directory checkpoint."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.common.config import PATHS
from src.common.io import require_file

LOGGER = logging.getLogger(__name__)


def _row_hash(row: pd.Series) -> str:
    """Create a stable content hash independent of dataframe representation."""
    payload = json.dumps(row.to_dict(), sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_checkpoint(checkpoint_path: Path) -> set[str]:
    if not checkpoint_path.is_file():
        return set()
    try:
        return set(json.loads(checkpoint_path.read_text(encoding="utf-8")).get("hashes", []))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid CDC checkpoint: {checkpoint_path}") from error


def detect_changes(filename: str, checkpoint_path: Path | None = None) -> pd.DataFrame:
    """Return new or changed source records and persist their current hashes."""
    source_path = PATHS.raw / filename
    require_file(source_path)
    checkpoint = checkpoint_path or PATHS.checkpoint
    frame = pd.read_csv(source_path)
    frame["_row_hash"] = frame.apply(_row_hash, axis=1)
    known_hashes = _load_checkpoint(checkpoint)
    changed = frame.loc[~frame["_row_hash"].isin(known_hashes)].drop(columns="_row_hash").copy()
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    temporary = checkpoint.with_suffix(".tmp")
    temporary.write_text(json.dumps({"last_run": datetime.now(timezone.utc).isoformat(), "hashes": frame["_row_hash"].tolist()}), encoding="utf-8")
    temporary.replace(checkpoint)
    LOGGER.info("CDC completed: changed_rows=%s total_rows=%s", len(changed), len(frame))
    return changed


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(detect_changes("consumo_energia.csv").head())
