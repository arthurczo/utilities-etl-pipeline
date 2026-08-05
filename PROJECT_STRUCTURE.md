# Project structure

```text
assets/       Versioned architecture diagrams and demo-recording guidance
dashboard/    Streamlit app, page and reusable display/data components
dags/         Airflow orchestration
data/         Local raw, Medallion artifacts and runtime state (ignored)
src/          Pipeline implementation by layer
tests/        Focused business-rule tests
```

`src/common/` owns paths and atomic artifact I/O. Each Medallion layer owns only its transformation concern; orchestration remains in `dags/`.
