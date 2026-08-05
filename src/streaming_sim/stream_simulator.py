"""Small event-by-event simulation that complements the batch pipeline."""
from __future__ import annotations

import random
import time
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import TypedDict


class ConsumptionEvent(TypedDict):
    id_unidade_consumidora: str
    regiao: str
    consumo_kwh: float
    timestamp: str


def event_generator(n_events: int = 10, delay_seconds: float = 1.0) -> Iterator[ConsumptionEvent]:
    """Yield synthetic events at a controlled rate."""
    regions = ["NORDESTE", "SUDESTE", "SUL", "NORTE", "CENTRO-OESTE"]
    for _ in range(n_events):
        yield {
            "id_unidade_consumidora": f"UC-{random.randint(1000, 9999)}",
            "regiao": random.choice(regions),
            "consumo_kwh": round(random.uniform(50, 500), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        time.sleep(delay_seconds)


def process_event(event: ConsumptionEvent) -> None:
    """Print a simplified real-time alert for demonstration purposes."""
    alert = " ⚠️ CONSUMO ALTO" if event["consumo_kwh"] > 400 else ""
    print(f"[STREAM] {event['timestamp']} | {event['id_unidade_consumidora']} | {event['regiao']} | {event['consumo_kwh']} kWh{alert}")


if __name__ == "__main__":
    for item in event_generator(n_events=10, delay_seconds=0.5):
        process_event(item)
