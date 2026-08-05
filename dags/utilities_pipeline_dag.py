"""Daily batch pipeline for utility-energy consumption data."""
from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.bronze.ingest import ingest_csv
from src.cdc.cdc_check import detect_changes
from src.gold.aggregate import aggregate
from src.silver.transform import transform
from src.visualization.generate_charts import plot_consumo_mensal, plot_ranking_unidades

DEFAULT_ARGS = {"owner": "data-engineering", "depends_on_past": False, "retries": 2, "retry_delay": timedelta(minutes=5), "execution_timeout": timedelta(minutes=20)}

with DAG(
    dag_id="utilities_medallion_pipeline",
    description="Daily Bronze → Silver → Gold pipeline for utility consumption.",
    default_args=DEFAULT_ARGS,
    start_date=pendulum.datetime(2026, 7, 1, tz="America/Sao_Paulo"),
    schedule="0 6 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["utilities", "medallion", "batch", "portfolio"],
    doc_md="CDC observes source changes; Bronze, Silver, Gold and chart tasks run sequentially.",
) as dag:
    detect_cdc_changes = PythonOperator(task_id="detect_cdc_changes", python_callable=detect_changes, op_kwargs={"filename": "consumo_energia.csv"})
    ingest_bronze = PythonOperator(task_id="ingest_bronze", python_callable=ingest_csv, op_kwargs={"filename": "consumo_energia.csv"})
    transform_silver = PythonOperator(task_id="transform_silver", python_callable=transform, op_kwargs={"bronze_filename": "bronze_consumo_energia.parquet"})
    aggregate_gold = PythonOperator(task_id="aggregate_gold", python_callable=aggregate, op_kwargs={"silver_filename": "silver_consumo_energia.parquet"})
    chart_monthly_consumption = PythonOperator(task_id="chart_monthly_consumption", python_callable=plot_consumo_mensal, op_kwargs={"mensal_filename": "gold_mensal_consumo_energia.parquet"})
    chart_consumer_ranking = PythonOperator(task_id="chart_consumer_ranking", python_callable=plot_ranking_unidades, op_kwargs={"ranking_filename": "gold_ranking_consumo_energia.parquet"})

    detect_cdc_changes >> ingest_bronze >> transform_silver >> aggregate_gold >> [chart_monthly_consumption, chart_consumer_ranking]
