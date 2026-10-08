import logging

logger = logging.getLogger(__name__)
table = "yt_api"

def insert_rows(cur, conn, schema, row):
    try:
        if schema == "staging":
            cur.execute(
                f"""
                INSERT INTO {schema}.{table}
                (
                    "Snapshot_Date",
                    "Video_ID",
                    "Video_Title",
                    "Upload_Date",
                    "Duration",
                    "Video_Views",
                    "Likes_Count",
                    "Comments_Count"
                )
                VALUES
                (
                    %(Snapshot_Date)s,
                    %(video_id)s,
                    %(title)s,
                    %(publishedAt)s,
                    %(duration)s,
                    %(viewCount)s,
                    %(likeCount)s,
                    %(commentCount)s
                )
                ON CONFLICT ("Snapshot_Date", "Video_ID")
                DO UPDATE SET
                    "Video_Title" = EXCLUDED."Video_Title",
                    "Video_Views" = EXCLUDED."Video_Views",
                    "Likes_Count" = EXCLUDED."Likes_Count",
                    "Comments_Count" = EXCLUDED."Comments_Count";
                """,
                row,
            )
            video_id = "video_id"
        else:
            cur.execute(
                f"""
                INSERT INTO {schema}.{table}
                (
                    "Snapshot_Date",
                    "Video_ID",
                    "Video_Title",
                    "Upload_Date",
                    "Duration",
                    "Video_Type",
                    "Video_Views",
                    "Likes_Count",
                    "Comments_Count"
                )
                VALUES
                (
                    %(Snapshot_Date)s,
                    %(Video_ID)s,
                    %(Video_Title)s,
                    %(Upload_Date)s,
                    %(Duration)s,
                    %(Video_Type)s,
                    %(Video_Views)s,
                    %(Likes_Count)s,
                    %(Comments_Count)s
                )
                ON CONFLICT ("Snapshot_Date", "Video_ID")
                DO UPDATE SET
                    "Video_Title" = EXCLUDED."Video_Title",
                    "Video_Views" = EXCLUDED."Video_Views",
                    "Likes_Count" = EXCLUDED."Likes_Count",
                    "Comments_Count" = EXCLUDED."Comments_Count",
                    "Duration" = EXCLUDED."Duration",
                    "Video_Type" = EXCLUDED."Video_Type";
                """,
                row,
            )
            video_id = "Video_ID"
        conn.commit()
        logger.info(f"Inserted/updated {schema} row: {row[video_id]}")

    except Exception as e:
        logger.error(f"Error inserting row: {e}")
        raise


def update_rows(cur, conn, schema, row):
    insert_rows(cur, conn, schema, row)

def delete_rows(cur, conn, schema, ids_to_delete):
    logger.info(
        f"Skipping deletion of historical records: "
        f"{len(ids_to_delete)} IDs"
    )