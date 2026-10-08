from pathlib import Path

from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook

import pendulum


POSTGRES_CONN_ID = "postgres_db_yt_elt"
SQL_DIR = Path(__file__).parent / "sql"


def execute_sql_file(filename):
    sql_file = SQL_DIR / filename

    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file}")

    sql = sql_file.read_text()
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    hook.run(sql)


with DAG(
    dag_id="youtube_data_analytics",
    start_date=pendulum.datetime(2026,7,1,tz="Europe/Malta"),
    schedule=None,
    catchup=False,
    tags=["youtube", "analytics"],
    description=(
        "Build YouTube analytics tables from the warehouse"
    ),

) as dag:

    @task
    def video_performance():
        execute_sql_file("video_performance.sql")

    @task
    def daily_growth():
        execute_sql_file("daily_growth.sql")

    @task
    def channel_summary():
        execute_sql_file("channel_summary.sql")

    performance = video_performance()
    growth = daily_growth()
    summary = channel_summary()

    performance >> growth >> summary