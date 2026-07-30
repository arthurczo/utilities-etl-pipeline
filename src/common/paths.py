"""Resolução centralizada do diretório de dados. Local e Docker montam
src/ em profundidades diferentes relativas à raiz do projeto (local:
src/ na raiz; container: src/ dentro de dags/), então o cálculo relativo
quebra em um dos dois ambientes. PIPELINE_DATA_DIR, setada no
docker-compose, sobrescreve o cálculo automático nesse caso."""
import os
from pathlib import Path


def get_data_dir() -> Path:
    override = os.environ.get("PIPELINE_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent.parent / "data"


DATA_DIR = get_data_dir()
