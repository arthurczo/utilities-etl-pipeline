"""Camada Bronze: ingestão do dado bruto sem regra de negócio"""

import pandas as pd
from datetime import datetime, timezone
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from common.paths import DATA_DIR

RAW_DIR = DATA_DIR / "raw"
BRONZE_DIR = DATA_DIR / "bronze"

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
