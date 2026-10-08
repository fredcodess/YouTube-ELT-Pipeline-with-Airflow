DROP TABLE IF EXISTS analytics_daily_growth;
CREATE TABLE analytics_daily_growth AS

WITH video_snapshots AS (
    SELECT
        "Snapshot_Date",
        "Video_ID",
        "Video_Title",
        "Video_Views",
        "Likes_Count",
        "Comments_Count",

        LAG("Video_Views") OVER (PARTITION BY "Video_ID" ORDER BY "Snapshot_Date"
        ) AS "Previous_Views",
        LAG("Likes_Count") OVER (PARTITION BY "Video_ID" ORDER BY "Snapshot_Date"
        ) AS "Previous_Likes",
        LAG("Comments_Count") OVER (PARTITION BY "Video_ID" ORDER BY "Snapshot_Date"
        ) AS "Previous_Comments"
    FROM core.yt_api
)
SELECT
    "Snapshot_Date",
    "Video_ID",
    "Video_Title",
    "Video_Views",
    "Likes_Count",
    "Comments_Count",
    "Previous_Views",
    "Previous_Likes",
    "Previous_Comments",

    CASE
        WHEN "Previous_Views" IS NOT NULL THEN "Video_Views" - "Previous_Views"
        ELSE NULL
    END AS "Views_Gained",
    CASE
        WHEN "Previous_Likes" IS NOT NULL THEN "Likes_Count" - "Previous_Likes"
        ELSE NULL
    END AS "Likes_Gained",
    CASE
        WHEN "Previous_Comments" IS NOT NULL THEN "Comments_Count" - "Previous_Comments"
        ELSE NULL
    END AS "Comments_Gained",
    CASE
        WHEN "Previous_Views" > 0
        THEN ROUND(
            (
                (
                    "Video_Views" - "Previous_Views"
                )::NUMERIC
                / "Previous_Views"
            ) * 100,
            4
        )
        ELSE NULL
    END AS "View_Growth_Percent"

FROM video_snapshots
ORDER BY "Snapshot_Date", "Video_ID";