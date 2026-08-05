<h1 align="center">⚡ Utilities Medallion Pipeline</h1>

<p align="center">A local-first Data Engineering portfolio project for utility-energy consumption analytics.</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Apache%20Airflow-2.9.3-017CEE?logo=apacheairflow&logoColor=white" alt="Apache Airflow">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Pytest-tested-0A9EDC?logo=pytest&logoColor=white" alt="Pytest">
  <a href="https://github.com/arthurczo/utilities-etl-pipeline/actions/workflows/ci.yml"><img src="https://github.com/arthurczo/utilities-etl-pipeline/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <img src="https://img.shields.io/badge/License-MIT-22C55E" alt="MIT License">
</p>

## Project overview

This project processes synthetic utility meter readings through a Medallion pipeline and exposes business-ready consumption metrics. It demonstrates data quality controls, deterministic file-based CDC, Airflow orchestration and an interactive local dashboard—without requiring cloud credentials.

## Architecture

<p align="center"><img src="assets/architecture.svg" alt="Utilities platform architecture" width="100%"><br><em>Local-first Medallion processing with optional BigQuery and Looker Studio serving layers.</em></p>

## Technology stack

Python · Pandas · PyArrow · Apache Airflow · Docker Compose · Streamlit · Plotly · Pytest · Optional Google BigQuery

## Medallion architecture

| Layer | Responsibility | Output |
|---|---|---|
| Bronze | Preserves source data and ingestion metadata. | `bronze_*.parquet` |
| Silver | Validates, types, standardizes, deduplicates and flags IQR outliers. | `silver_*.parquet` |
| Gold | Produces regional monthly metrics and a top-consumer ranking. | `gold_*.parquet` |

CDC uses stable SHA-256 row hashes with a local checkpoint. Writes are atomic so incomplete Parquet artifacts are never published.

## Pipeline flow

<p align="center"><img src="assets/pipeline-flow.svg" alt="Daily pipeline flow" width="100%"><br><em>Airflow schedules daily processing; CDC observes inserts and updates without blocking ingestion.</em></p>

## Dashboard

The Streamlit dashboard reads the latest Gold artifacts from `data/gold/`. It includes KPI cards and filters for region, month and consumer, plus interactive Plotly views for consumption trends, regional totals, top consumers and outlier distribution.

<p align="center"><img src="assets/dashboard-preview.png" alt="Utilities dashboard overview" width="100%"><br><em>Dashboard overview generated from the local Gold layer.</em></p>

<p align="center"><img src="assets/dashboard-monthly-trend.png" alt="Monthly consumption trend" width="48%"> <img src="assets/dashboard-consumption-by-region.png" alt="Consumption by region" width="48%"><br><em>Interactive dashboard views: monthly trend and regional consumption.</em></p>

## Airflow orchestration

`utilities_medallion_pipeline` runs daily at 06:00 (America/Sao_Paulo), with two retries, a 20-minute task timeout, no catchup and one active run at a time. The DAG executes CDC → Bronze → Silver → Gold → charts.

## Project structure

```text
assets/       Diagrams, dashboard screenshots and demo guidance
dashboard/    Streamlit app, page and reusable components
dags/         Airflow DAG
data/         Local source, Medallion artifacts and runtime state (ignored)
src/          Bronze, Silver, Gold, CDC, visualization and shared utilities
tests/        Focused business-rule and dashboard-data tests
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for ownership details.

## Running locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_sample_data.py
python -m src.bronze.ingest
python -m src.silver.transform
python -m src.gold.aggregate
python -m src.visualization.generate_charts
streamlit run dashboard/app.py
```

`make generate`, `make run` and `make test` provide the same shortcuts on systems with GNU Make.

## Running with Docker

```bash
docker compose up airflow-init  # first run only
docker compose up
```

Open `http://localhost:8081` and sign in with `admin` / `admin`. The Docker stack runs Airflow and Postgres; the dashboard remains a local Streamlit process.

## Testing

```bash
python -m pytest -q
python -m compileall -q src dags scripts dashboard
```

GitHub Actions runs these checks on every push.

## Results

<p align="center"><img src="reports/consumo_mensal_por_regiao.png" alt="Monthly consumption by region report" width="48%"> <img src="reports/ranking_unidades_consumidoras.png" alt="Consumer ranking report" width="48%"><br><em>Static reports produced directly from Gold artifacts.</em></p>

## Future improvements

See [ROADMAP.md](ROADMAP.md). The next highest-value improvements are infrastructure-as-code for BigQuery/IAM and log-based CDC for a production data source.

## License

Distributed under the [MIT License](LICENSE).
