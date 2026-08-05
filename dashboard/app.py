"""Interactive local dashboard for the Utilities ETL Gold layer."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.charts import consumption_by_region, monthly_trend, outlier_distribution, top_consumers
from dashboard.components.data import filter_monthly, filter_ranking, load_gold_artifacts
from src.common.config import PATHS

st.set_page_config(page_title="Utilities Data Platform", page_icon="⚡", layout="wide")
st.title("⚡ Utilities Data Platform")
st.caption("Interactive view of the latest local Gold-layer artifacts. No cloud credentials required.")

try:
    artifacts = load_gold_artifacts(PATHS.data)
except FileNotFoundError as error:
    st.error(str(error))
    st.code("python scripts/generate_sample_data.py\npython -m src.bronze.ingest\npython -m src.silver.transform\npython -m src.gold.aggregate")
    st.stop()

all_regions = sorted(artifacts.monthly["regiao"].dropna().unique().tolist())
all_months = sorted(artifacts.monthly["ano_mes"].dropna().unique().tolist())
all_consumers = sorted(artifacts.ranking["id_unidade_consumidora"].dropna().unique().tolist())
with st.sidebar:
    st.header("Filters")
    regions = st.multiselect("Region", all_regions, default=all_regions)
    months = st.multiselect("Month", all_months, default=all_months)
    consumers = st.multiselect("Consumer", all_consumers)
    st.caption(f"Updated from: `{artifacts.monthly_path.name}`")

monthly = filter_monthly(artifacts.monthly, regions, months)
ranking = filter_ranking(artifacts.ranking, regions, consumers)
total_consumption = monthly["consumo_total_kwh"].sum()
total_consumers = monthly["qtd_unidades"].max() if not monthly.empty else 0
processed_records = monthly["qtd_leituras"].sum() if not monthly.empty and "qtd_leituras" in monthly else 0
outliers = monthly["qtd_leituras_atipicas"].sum()

cards = st.columns(4)
cards[0].metric("Total Consumption", f"{total_consumption:,.0f} kWh")
cards[1].metric("Consumers", f"{total_consumers:,.0f}")
cards[2].metric("Processed Records", f"{processed_records:,.0f}")
cards[3].metric("Detected Outliers", f"{outliers:,.0f}")

if monthly.empty:
    st.warning("No Gold data matches the selected region and month filters.")
    st.stop()

left, right = st.columns(2)
left.plotly_chart(monthly_trend(monthly), use_container_width=True)
right.plotly_chart(consumption_by_region(monthly), use_container_width=True)
left, right = st.columns(2)
left.plotly_chart(top_consumers(ranking), use_container_width=True)
right.plotly_chart(outlier_distribution(monthly), use_container_width=True)

with st.expander("Gold artifacts"):
    st.write({"monthly": str(artifacts.monthly_path), "ranking": str(artifacts.ranking_path), "monthly_rows": len(artifacts.monthly), "ranking_rows": len(artifacts.ranking)})
