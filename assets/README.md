# Demo assets

The architecture diagrams are versioned SVGs so they remain crisp in GitHub and presentations.

`dashboard-preview.png` is deliberately pending until a real Streamlit session can be captured. Do not replace it with a mock or generated screenshot: launch the dashboard against Gold artifacts and capture the rendered browser.

The following files are intentionally **not** committed as fake demos:

| Expected file | How to record |
|---|---|
| `dashboard-demo.gif` | Run `streamlit run dashboard/app.py`, apply filters, then record the browser with ScreenToGif, Kap, or a browser recorder. |
| `airflow-demo.gif` | Start Docker Compose, trigger the DAG in Airflow and record the Graph/Grid view. Never expose credentials. |
| `pipeline-demo.gif` | Run `make generate && make run` and record the terminal plus generated reports. |

Keep each recording under 20 seconds, crop to the relevant application and use realistic data produced by this repository.
