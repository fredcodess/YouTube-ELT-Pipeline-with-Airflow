from datawarehouse.data_utils import (
    get_conn_cursor,
    close_conn_cursor,
    create_schema,
    create_table,
)
from datawarehouse.data_loading import load_data
from datawarehouse.data_modification import insert_rows
from datawarehouse.data_transformation import transform_data
import logging
from airflow.decorators import task

logger = logging.getLogger(__name__)

@task
def staging_table():
    schema = "staging"
    conn, cur = None, None

    try:
        conn, cur = get_conn_cursor()
        create_schema(schema)
        create_table(schema)
        yt_data = load_data()

        for row in yt_data:
            insert_rows(cur,conn,schema,row)

        logger.info(f"{schema} table loaded successfully")

    except Exception as e:
        logger.error(f"An error occurred loading {schema}: {e}")
        raise

    finally:
        if conn and cur:
            close_conn_cursor(conn, cur)


@task
def core_table():
    schema = "core"
    conn, cur = None, None

    try:
        conn, cur = get_conn_cursor()
        create_schema(schema)
        create_table(schema)
        cur.execute("SELECT * FROM staging.yt_api;")

        rows = cur.fetchall()

        for row in rows:
            transformed_row = transform_data(dict(row))
            insert_rows(cur,conn,schema,transformed_row)

        logger.info(f"{schema} table loaded successfully")

    except Exception as e:
        logger.error(f"An error occurred loading {schema}: {e}")
        raise

    finally:
        if conn and cur:
            close_conn_cursor(conn, cur)