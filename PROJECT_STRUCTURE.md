# Project structure

```text
assets/       Versioned diagrams, dashboard screenshots and demo-recording guidance
dashboard/    Streamlit app, page and reusable data/chart components
dags/         Airflow orchestration
data/         Local raw, Medallion artifacts and runtime state (ignored)
src/          Pipeline implementation by layer
tests/        Focused business-rule tests
```

`src/common/` owns paths and atomic artifact I/O. Each Medallion layer owns its transformation concern; orchestration remains in `dags/` and presentation in `dashboard/`.
