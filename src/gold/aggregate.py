"""Gold layer: business-ready aggregates and optional BigQuery publishing."""
from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd

from src.common.config import PATHS
from src.common.io import require_file, write_parquet_atomic

LOGGER = logging.getLogger(__name__)
TOP_CONSUMERS_LIMIT = 20


def aggregate(silver_filename: str) -> tuple[Path, Path]:
    """Create monthly regional metrics and a ranking of high-consuming units."""
    source_path = PATHS.silver / silver_filename
    require_file(source_path)
    frame = pd.read_parquet(source_path).copy()
    frame["ano_mes"] = pd.to_datetime(frame["data_leitura"]).dt.to_period("M").astype(str)
    monthly = (
        frame.groupby(["regiao", "ano_mes"], as_index=False)
        .agg(consumo_medio_kwh=("consumo_kwh", "mean"), consumo_total_kwh=("consumo_kwh", "sum"), qtd_unidades=("id_unidade_consumidora", "nunique"), qtd_leituras_atipicas=("consumo_atipico", "sum"))
        .sort_values(["regiao", "ano_mes"])
    )
    monthly["variacao_pct_mom"] = monthly.groupby("regiao")["consumo_total_kwh"].pct_change().mul(100).round(2)
    ranking = (
        frame.groupby(["id_unidade_consumidora", "regiao"], as_index=False)
        .agg(consumo_medio_kwh=("consumo_kwh", "mean"), qtd_leituras_atipicas=("consumo_atipico", "sum"))
        .nlargest(TOP_CONSUMERS_LIMIT, "consumo_medio_kwh")
    )
    monthly_path = PATHS.gold / silver_filename.replace("silver_", "gold_mensal_", 1)
    ranking_path = PATHS.gold / silver_filename.replace("silver_", "gold_ranking_", 1)
    write_parquet_atomic(monthly, monthly_path)
    write_parquet_atomic(ranking, ranking_path)
    LOGGER.info("Gold completed: monthly_rows=%s ranking_rows=%s", len(monthly), len(ranking))
    return monthly_path, ranking_path


def load_to_bigquery(parquet_path: Path, table_id: str, project_id: str | None = None) -> None:
    """Replace a fully-qualified BigQuery table with a Gold parquet artifact."""
    require_file(parquet_path)
    if len(table_id.split(".")) != 3:
        raise ValueError("table_id must use the format 'project.dataset.table'")
    from google.cloud import bigquery

    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path and not Path(credentials_path).is_file():
        raise FileNotFoundError("GOOGLE_APPLICATION_CREDENTIALS does not point to a file")
    client = bigquery.Client(project=project_id)
    job_config = bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.PARQUET, write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE)
    with parquet_path.open("rb") as parquet_file:
        client.load_table_from_file(parquet_file, table_id, job_config=job_config).result()
    LOGGER.info("Gold artifact loaded to BigQuery table %s", table_id)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    aggregate("silver_consumo_energia.parquet")
