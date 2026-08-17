import os
import sys

import pendulum

from airflow import DAG
from airflow.models import Variable
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import ExternalPythonOperator

tmp = Variable.get("tmp", default_var="/tmp")
venv_python = os.path.join(tmp, ".venv", "bin", "python")

default_args = {
    "owner": "dairy-campus",
    "retries": 1,
}


def _run_generate_data(tmp, api_key):
    os.chdir(tmp)
    os.environ["METEOSERVER_API_KEY"] = api_key
    sys.path.insert(0, tmp)
    import generate_data

    generate_data.main()


def _run_send_notifications(tmp, env_vars):
    os.chdir(tmp)
    os.environ.update(env_vars)
    sys.path.insert(0, tmp)
    import send_notification

    send_notification.main()


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

    generate_data = ExternalPythonOperator(
        task_id="generate_data",
        python=venv_python,
        python_callable=_run_generate_data,
        op_kwargs={"tmp": tmp, "api_key": secrets["METEOSERVER_API_KEY"]},
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

    send_notifications = ExternalPythonOperator(
        task_id="send_notifications",
        python=venv_python,
        python_callable=_run_send_notifications,
        op_kwargs={
            "tmp": tmp,
            "env_vars": {
                "SUPABASE_URL": secrets["SUPABASE_URL"],
                "SUPABASE_KEY": secrets["SUPABASE_KEY"],
                "VAPID_PUBLIC_KEY": secrets["VAPID_PUBLIC_KEY"],
                "VAPID_PRIVATE_KEY": secrets["VAPID_PRIVATE_KEY"],
                "VAPID_SUBJECT": secrets["VAPID_SUBJECT"],
            },
        },
    )

    git_pull >> generate_data >> commit_and_push >> send_notifications