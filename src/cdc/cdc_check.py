"""CDC simulado via hash de linha + checkpoint, sem depender de
infraestrutura de replicação (Debezium/Datastream). Ver README para o
racional da abordagem."""
import json
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

RAW_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
CHECKPOINT_FILE = Path(__file__).parent / "_checkpoint.json"


def _row_hash(row) -> str:
    return hashlib.md5(str(row.values).encode()).hexdigest()


def detect_changes(filename: str) -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / filename)
    df["_row_hash"] = df.apply(_row_hash, axis=1)

    if CHECKPOINT_FILE.exists():
        checkpoint = json.loads(CHECKPOINT_FILE.read_text())
        known_hashes = set(checkpoint.get("hashes", []))
    else:
        known_hashes = set()

    # cobre INSERT (hash novo) e UPDATE (conteúdo mudou -> hash mudou)
    changed_df = df[~df["_row_hash"].isin(known_hashes)].copy()

    checkpoint = {
        "last_run": datetime.now(timezone.utc).isoformat(),
        "hashes": df["_row_hash"].tolist(),
    }
    CHECKPOINT_FILE.write_text(json.dumps(checkpoint))

    print(f"[CDC] {len(changed_df)} registros novos/alterados de {len(df)} totais")
    return changed_df.drop(columns=["_row_hash"])


if __name__ == "__main__":
    delta = detect_changes("consumo_energia.csv")
    print(delta.head())
