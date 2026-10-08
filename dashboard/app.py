import os

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(
    page_title="YouTube Analytics",
    page_icon="▶️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>

    /* Main application */
    .main {
        padding-top: 1rem;
    }

    /* Page title */
    .dashboard-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        color: #777;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid #e6e6e6;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        min-height: 115px;
    }

    .kpi-title {
        font-size: 0.85rem;
        color: #777;
        margin-bottom: 8px;
    }

    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #222;
    }

    .kpi-description {
        font-size: 0.75rem;
        color: #999;
        margin-top: 5px;
    }

    /* Section titles */
    .section-title {
        font-size: 1.25rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.7rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid #e6e6e6;
    }

    /* Remove excessive chart spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def get_engine():

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:wWfKvYbyD3kRnE4u@localhost:5433/elt_db",
    )
    return create_engine(database_url)

engine = get_engine()


@st.cache_data
def load_performance():
    query = """
        SELECT *
        FROM analytics_video_performance
        ORDER BY "Snapshot_Date";
    """
    return pd.read_sql(query, engine)

@st.cache_data
def load_growth():
    query = """
        SELECT *
        FROM analytics_daily_growth
        ORDER BY "Snapshot_Date";
    """
    return pd.read_sql(query, engine)


@st.cache_data
def load_summary():
    query = """
        SELECT *
        FROM analytics_channel_summary
        ORDER BY "Snapshot_Date";
    """
    return pd.read_sql(query, engine)

try:
    performance_df = load_performance()
    growth_df = load_growth()
    summary_df = load_summary()

    # Normalize dates
    performance_df["Snapshot_Date"] = pd.to_datetime(performance_df["Snapshot_Date"])

    growth_df["Snapshot_Date"] = pd.to_datetime(growth_df["Snapshot_Date"])

    summary_df["Snapshot_Date"] = pd.to_datetime(summary_df["Snapshot_Date"])

except Exception as e:
    st.error(f"Unable to load analytics data from PostgreSQL: {e}")
    st.stop()

if performance_df.empty:

    st.warning("No data is currently available in analytics_video_performance.")
    st.stop()


st.markdown(
    '<div class="dashboard-title">▶️ YouTube Analytics</div>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="dashboard-subtitle">
        Channel performance, audience engagement and video growth
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:

    st.markdown("## Dashboard Filters")

    st.markdown("---")

    # DATE FILTER
    min_date = performance_df[
        "Snapshot_Date"
    ].min().date()

    max_date = performance_df[
        "Snapshot_Date"
    ].max().date()

    date_range = st.date_input(
        "Snapshot period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:

        start_date, end_date = date_range

    else:

        start_date = min_date
        end_date = max_date

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    # VIDEO TYPE
    video_types = sorted(
        performance_df[
            "Video_Type"
        ]
        .dropna()
        .unique()
    )

    selected_types = st.multiselect(
        "Video type",
        video_types,
        default=video_types,
    )

    st.markdown("---")

    # DATA INFO
    st.caption(
        f"Data available: "
        f"{min_date.strftime('%d %b %Y')} → "
        f"{max_date.strftime('%d %b %Y')}"
    )


filtered_performance = performance_df[
    (
        performance_df[
            "Snapshot_Date"
        ].between(
            start_date,
            end_date,
        )
    )
    &
    (
        performance_df[
            "Video_Type"
        ].isin(selected_types)
    )
].copy()


if filtered_performance.empty:
    st.warning("No videos match the selected filters.")
    st.stop()

latest_snapshot = filtered_performance["Snapshot_Date"].max()

latest_data = filtered_performance[
    filtered_performance[
        "Snapshot_Date"
    ] == latest_snapshot
].copy()

total_videos = latest_data["Video_ID"].nunique()
total_views = latest_data["Video_Views"].sum()
total_likes = latest_data["Likes_Count"].sum()
total_comments = latest_data["Comments_Count"].sum()

latest_growth = growth_df[
    growth_df[
        "Snapshot_Date"
    ] == latest_snapshot
].copy()


if latest_growth.empty:
    views_gained = 0
else:
    views_gained = latest_growth["Views_Gained"].sum()

    if pd.isna(views_gained):
        views_gained = 0

st.markdown(
    '<div class="section-title">Channel Overview</div>',
    unsafe_allow_html=True,
)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Videos</div>
            <div class="kpi-value">{total_videos:,}</div>
            <div class="kpi-description">Latest snapshot</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi2:

    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Views</div>
            <div class="kpi-value">{total_views:,.0f}</div>
            <div class="kpi-description">Latest snapshot</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Likes</div>
            <div class="kpi-value">{total_likes:,.0f}</div>
            <div class="kpi-description">Latest snapshot</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi4:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Comments</div>
            <div class="kpi-value">{total_comments:,.0f}</div>
            <div class="kpi-description">Latest snapshot</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi5:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Views Gained</div>
            <div class="kpi-value">{views_gained:,.0f}</div>
            <div class="kpi-description">Since previous snapshot</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    '<div class="section-title">Channel Growth</div>',
    unsafe_allow_html=True,
)

summary_filtered = summary_df[
    summary_df[
        "Snapshot_Date"
    ].between(
        start_date,
        end_date,
    )
].copy()


if not summary_filtered.empty:
    fig_views = px.line(
        summary_filtered,
        x="Snapshot_Date",
        y="Total_Views",
        markers=True,
    )
    fig_views.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20,),
        xaxis_title=None,
        yaxis_title="Total Views",
        hovermode="x unified",
    )

    fig_views.update_traces(line=dict(width=3), marker=dict(size=7),)

    st.plotly_chart(
        fig_views,
        use_container_width=True,
    )

left_col, right_col = st.columns(2)

with left_col:
    st.markdown(
        '<div class="section-title">Daily Views Gained</div>',
        unsafe_allow_html=True,
    )

    growth_filtered = growth_df[
        growth_df[
            "Snapshot_Date"
        ].between(
            start_date,
            end_date,
        )
    ].copy()

    if not growth_filtered.empty:

        daily_growth = (
            growth_filtered
            .groupby(
                "Snapshot_Date",
                as_index=False,
            )[
                "Views_Gained"
            ]
            .sum()
        )

        fig_growth = px.bar(
            daily_growth,
            x="Snapshot_Date",
            y="Views_Gained",
        )

        fig_growth.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
            xaxis_title=None,
            yaxis_title="Views Gained",
        )

        st.plotly_chart(
            fig_growth,
            use_container_width=True,
        )

with right_col:

    st.markdown(
        '<div class="section-title">Video Portfolio</div>',
        unsafe_allow_html=True,
    )
    type_summary = (
        latest_data
        .groupby(
            "Video_Type",
            as_index=False,
        )
        .agg(
            Videos=(
                "Video_ID",
                "nunique",
            ),
            Views=(
                "Video_Views",
                "sum",
            ),
        )
    )

    if not type_summary.empty:

        fig_donut = px.pie(
            type_summary,
            names="Video_Type",
            values="Videos",
            hole=0.58,
        )

        fig_donut.update_layout(
            height=380,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
            showlegend=True,
            legend_title_text="Video Type",
        )

        fig_donut.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Videos: %{value}<br>"
                "Share: %{percent}"
                "<extra></extra>"
            ),
        )

        st.plotly_chart(
            fig_donut,
            use_container_width=True,
        )

st.markdown(
    '<div class="section-title">Top Performing Videos</div>',
    unsafe_allow_html=True,
)

top_videos = (
    latest_data
    .sort_values(
        "Video_Views",
        ascending=False,
    )
    .head(10)
)

if not top_videos.empty:

    fig_top = px.bar(
        top_videos.sort_values(
            "Video_Views"
        ),
        x="Video_Views",
        y="Video_Title",
        orientation="h",
    )

    fig_top.update_layout(
        height=500,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
        xaxis_title="Views",
        yaxis_title=None,
    )

    st.plotly_chart(
        fig_top,
        use_container_width=True,
    )


left_col, right_col = st.columns(2)

with left_col:

    st.markdown(
        '<div class="section-title">Top Engagement Rate</div>',
        unsafe_allow_html=True,
    )
    engagement = (
        latest_data
        .sort_values(
            "Engagement_Rate",
            ascending=False,
        )
        .head(10)
    )

    if not engagement.empty:

        fig_engagement = px.bar(
            engagement.sort_values(
                "Engagement_Rate"
            ),
            x="Engagement_Rate",
            y="Video_Title",
            orientation="h",
        )

        fig_engagement.update_layout(
            height=450,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
            xaxis_title="Engagement Rate (%)",
            yaxis_title=None,
        )

        st.plotly_chart(
            fig_engagement,
            use_container_width=True,
        )

with right_col:

    st.markdown(
        '<div class="section-title">Views by Video Type</div>',
        unsafe_allow_html=True,
    )
    type_views = (
        latest_data
        .groupby(
            "Video_Type",
            as_index=False,
        )[
            "Video_Views"
        ]
        .sum()
    )

    if not type_views.empty:

        fig_type_views = px.bar(
            type_views,
            x="Video_Type",
            y="Video_Views",
        )

        fig_type_views.update_layout(
            height=450,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
            xaxis_title="Video Type",
            yaxis_title="Views",
        )

        st.plotly_chart(
            fig_type_views,
            use_container_width=True,
        )

st.markdown(
    '<div class="section-title">Video Performance Details</div>',
    unsafe_allow_html=True,
)

display_columns = [
    "Snapshot_Date",
    "Video_ID",
    "Video_Title",
    "Video_Type",
    "Video_Views",
    "Likes_Count",
    "Comments_Count",
    "Like_Rate",
    "Comment_Rate",
    "Engagement_Rate",
]

available_columns = [
    column
    for column in display_columns
    if column in latest_data.columns
]

display_df = latest_data[
    available_columns
].sort_values(
    "Video_Views",
    ascending=False,
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
)

st.divider()

st.caption(
    f"Latest data snapshot: "
    f"{latest_snapshot.strftime('%d %B %Y')}"
)