"""Camada Silver: tipagem, deduplicação, padronização e detecção de outliers.
Falhas de qualidade (nulo, duplicata) são descartadas; outliers estatísticos
são apenas sinalizados (`consumo_atipico`), pois podem ser sinal real de
anomalia operacional (vazamento, defeito de equipamento) e a decisão de
descartar cabe à camada de consumo, não ao pipeline.
"""
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from common.paths import DATA_DIR

BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"

IQR_MULTIPLIER = 1.5  # limite padrão de mercado para detecção de outlier via IQR


def _flag_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Marca outliers por região via IQR — o limiar de anomalia varia por
    região (Nordeste tem base de consumo maior que Sul), então um único
    limite global geraria falsos positivos/negativos."""
    def flag_group(group: pd.DataFrame) -> pd.Series:
        q1, q3 = group["consumo_kwh"].quantile([0.25, 0.75])
        iqr = q3 - q1
        limite = q3 + IQR_MULTIPLIER * iqr
        return group["consumo_kwh"] > limite

    df["consumo_atipico"] = df.groupby("regiao", group_keys=False).apply(flag_group)
    return df


def transform(bronze_filename: str) -> Path:
    df = pd.read_parquet(BRONZE_DIR / bronze_filename)

    df["data_leitura"] = pd.to_datetime(df["data_leitura"])
    df["consumo_kwh"] = pd.to_numeric(df["consumo_kwh"], errors="coerce")
    df["regiao"] = df["regiao"].str.strip().str.upper()

    df = df.dropna(subset=["consumo_kwh"])
    df = df.drop_duplicates(subset=["id_unidade_consumidora", "data_leitura"])
    df = _flag_outliers(df)

    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SILVER_DIR / bronze_filename.replace("bronze_", "silver_")
    df.to_parquet(out_path, index=False)

    n_atipicos = int(df["consumo_atipico"].sum())
    print(f"[SILVER] {len(df)} registros limpos ({n_atipicos} atípicos sinalizados) -> {out_path}")
    return out_path


if __name__ == "__main__":
    transform("bronze_consumo_energia.parquet")
