"""Camada Gold: agregações de negócio prontas para consumo (BI/BigQuery).
Duas tabelas são geradas: consumo mensal por região (com variação percentual
e contagem de atípicos) e ranking das unidades consumidoras de maior consumo.
"""
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from common.paths import DATA_DIR

SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"


def aggregate(silver_filename: str) -> tuple[Path, Path]:
    df = pd.read_parquet(SILVER_DIR / silver_filename)
    df["ano_mes"] = df["data_leitura"].dt.to_period("M").astype(str)

    mensal = (
        df.groupby(["regiao", "ano_mes"])
        .agg(
            consumo_medio_kwh=("consumo_kwh", "mean"),
            consumo_total_kwh=("consumo_kwh", "sum"),
            qtd_unidades=("id_unidade_consumidora", "nunique"),
            qtd_leituras_atipicas=("consumo_atipico", "sum"),
        )
        .reset_index()
        .sort_values(["regiao", "ano_mes"])
    )
    # variação mês a mês por região — indicador central pra dashboard de tendência
    mensal["variacao_pct_mom"] = (
        mensal.groupby("regiao")["consumo_total_kwh"].pct_change().round(4) * 100
    )

    ranking = (
        df.groupby(["id_unidade_consumidora", "regiao"])
        .agg(consumo_medio_kwh=("consumo_kwh", "mean"), qtd_leituras_atipicas=("consumo_atipico", "sum"))
        .reset_index()
        .sort_values("consumo_medio_kwh", ascending=False)
        .head(20)
    )

    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    mensal_path = GOLD_DIR / silver_filename.replace("silver_", "gold_mensal_")
    ranking_path = GOLD_DIR / silver_filename.replace("silver_", "gold_ranking_")
    mensal.to_parquet(mensal_path, index=False)
    ranking.to_parquet(ranking_path, index=False)

    print(f"[GOLD] {len(mensal)} linhas mensais -> {mensal_path}")
    print(f"[GOLD] {len(ranking)} unidades no ranking -> {ranking_path}")
    return mensal_path, ranking_path


def load_to_bigquery(parquet_path: Path, table_id: str):
    """Carrega um parquet da Gold no BigQuery. table_id: 'projeto.dataset.tabela'.
    Requer GOOGLE_APPLICATION_CREDENTIALS apontando pro gcp-key.json."""
    from google.cloud import bigquery

    df = pd.read_parquet(parquet_path)
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    client.load_table_from_dataframe(df, table_id, job_config=job_config).result()
    print(f"[GOLD] Carregado no BigQuery: {table_id}")


if __name__ == "__main__":
    mensal_path, ranking_path = aggregate("silver_consumo_energia.parquet")
    # load_to_bigquery(mensal_path, "seu-projeto.utilities_dataset.consumo_mensal")
    # load_to_bigquery(ranking_path, "seu-projeto.utilities_dataset.consumo_ranking")
