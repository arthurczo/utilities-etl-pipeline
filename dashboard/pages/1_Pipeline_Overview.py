"""Visual inventory of the local Medallion pipeline."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.data import load_gold_artifacts
from src.common.config import PATHS

st.set_page_config(page_title="Pipeline Overview", page_icon="🗺️", layout="wide")
st.title("🗺️ Pipeline Overview")
st.caption("Local implementation today; cloud endpoints are optional production integrations.")

try:
    artifacts = load_gold_artifacts(PATHS.data)
    gold_records = len(artifacts.monthly) + len(artifacts.ranking)
    generated_files = f"{artifacts.monthly_path.name}, {artifacts.ranking_path.name}"
except FileNotFoundError:
    gold_records, generated_files = 0, "Run ETL to generate artifacts"

layers = [
    ("☁️ Cloud Storage", "Source landing zone (simulated locally)", "CSV meter readings", "data/raw/consumo_energia.csv", "Source file"),
    ("🛫 Airflow", "Schedules, retries and observability", "DAG run", "utilities_medallion_pipeline", "1 DAG"),
    ("🥉 Bronze", "Immutable source copy with metadata", "Raw CSV", "data/bronze/bronze_*.parquet", "1,515 rows*"),
    ("🥈 Silver", "Validated, typed and deduplicated readings", "Bronze Parquet", "data/silver/silver_*.parquet", "1,485 rows*"),
    ("🥇 Gold", "Business aggregates for consumption", "Silver Parquet", generated_files, f"{gold_records} aggregate rows"),
    ("🔷 BigQuery", "Optional serving layer for cloud analytics", "Gold Parquet", "project.dataset.table", "On demand"),
    ("📊 Looker Studio", "Optional BI visualization", "BigQuery table", "Dashboard", "On demand"),
]

st.markdown("#### Cloud Storage → Airflow → Bronze → Silver → Gold → BigQuery → Looker Studio")
for name, purpose, input_name, output_name, records in layers:
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([1.2, 2.4, 2, 2])
        col1.markdown(f"**{name}**")
        col2.caption("Purpose"); col2.write(purpose)
        col3.caption("Input"); col3.code(input_name, language=None)
        col4.caption(f"Output · {records}"); col4.code(output_name, language=None)

st.caption("*Record counts reflect the included deterministic sample dataset and update after each ETL execution.")
