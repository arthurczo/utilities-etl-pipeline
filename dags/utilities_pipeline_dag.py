"""DAG do pipeline medallion de consumo de energia.
Fluxo: Bronze -> Silver -> Gold -> Visualização, com CDC rodando em
paralelo à ingestão. Orquestração aqui; lógica de negócio em src/."""
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from bronze.ingest import ingest_csv
from silver.transform import transform
from gold.aggregate import aggregate
from cdc.cdc_check import detect_changes
from visualization.generate_charts import plot_consumo_mensal, plot_ranking_unidades

default_args = {
    "owner": "arthur",
    "retries": 2,
}

with DAG(
    dag_id="utilities_medallion_pipeline",
    description="Pipeline Bronze -> Silver -> Gold -> Viz para consumo de energia",
    default_args=default_args,
    start_date=datetime(2026, 7, 1),
    schedule="@daily",
    catchup=False,
    tags=["utilities", "medallion", "etl"],
) as dag:

    task_cdc = PythonOperator(
        task_id="detect_changes_cdc",
        python_callable=detect_changes,
        op_kwargs={"filename": "consumo_energia.csv"},
    )

    task_bronze = PythonOperator(
        task_id="ingest_bronze",
        python_callable=ingest_csv,
        op_kwargs={"filename": "consumo_energia.csv"},
    )

    task_silver = PythonOperator(
        task_id="transform_silver",
        python_callable=transform,
        op_kwargs={"bronze_filename": "bronze_consumo_energia.parquet"},
    )

    task_gold = PythonOperator(
        task_id="aggregate_gold",
        python_callable=aggregate,
        op_kwargs={"silver_filename": "silver_consumo_energia.parquet"},
    )

    task_viz_mensal = PythonOperator(
        task_id="plot_consumo_mensal",
        python_callable=plot_consumo_mensal,
        op_kwargs={"mensal_filename": "gold_mensal_consumo_energia.parquet"},
    )

    task_viz_ranking = PythonOperator(
        task_id="plot_ranking_unidades",
        python_callable=plot_ranking_unidades,
        op_kwargs={"ranking_filename": "gold_ranking_consumo_energia.parquet"},
    )

    task_cdc
    task_bronze >> task_silver >> task_gold >> [task_viz_mensal, task_viz_ranking]
