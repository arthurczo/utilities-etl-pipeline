"""Gera um dataset sintético de consumo de energia, maior e mais realista
que o exemplo inicial: 12 meses, múltiplas regiões e unidades consumidoras,
com sazonalidade, anomalias de consumo e sujeira de dados proposital
(nulos, duplicatas, inconsistência de texto) para validar as camadas
Silver/Gold do pipeline.

Nota: gerado sinteticamente por não haver acesso a portais de dados
abertos neste ambiente. Estruturalmente segue o padrão de datasets
públicos de consumo de energia (ex: ANEEL, ONS) — trocar por um CSV
real desses portais é só substituir data/raw/consumo_energia.csv.
"""
import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(seed=42)
OUT_PATH = Path(__file__).parent.parent / "data" / "raw" / "consumo_energia.csv"

REGIOES = {
    "SUDESTE": {"unidades": 40, "base": 320, "sazonalidade": 60},
    "NORDESTE": {"unidades": 30, "base": 410, "sazonalidade": 90},  # mais calor = mais consumo
    "SUL": {"unidades": 25, "base": 260, "sazonalidade": 80},       # inverno pesa mais
    "NORTE": {"unidades": 15, "base": 300, "sazonalidade": 50},
    "CENTRO-OESTE": {"unidades": 15, "base": 280, "sazonalidade": 55},
}

MESES = pd.date_range("2025-08-01", "2026-07-01", freq="MS")


def gerar():
    linhas = []
    uc_counter = 1000
    for regiao, cfg in REGIOES.items():
        for _ in range(cfg["unidades"]):
            uc_counter += 1
            uc_id = f"UC-{uc_counter}"
            for mes in MESES:
                # sazonalidade simples: pico em jan/fev (verão) e jun/jul (inverno-SUL)
                fator_sazonal = np.sin((mes.month / 12) * 2 * np.pi)
                consumo = cfg["base"] + fator_sazonal * cfg["sazonalidade"] + RNG.normal(0, 25)

                # ~2% de chance de anomalia real (vazamento, equipamento com defeito)
                if RNG.random() < 0.02:
                    consumo *= RNG.uniform(2.0, 3.5)

                linhas.append({
                    "id_unidade_consumidora": uc_id,
                    "regiao": regiao,
                    "data_leitura": mes.strftime("%Y-%m-%d"),
                    "consumo_kwh": round(max(consumo, 0), 2),
                })

    df = pd.DataFrame(linhas)

    # --- sujeira de dados proposital, pra validar Silver/CDC de verdade ---
    # 1. Inconsistência de texto em ~5% das linhas (o que a Silver precisa padronizar)
    idx_sujo = df.sample(frac=0.05, random_state=1).index
    df.loc[idx_sujo, "regiao"] = df.loc[idx_sujo, "regiao"].str.lower() + " "

    # 2. Nulos em ~1% das linhas (o que a Silver precisa descartar)
    idx_nulo = df.sample(frac=0.01, random_state=2).index
    df.loc[idx_nulo, "consumo_kwh"] = np.nan

    # 3. Duplicatas exatas em ~1% das linhas (o que a Silver precisa deduplicar)
    duplicatas = df.sample(frac=0.01, random_state=3)
    df = pd.concat([df, duplicatas], ignore_index=True)

    df = df.sample(frac=1, random_state=4).reset_index(drop=True)  # embaralha
    df.to_csv(OUT_PATH, index=False)
    print(f"Gerado {len(df)} registros em {OUT_PATH}")


if __name__ == "__main__":
    gerar()
