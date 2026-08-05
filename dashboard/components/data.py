"""Load and filter ETL artifacts for dashboard views."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class GoldArtifacts:
    """Gold datasets and their artifact locations."""

    monthly: pd.DataFrame
    ranking: pd.DataFrame
    monthly_path: Path
    ranking_path: Path


def load_gold_artifacts(data_dir: Path) -> GoldArtifacts:
    """Load the current Gold outputs, failing with an actionable message."""
    gold_dir = data_dir / "gold"
    monthly_path = gold_dir / "gold_mensal_consumo_energia.parquet"
    ranking_path = gold_dir / "gold_ranking_consumo_energia.parquet"
    missing = [str(path) for path in (monthly_path, ranking_path) if not path.is_file()]
    if missing:
        raise FileNotFoundError("Gold artifacts not found. Run the ETL first: " + ", ".join(missing))
    monthly = pd.read_parquet(monthly_path)
    ranking = pd.read_parquet(ranking_path)
    return GoldArtifacts(monthly=monthly, ranking=ranking, monthly_path=monthly_path, ranking_path=ranking_path)


def filter_monthly(frame: pd.DataFrame, regions: list[str], months: list[str]) -> pd.DataFrame:
    """Apply optional region and month selections to monthly aggregates."""
    filtered = frame.copy()
    if regions:
        filtered = filtered[filtered["regiao"].isin(regions)]
    if months:
        filtered = filtered[filtered["ano_mes"].isin(months)]
    return filtered


def filter_ranking(frame: pd.DataFrame, regions: list[str], consumers: list[str]) -> pd.DataFrame:
    """Apply optional region and consumer selections to the Gold ranking."""
    filtered = frame.copy()
    if regions:
        filtered = filtered[filtered["regiao"].isin(regions)]
    if consumers:
        filtered = filtered[filtered["id_unidade_consumidora"].isin(consumers)]
    return filtered.sort_values("consumo_medio_kwh", ascending=False)
