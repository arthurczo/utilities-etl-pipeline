# Utilities Medallion Pipeline

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/Airflow-2.9.3-017CEE?logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)

Pipeline de portfólio para Engenharia de Dados que processa leituras sintéticas de consumo de energia. O projeto demonstra uma arquitetura Medallion, controles de qualidade, CDC baseado em estado e orquestração diária com Airflow.

## Arquitetura

```text
CSV source → Bronze (preservação + metadados) → Silver (qualidade) → Gold (métricas) → Charts / BigQuery
                 └──────────────── CDC: hash SHA-256 + checkpoint ────────────────┘
```

| Camada | Responsabilidade |
|---|---|
| Bronze | Preserva a entrada e registra origem e horário de ingestão. |
| Silver | Aplica tipagem, padroniza região, remove chaves inválidas/duplicadas e sinaliza outliers por IQR. |
| Gold | Publica consumo mensal regional, variação mês a mês e ranking das unidades. |

O CDC é uma simulação para arquivos: hashes estáveis detectam inserções e alterações e o checkpoint fica em `data/state/`. Em produção, substituir por CDC log-based (por exemplo, Datastream ou Debezium). A execução é idempotente: cada camada substitui seu artefato Parquet de forma atômica.

## Estrutura

```text
dags/       Orquestração Airflow
src/        Camadas Bronze, Silver, Gold, CDC, streaming e visualização
data/       Dados locais e estado de execução (não versionados)
tests/      Testes de regras de negócio críticas
reports/    Gráficos gerados
```

## Executar localmente

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate  |  Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
make generate  # ou: python scripts/generate_sample_data.py
make run
make test
```

Sem `make`, use `python -m src.bronze.ingest`, `python -m src.silver.transform` e `python -m src.gold.aggregate` a partir da raiz. A etapa de geração produz dados sintéticos determinísticos com duplicatas, valores nulos e inconsistências de texto para exercitar a Silver.

## Airflow e BigQuery

```bash
docker compose up airflow-init  # somente na primeira vez
docker compose up
```

Abra `http://localhost:8081` com `admin` / `admin` e habilite `utilities_medallion_pipeline`. A DAG executa diariamente às 06:00 (America/Sao_Paulo), sem backfill e com retries/timeout definidos.

BigQuery é opcional. Copie `.env.example`, configure `GOOGLE_APPLICATION_CREDENTIALS` com uma service account fora do Git e chame `load_to_bigquery` com um identificador `project.dataset.table`. A carga usa substituição atômica da tabela alvo; o dataset deve existir previamente.

## Resultados

| Consumo mensal por região | Ranking de unidades consumidoras |
|---|---|
| ![Consumo mensal](reports/consumo_mensal_por_regiao.png) | ![Ranking](reports/ranking_unidades_consumidoras.png) |
