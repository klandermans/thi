# airflo workflow logic

```
git pull --ff-only -> generate_data.py -> git add/commit/push docs/data/*.json -> send_notification.py -> cleanup /thi 
```

dag file: [dags/thi_pipeline_dag.py](dags/thi_pipeline_dag.py)
schedule: `41 6,9,12 * * *` (06:41, 09:41, 12:41 UTC) - same trigger as the old GitHub Actions workflow

# deploying

- no seperated venv
- generate_data.py and send_notification.py only non stdlib deps are requests (already installed) supabase and pywebpush (need adding to the dockerfile)
- two variables need to be set: 
  -tmp; clones into its own tmp/thi subfolder rather than the shared root
  -thi_secrets; 
  {"METEOSERVER_API_KEY": "", 
  "SUPABASE_URL": "", 
  "SUPABASE_KEY": "", 
  "VAPID_PUBLIC_KEY": "", 
  "VAPID_PRIVATE_KEY": "", 
  "VAPID_SUBJECT": "mailto:demo@example.com", 
  "GH_PAT": ""} 
  ###gh path with push acces to klandermans/thi