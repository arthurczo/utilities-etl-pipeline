"""Silver layer: validated, typed, deduplicated utility readings."""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.common.config import PATHS
from src.common.io import require_file, write_parquet_atomic

LOGGER = logging.getLogger(__name__)
IQR_MULTIPLIER = 1.5
KEY_COLUMNS = ["id_unidade_consumidora", "data_leitura"]


def _flag_outliers(frame: pd.DataFrame) -> pd.Series:
    """Return an outlier flag calculated independently for each region."""
    quartiles = frame.groupby("regiao")["consumo_kwh"].quantile([0.25, 0.75]).unstack()
    quartiles.columns = ["q1", "q3"]
    upper_bound = quartiles["q3"] + IQR_MULTIPLIER * (quartiles["q3"] - quartiles["q1"])
    return frame["consumo_kwh"] > frame["regiao"].map(upper_bound)


def transform(bronze_filename: str) -> Path:
    """Apply quality controls and materialize the Silver parquet artifact."""
    source_path = PATHS.bronze / bronze_filename
    require_file(source_path)
    frame = pd.read_parquet(source_path).copy()
    input_rows = len(frame)
    frame["data_leitura"] = pd.to_datetime(frame["data_leitura"], errors="coerce")
    frame["consumo_kwh"] = pd.to_numeric(frame["consumo_kwh"], errors="coerce")
    frame["regiao"] = frame["regiao"].astype("string").str.strip().str.upper()
    frame["id_unidade_consumidora"] = frame["id_unidade_consumidora"].astype("string").str.strip()
    frame = frame.dropna(subset=[*KEY_COLUMNS, "regiao", "consumo_kwh"])
    frame = frame[frame["consumo_kwh"] >= 0]
    frame = frame.drop_duplicates(subset=KEY_COLUMNS, keep="last")
    frame["consumo_atipico"] = _flag_outliers(frame).fillna(False).astype(bool)
    output_path = PATHS.silver / bronze_filename.replace("bronze_", "silver_", 1)
    write_parquet_atomic(frame, output_path)
    LOGGER.info("Silver completed: input_rows=%s output_rows=%s rejected_rows=%s outliers=%s", input_rows, len(frame), input_rows - len(frame), int(frame["consumo_atipico"].sum()))
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    transform("bronze_consumo_energia.parquet")
