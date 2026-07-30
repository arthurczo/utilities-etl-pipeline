import os
from pathlib import Path


def get_data_dir() -> Path:
    override = os.environ.get("PIPELINE_DATA_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent.parent.parent / "data"


DATA_DIR = get_data_dir()
