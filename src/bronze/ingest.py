"""Camada Bronze: ingestão do dado bruto sem regra de negócio, preservando
metadados de origem para permitir reprocessamento a partir daqui."""
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

RAW_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
BRONZE_DIR = Path(__file__).parent.parent.parent / "data" / "bronze"

REQUIRED_COLUMNS = ["id_unidade_consumidora", "regiao", "data_leitura", "consumo_kwh"]


def ingest_csv(filename: str) -> Path:
    df = pd.read_csv(RAW_DIR / filename)

    faltando = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas obrigatórias ausentes em {filename}: {faltando}")

    df["_ingested_at"] = datetime.now(timezone.utc).isoformat()
    df["_source_file"] = filename

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BRONZE_DIR / f"bronze_{filename.replace('.csv', '')}.parquet"
    df.to_parquet(out_path, index=False)
    print(f"[BRONZE] {len(df)} registros ingeridos de {filename} -> {out_path}")
    return out_path


if __name__ == "__main__":
    ingest_csv("consumo_energia.csv")
