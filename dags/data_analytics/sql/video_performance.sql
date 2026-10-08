DROP TABLE IF EXISTS analytics_video_performance;
CREATE TABLE analytics_video_performance AS

WITH latest_snapshot AS (
    SELECT
        "Video_ID",
        MAX("Snapshot_Date") AS "Snapshot_Date"
    FROM core.yt_api
    GROUP BY "Video_ID"
),

latest_videos AS (
    SELECT
        y."Snapshot_Date",
        y."Video_ID",
        y."Video_Title",
        y."Upload_Date",
        y."Duration",
        y."Video_Type",
        y."Video_Views",
        y."Likes_Count",
        y."Comments_Count"
    FROM core.yt_api y
    INNER JOIN latest_snapshot l
        ON y."Video_ID" = l."Video_ID"
        AND y."Snapshot_Date" = l."Snapshot_Date"
)

SELECT
    "Snapshot_Date",
    "Video_ID",
    "Video_Title",
    "Upload_Date",
    "Duration",
    "Video_Type",
    "Video_Views",
    "Likes_Count",
    "Comments_Count",

    CASE
        WHEN "Video_Views" > 0
        THEN ROUND(
            ("Likes_Count"::NUMERIC / "Video_Views") * 100,
            4
        )
        ELSE 0
    END AS "Like_Rate",
    CASE
        WHEN "Video_Views" > 0
        THEN ROUND(
            ("Comments_Count"::NUMERIC / "Video_Views") * 100,
            4
        )
        ELSE 0
    END AS "Comment_Rate",
    CASE
        WHEN "Video_Views" > 0
        THEN ROUND(
            (
                ("Likes_Count" + "Comments_Count")::NUMERIC
                / "Video_Views"
            ) * 100,
            4
        )
        ELSE 0
    END AS "Engagement_Rate",

    CURRENT_DATE - "Upload_Date"::DATE
        AS "Video_Age_Days"
FROM latest_videos;