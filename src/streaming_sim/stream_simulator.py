"""Simulador de streaming — processamento evento-a-evento em vez de lote. """

import time
import random
from datetime import datetime, timezone


def event_generator(n_events: int = 10, delay_seconds: float = 1.0):
    regioes = ["NORDESTE", "SUDESTE", "SUL", "NORTE", "CENTRO-OESTE"]
    for _ in range(n_events):
        event = {
            "id_unidade_consumidora": f"UC-{random.randint(1000, 9999)}",
            "regiao": random.choice(regioes),
            "consumo_kwh": round(random.uniform(50, 500), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        yield event
        time.sleep(delay_seconds)


def process_event(event: dict):
    alerta = " ⚠️ CONSUMO ALTO" if event["consumo_kwh"] > 400 else ""
    print(f"[STREAM] {event['timestamp']} | {event['id_unidade_consumidora']} "
          f"| {event['regiao']} | {event['consumo_kwh']} kWh{alerta}")


if __name__ == "__main__":
    for evt in event_generator(n_events=10, delay_seconds=0.5):
        process_event(evt)
