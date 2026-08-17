# airflow

Runs the same pipeline as `deploy/vm/run_pipeline.sh` / the old
`.github/workflows/update_data.yml`, orchestrated by Airflow instead of cron.

# workflow logic

```
git pull --ff-only -> generate_data.py -> git add/commit/push docs/data/*.json -> send_notification.py
```

dag file: [dags/thi_pipeline_dag.py](dags/thi_pipeline_dag.py)
schedule: `41 6,9,12 * * *` (06:41, 09:41, 12:41 UTC) - same trigger as the old GitHub Actions workflow