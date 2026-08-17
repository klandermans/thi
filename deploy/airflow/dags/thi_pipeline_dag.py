import pendulum

from airflow import DAG
from airflow.models import Variable
from airflow.providers.standard.operators.bash import BashOperator

tmp = Variable.get("tmp", default_var="/tmp")

ENV_SETUP = 'export AIRFLOW_VAR_ENV=BAR'

default_args = {
    "owner": "dairy-campus",
    "retries": 1,
}

with DAG(
    dag_id="thi_updater",
    description="get weather forecasts, pushing data to the site and sending notifications on update",
    start_date=pendulum.datetime(2026, 1, 1, tz="Europe/Amsterdam"),
    schedule="41 8,11,14 * * *",
    catchup=False,
    default_args=default_args,
    tags=["thi"],
) as dag:

    git_pull = BashOperator(
        task_id="git_pull",
        bash_command=f'cd "{tmp}" && git pull --ff-only',
    )

    secrets = Variable.get("thi_secrets", deserialize_json=True)

    generate_data = BashOperator(
        task_id="generate_data",
        bash_command=f'cd "{tmp}" && ' + ENV_SETUP + " && python generate_data.py",
        env={"METEOSERVER_API_KEY": secrets["METEOSERVER_API_KEY"]},
        append_env=True,
    )

    commit_and_push = BashOperator(
        task_id="commit_and_push",
        bash_command=f"""
set -uo pipefail
cd "{tmp}"
git config user.email "airflow@tmp.local"
git config user.name "THI Airflow"
git add docs/data/*.json
git diff --quiet && git diff --staged --quiet || (git commit -m "update weather data [skip ci]" && git push origin HEAD:main)
""",
    )

    send_notifications = BashOperator(
        task_id="send_notifications",
        bash_command=f'cd "{tmp}" && ' + ENV_SETUP + " && python send_notification.py",
        env={
            "SUPABASE_URL": secrets["SUPABASE_URL"],
            "SUPABASE_KEY": secrets["SUPABASE_KEY"],
            "VAPID_PUBLIC_KEY": secrets["VAPID_PUBLIC_KEY"],
            "VAPID_PRIVATE_KEY": secrets["VAPID_PRIVATE_KEY"],
            "VAPID_SUBJECT": secrets["VAPID_SUBJECT"],
        },
        append_env=True,
    )

    git_pull >> generate_data >> commit_and_push >> send_notifications