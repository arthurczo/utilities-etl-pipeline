# Utilities ETL Pipeline

Pipeline de engenharia de dados para o setor de Utilities, simulando a
ingestão e disponibilização de dados de consumo de energia. Implementa
arquitetura medallion (Bronze → Silver → Gold), orquestração com Apache
Airflow, detecção de mudanças incremental (CDC), simulação de streaming
e carga no BigQuery.

## Stack

Python · Apache Airflow (Docker) · Google BigQuery · Pandas · Matplotlib

## Arquitetura

```
data/raw/  →  BRONZE  →  SILVER  →  GOLD  →  Visualização / BigQuery
(CSV bruto)  (ingestão)  (limpeza)  (agregação)
```

Orquestrado pela DAG `utilities_medallion_pipeline`, rodando diariamente
(batch). CDC roda em paralelo à ingestão, identificando registros novos
ou alterados desde a última execução.

## Decisões de arquitetura

**Medallion (Bronze/Silver/Gold).** Bronze preserva o dado exatamente como
recebido da fonte, sem regra de negócio — permite reprocessar a partir
daqui se um bug for encontrado nas camadas seguintes, sem depender da
fonte original. Silver aplica tipagem, deduplicação e padronização. Gold
entrega agregações prontas para consumo por BI/stakeholders.

**Outliers sinalizados, não descartados.** A camada Silver marca leituras
atípicas via IQR por região (`consumo_atipico`) em vez de removê-las —
um outlier pode ser sazonalidade real ou um vazamento/defeito de
equipamento, e essa decisão de negócio não deve ser tomada silenciosamente
pelo pipeline.

**CDC via hash + checkpoint.** Em produção, CDC normalmente usa
ferramentas como Debezium ou Datastream, que capturam mudanças direto do
log de transações da fonte (WAL/binlog) em tempo real. Aqui o conceito é
simulado com hash de linha + checkpoint entre execuções — sem a
infraestrutura de replicação, mas com o mesmo objetivo: processar só o
delta, não a base inteira.

**Streaming vs. Batch.** O pipeline principal é batch (schedule diário).
`src/streaming_sim/` simula processamento evento-a-evento para demonstrar
a diferença — em produção real no GCP, isso seria Pub/Sub + Dataflow.

**Airflow com LocalExecutor.** Optei por LocalExecutor em vez do
CeleryExecutor padrão do Airflow por ser suficiente para o volume deste
pipeline e não exigir Redis/workers adicionais — menos infraestrutura
para manter, sem abrir mão de retries e agendamento.

**Dataset sintético.** Os dados são gerados sinteticamente
(`scripts/generate_sample_data.py`), simulando sazonalidade por região e
~2% de anomalias reais de consumo, por não haver acesso a um portal de
dados abertos neste ambiente de desenvolvimento. A estrutura segue o
padrão de datasets públicos de consumo de energia (ANEEL/ONS); substituir
por um CSV real é só trocar `data/raw/consumo_energia.csv`.

## Estrutura

```
dags/                    DAG do Airflow
src/bronze/               ingestão bruta
src/silver/                limpeza, deduplicação, detecção de outlier
src/gold/                    agregações + carga no BigQuery
src/cdc/                       change data capture (simulado)
src/streaming_sim/              simulação de streaming
src/visualization/                geração de gráficos
scripts/generate_sample_data.py    geração do dataset de exemplo
reports/                             gráficos gerados
```

## Como rodar

```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

python scripts/generate_sample_data.py   # gera data/raw/consumo_energia.csv
python src/bronze/ingest.py
python src/silver/transform.py
python src/gold/aggregate.py
python src/visualization/generate_charts.py
```

### Via Airflow
```bash
docker compose up airflow-init   # primeira vez apenas
docker compose up
```
Acesse `http://localhost:8081` (`admin`/`admin`) e ative a DAG
`utilities_medallion_pipeline`.

### Conectar ao BigQuery / Looker Studio
1. Crie um projeto GCP, ative a API do BigQuery e gere uma chave de
   service account como `gcp-key.json` (não versionada — já no `.gitignore`)
2. Descomente as chamadas `load_to_bigquery(...)` em `src/gold/aggregate.py`
3. Conecte a tabela Gold do BigQuery direto como fonte de dados no Looker
   Studio para um dashboard interativo e ao vivo

## Resultados

| Consumo mensal por região | Ranking de unidades consumidoras |
|---|---|
| ![mensal](reports/consumo_mensal_por_regiao.png) | ![ranking](reports/ranking_unidades_consumidoras.png) |
