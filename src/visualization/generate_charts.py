"""Gera visualizações estáticas a partir da camada Gold. """

import matplotlib.pyplot as plt
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from common.paths import DATA_DIR, get_data_dir

GOLD_DIR = DATA_DIR / "gold"
REPORTS_DIR = get_data_dir().parent / "reports"

plt.style.use("seaborn-v0_8-whitegrid")

def plot_consumo_mensal(mensal_filename: str) -> Path:
    df = pd.read_parquet(GOLD_DIR / mensal_filename)

    fig, ax = plt.subplots(figsize=(10, 5))
    for regiao, grupo in df.groupby("regiao"):
        ax.plot(grupo["ano_mes"], grupo["consumo_total_kwh"], marker="o", label=regiao)

    ax.set_title("Consumo total de energia por região (kWh/mês)")
    ax.set_xlabel("Mês")
    ax.set_ylabel("Consumo total (kWh)")
    ax.legend(title="Região", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=45)
    plt.tight_layout()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "consumo_mensal_por_regiao.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"[VIZ] Gráfico salvo em {out_path}")
    return out_path

def plot_ranking_unidades(ranking_filename: str) -> Path:
    df = pd.read_parquet(GOLD_DIR / ranking_filename).sort_values("consumo_medio_kwh")

    fig, ax = plt.subplots(figsize=(9, 7))
    cores = ["#d62728" if n > 0 else "#1f77b4" for n in df["qtd_leituras_atipicas"]]
    ax.barh(df["id_unidade_consumidora"], df["consumo_medio_kwh"], color=cores)
    ax.set_title("Top 20 unidades consumidoras por consumo médio\n(vermelho = com leitura atípica sinalizada)")
    ax.set_xlabel("Consumo médio (kWh)")
    plt.tight_layout()

    out_path = REPORTS_DIR / "ranking_unidades_consumidoras.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"[VIZ] Gráfico salvo em {out_path}")
    return out_path

if __name__ == "__main__":
    plot_consumo_mensal("gold_mensal_consumo_energia.parquet")
    plot_ranking_unidades("gold_ranking_consumo_energia.parquet")
