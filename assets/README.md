# Demo assets

The architecture diagrams are versioned SVGs so they remain crisp in GitHub and presentations. Dashboard screenshots are captured from the local Streamlit application using Gold artifacts.

The following GIFs are intentionally **not** committed as fake demos:

| Expected file | How to record |
|---|---|
| `dashboard-demo.gif` | Run `streamlit run dashboard/app.py`, apply filters, then record the browser with ScreenToGif, Kap, or a browser recorder. |
| `airflow-demo.gif` | Start Docker Compose, trigger the DAG in Airflow and record the Graph/Grid view. Never expose credentials. |
| `pipeline-demo.gif` | Run `make generate && make run` and record the terminal plus generated reports. |

Keep each recording under 20 seconds, crop to the relevant application and use realistic data produced by this repository.
