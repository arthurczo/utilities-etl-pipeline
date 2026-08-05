from __future__ import annotations

import pandas as pd

from dashboard.components.data import filter_monthly, filter_ranking


def test_dashboard_filters_respect_selected_dimensions() -> None:
    monthly = pd.DataFrame({"regiao": ["SUL", "NORTE"], "ano_mes": ["2026-01", "2026-02"], "consumo_total_kwh": [100, 200]})
    ranking = pd.DataFrame({"regiao": ["SUL", "NORTE"], "id_unidade_consumidora": ["UC-1", "UC-2"], "consumo_medio_kwh": [100, 200]})

    assert len(filter_monthly(monthly, ["SUL"], ["2026-01"])) == 1
    filtered_ranking = filter_ranking(ranking, ["NORTE"], ["UC-2"])
    assert filtered_ranking.iloc[0]["id_unidade_consumidora"] == "UC-2"
