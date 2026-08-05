"""Plotly chart factories used by the dashboard."""
from __future__ import annotations

import plotly.express as px
import pandas as pd

COLOR_SEQUENCE = ["#0EA5E9", "#22C55E", "#F59E0B", "#A855F7", "#EF4444"]


def monthly_trend(frame: pd.DataFrame):
    return px.line(frame, x="ano_mes", y="consumo_total_kwh", color="regiao", markers=True, color_discrete_sequence=COLOR_SEQUENCE, title="Monthly Consumption Trend", labels={"ano_mes": "Month", "consumo_total_kwh": "Consumption (kWh)", "regiao": "Region"})


def consumption_by_region(frame: pd.DataFrame):
    grouped = frame.groupby("regiao", as_index=False)["consumo_total_kwh"].sum().sort_values("consumo_total_kwh", ascending=False)
    return px.bar(grouped, x="regiao", y="consumo_total_kwh", color="regiao", color_discrete_sequence=COLOR_SEQUENCE, title="Consumption by Region", labels={"regiao": "Region", "consumo_total_kwh": "Consumption (kWh)"})


def top_consumers(frame: pd.DataFrame):
    top = frame.head(20).sort_values("consumo_medio_kwh")
    return px.bar(top, x="consumo_medio_kwh", y="id_unidade_consumidora", color="regiao", orientation="h", color_discrete_sequence=COLOR_SEQUENCE, title="Top Consumers", labels={"id_unidade_consumidora": "Consumer", "consumo_medio_kwh": "Average consumption (kWh)", "regiao": "Region"})


def outlier_distribution(frame: pd.DataFrame):
    grouped = frame.groupby("regiao", as_index=False)["qtd_leituras_atipicas"].sum()
    return px.pie(grouped, values="qtd_leituras_atipicas", names="regiao", color_discrete_sequence=COLOR_SEQUENCE, title="Outlier Distribution")
