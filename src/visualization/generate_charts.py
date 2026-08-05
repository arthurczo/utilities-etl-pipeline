"""Create portfolio charts from Gold-layer artifacts."""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.common.config import PATHS
from src.common.io import require_file

LOGGER = logging.getLogger(__name__)
plt.style.use("seaborn-v0_8-whitegrid")


def plot_consumo_mensal(mensal_filename: str) -> Path:
    """Create a line chart of total monthly consumption by region."""
    source_path = PATHS.gold / mensal_filename
    require_file(source_path)
    frame = pd.read_parquet(source_path)
    figure, axis = plt.subplots(figsize=(10, 5))
    for region, group in frame.groupby("regiao"):
        axis.plot(group["ano_mes"], group["consumo_total_kwh"], marker="o", label=region)
    axis.set(title="Consumo total de energia por região (kWh/mês)", xlabel="Mês", ylabel="Consumo total (kWh)")
    axis.legend(title="Região", bbox_to_anchor=(1.02, 1), loc="upper left")
    figure.autofmt_xdate(rotation=45)
    figure.tight_layout()
    PATHS.reports.mkdir(parents=True, exist_ok=True)
    output_path = PATHS.reports / "consumo_mensal_por_regiao.png"
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
    LOGGER.info("Monthly consumption chart saved to %s", output_path)
    return output_path


def plot_ranking_unidades(ranking_filename: str) -> Path:
    """Create a horizontal chart for the highest-average-consumption units."""
    source_path = PATHS.gold / ranking_filename
    require_file(source_path)
    frame = pd.read_parquet(source_path).sort_values("consumo_medio_kwh")
    figure, axis = plt.subplots(figsize=(9, 7))
    colors = ["#d62728" if count > 0 else "#1f77b4" for count in frame["qtd_leituras_atipicas"]]
    axis.barh(frame["id_unidade_consumidora"], frame["consumo_medio_kwh"], color=colors)
    axis.set(title="Top 20 unidades por consumo médio\n(vermelho = leitura atípica)", xlabel="Consumo médio (kWh)")
    figure.tight_layout()
    PATHS.reports.mkdir(parents=True, exist_ok=True)
    output_path = PATHS.reports / "ranking_unidades_consumidoras.png"
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
    LOGGER.info("Consumer ranking chart saved to %s", output_path)
    return output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    plot_consumo_mensal("gold_mensal_consumo_energia.parquet")
    plot_ranking_unidades("gold_ranking_consumo_energia.parquet")
