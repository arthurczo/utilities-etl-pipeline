.PHONY: generate run test lint docker-init docker-up

generate:
	python scripts/generate_sample_data.py

run:
	python -m src.bronze.ingest
	python -m src.silver.transform
	python -m src.gold.aggregate
	python -m src.visualization.generate_charts

test:
	python -m pytest -q

lint:
	python -m compileall -q src dags scripts

docker-init:
	docker compose up airflow-init

docker-up:
	docker compose up
