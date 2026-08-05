from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.bronze import ingest
from src.cdc import cdc_check
from src.common.config import PipelinePaths
from src.gold import aggregate
from src.silver import transform


@pytest.fixture
def pipeline_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> PipelinePaths:
    paths = PipelinePaths(data=tmp_path / "data", reports=tmp_path / "reports", checkpoint=tmp_path / "data" / "state" / "cdc_checkpoint.json")
    for module in (ingest, transform, aggregate, cdc_check):
        monkeypatch.setattr(module, "PATHS", paths)
    paths.raw.mkdir(parents=True)
    return paths


def test_medallion_pipeline_applies_quality_rules_and_aggregates(pipeline_paths: PipelinePaths) -> None:
    source = pd.DataFrame({
        "id_unidade_consumidora": ["UC-1", "UC-1", "UC-2", "UC-3"],
        "regiao": ["sul ", "SUL", "SUL", "NORTE"],
        "data_leitura": ["2026-01-01", "2026-01-01", "2026-01-01", "invalid"],
        "consumo_kwh": [100.0, 999.0, 200.0, 50.0],
    })
    source.to_csv(pipeline_paths.raw / "consumo.csv", index=False)

    bronze_path = ingest.ingest_csv("consumo.csv")
    silver_path = transform.transform(bronze_path.name)
    monthly_path, ranking_path = aggregate.aggregate(silver_path.name)

    silver = pd.read_parquet(silver_path)
    monthly = pd.read_parquet(monthly_path)
    ranking = pd.read_parquet(ranking_path)
    assert len(silver) == 2
    assert set(silver["regiao"]) == {"SUL"}
    assert monthly.loc[0, "consumo_total_kwh"] == 1199.0
    assert len(ranking) == 2


def test_cdc_is_idempotent_and_detects_content_change(pipeline_paths: PipelinePaths) -> None:
    source_path = pipeline_paths.raw / "consumo.csv"
    pd.DataFrame({"id_unidade_consumidora": ["UC-1"], "regiao": ["SUL"], "data_leitura": ["2026-01-01"], "consumo_kwh": [100]}).to_csv(source_path, index=False)

    assert len(cdc_check.detect_changes("consumo.csv")) == 1
    assert cdc_check.detect_changes("consumo.csv").empty
    pd.DataFrame({"id_unidade_consumidora": ["UC-1"], "regiao": ["SUL"], "data_leitura": ["2026-01-01"], "consumo_kwh": [150]}).to_csv(source_path, index=False)
    assert len(cdc_check.detect_changes("consumo.csv")) == 1
