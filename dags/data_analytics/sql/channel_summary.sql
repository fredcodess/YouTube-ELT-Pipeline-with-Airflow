DROP TABLE IF EXISTS analytics_channel_summary;
CREATE TABLE analytics_channel_summary AS

WITH daily_metrics AS (
    SELECT
        "Snapshot_Date",
        COUNT(DISTINCT "Video_ID") AS "Total_Videos",
        SUM("Video_Views") AS "Total_Views",
        SUM("Likes_Count") AS "Total_Likes",
        SUM("Comments_Count") AS "Total_Comments",
        AVG("Video_Views") AS "Average_Views",
        AVG("Likes_Count") AS "Average_Likes",
        AVG("Comments_Count") AS "Average_Comments"
    FROM core.yt_api
    GROUP BY "Snapshot_Date"
),

growth AS (
    SELECT
        "Snapshot_Date",
        SUM(COALESCE("Views_Gained", 0)) AS "Views_Gained",
        SUM(COALESCE("Likes_Gained", 0)) AS "Likes_Gained",
        SUM(COALESCE("Comments_Gained", 0)) AS "Comments_Gained"
    FROM analytics_daily_growth
    GROUP BY "Snapshot_Date"
)
SELECT
    d."Snapshot_Date",
    d."Total_Videos",
    d."Total_Views",
    d."Total_Likes",
    d."Total_Comments",
    ROUND(d."Average_Views",2) AS "Average_Views",
    ROUND(d."Average_Likes",2) AS "Average_Likes",
    ROUND(d."Average_Comments",2) AS "Average_Comments",
    COALESCE(g."Views_Gained",0) AS "Views_Gained",
    COALESCE(g."Likes_Gained",0) AS "Likes_Gained",
    COALESCE(g."Comments_Gained",0) AS "Comments_Gained"

FROM daily_metrics d
LEFT JOIN growth g
    ON d."Snapshot_Date" = g."Snapshot_Date"
ORDER BY
    d."Snapshot_Date";