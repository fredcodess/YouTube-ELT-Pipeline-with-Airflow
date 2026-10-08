# YouTube Analytics ELT Pipeline | Airflow, Docker & PostgreSQL

> An end-to-end data engineering project that extracts YouTube data through an API, orchestrates an ELT pipeline with Apache Airflow, stores historical data in PostgreSQL, validates data quality with Soda, builds analytical datasets with SQL, and delivers insights through a Streamlit dashboard.

---

## About Me

I'm a Computer Science graduate currently studying for an MSc in Artificial Intelligence.

I'm transitioning into data engineering because I enjoy the engineering problems behind data products, from getting data from sources, structuring it properly, automating the workflow, validating its quality, and making it usable for analysis and decision-making.

My background has given me experience across Python, SQL, databases, cloud technologies, data analysis and machine learning. During my Computer Science degree I developed foundations in databases, data engineering, software engineering and cloud computing. More recently, my work in AI research has involved building Python-based pipelines, modular systems, testing, debugging and performance optimisation.

---

## Why I Built This Project

As someone interested in YouTube content creation, I wanted to build my own version of the analytics tools that creators typically pay for. I wanted to go beyond simply viewing YouTube's basic metrics and build something that could track historical performance, identify video growth, measure engagement, and turn the data into useful insights.

Building it myself also gave me an opportunity to explore the data engineering behind an analytics product, from collecting the data through an API and storing historical snapshots, to transforming, validating and presenting it in a dashboard.

---

# Architecture

![Screenshot](https://github.com/fredcodess/YouTube-ELT-Pipeline-with-Airflow/blob/main/images/YouTube%20Data%20Pipeline%20Architecture.png?raw=true)

---

# Technology Stack

| Technology | For |
|---|---|
| **Python** | API extraction, data processing and orchestration logic |
| **YouTube Data API** | External data source |
| **Apache Airflow** | Workflow orchestration |
| **PostgreSQL** | Data warehouse |
| **SQL** | Data transformation and analytics |
| **Soda** | Data quality validation |
| **Streamlit** | Analytics dashboard |
| **Docker** | Local infrastructure and service isolation |
| **pytest** | Testing |
| **Git / GitHub** | Version control and project management |

---

# Data Pipeline

## 1. Extraction

The pipeline starts by interacting with the YouTube API.

1. Identifying the target youtube channel.
2. Retrieving video IDs.
3. Extracting video metadata and metrics.
4. Writing the extracted data to a dated JSON snapshot.

Each snapshot is stored using the following naming convention:

```text
YT_data_YYYY-MM-DD.json
```

For example:

```text
YT_data_2026-10-07.json
```

The snapshot date is important because YouTube metrics such as views, likes and comments change over time.

---

# 2. Historical Snapshots

One of the main design decisions in this project was to preserve historical states.

A video is therefore not uniquely identified by `Video_ID` alone.

The warehouse uses:

```text
Snapshot_Date + Video_ID
```

as the logical unique key.

For example:

```text
Snapshot Date    Video ID    Views
------------------------------------
2026-10-01       ABC123      10,000
2026-10-02       ABC123      11,500
2026-10-04       ABC123      15,200
2026-10-07       ABC123      19,800
```

This makes it possible to answer questions such as:

- How quickly did a video gain views?
- Which videos are growing fastest?
- How has channel performance changed over time?
- How does engagement change between snapshots?

Without historical snapshots, those questions would not be possible.

---

# 3. Staging Layer

The staging layer stores the API data in a structure close to its source representation.

Schema:

```text
staging.yt_api
```

The staging layer contains:

- Snapshot date
- Video ID
- Video title
- Upload date
- Duration
- Views
- Likes
- Comments

The purpose of this layer is to provide a reliable boundary between external data and the transformed warehouse model.

---

# 4. Core Layer

The core layer transforms the staging data into a cleaner analytical structure.

Schema:

```text
core.yt_api
```

Transformations include:

- Converting metric values into numeric database types.
- Converting ISO-8601 video durations into PostgreSQL `TIME`.
- Classifying videos as `Shorts` or `Normal`.
- Preserving snapshot history.

The core table uses:

```text
PRIMARY KEY (Snapshot_Date, Video_ID)
```

This allows the same video to appear across multiple historical snapshots.

---

# 5. Data Quality

Data quality is treated as a separate stage rather than assuming that successfully loading data means the data is correct.

Soda is used to validate both:

```text
staging
   ↓
core
```

The data-quality workflow is orchestrated by Airflow.

If the quality checks fail, downstream processing should not continue.

This separation allows the pipeline to distinguish between:

```text
Pipeline succeeded
```

and:

```text
Pipeline completed, but the data should not be trusted.
```

---

# 6. Analytics Layer

The analytics layer is built using SQL transformations over the core warehouse.

Three analytical datasets are currently produced.

## Video Performance

```text
analytics_video_performance
```

This provides the latest available state of each video.

Metrics include:

- Views
- Likes
- Comments
- Like rate
- Comment rate
- Engagement rate
- Video age
- Video type

Example engagement calculation:

```text
Engagement Rate =
(Likes + Comments) / Views × 100
```

---

## Daily Growth

```text
analytics_daily_growth
```

This dataset compares consecutive snapshots for each video.

It calculates:

- Previous views
- Previous likes
- Previous comments
- Views gained
- Likes gained
- Comments gained
- View growth percentage

Window functions such as `LAG()` are used to compare a video with its previous snapshot.

Conceptually:

```text
Current Views - Previous Views = Views Gained
```

This transforms static API snapshots into a time-series view of video performance.

---

## Channel Summary

```text
analytics_channel_summary
```

This provides channel-level metrics for each snapshot date.

Metrics include:

- Total videos
- Total views
- Total likes
- Total comments
- Average views
- Average likes
- Average comments
- Views gained
- Likes gained
- Comments gained

This dataset is designed specifically for high-level reporting and dashboarding.

---

# 7. Streamlit Dashboard

The final layer is an interactive Streamlit dashboard.

The dashboard provides:

### KPI cards

- Total videos
- Total views
- Total likes
- Total comments
- Views gained

### Visualisations

- Channel views over time
- Daily views gained
- Top performing videos
- Engagement rate
- Views by video type
- Shorts vs Normal video composition

### Filters

- Snapshot date
- Video type

The dashboard is intentionally built on top of the analytics layer rather than querying and transforming the raw API data itself.

This keeps the analytical logic in the data platform and the dashboard focused on presentation.

---

# Screenshots

## Airflow Orchestration

The Airflow UI shows the automated workflow and task dependencies.

![Airflow pipeline](https://github.com/fredcodess/YouTube-ELT-Pipeline-with-Airflow/blob/main/images/airflow.png?raw=true)

The workflow is structured around:

```text
produce_json
     ↓
update_db
     ↓
data_quality
     ↓
youtube_data_analytics
```

---

## Docker Infrastructure

The project runs its data infrastructure using Docker.

![Docker containers](https://github.com/fredcodess/YouTube-ELT-Pipeline-with-Airflow/blob/main/images/docker.png?raw=true)

Docker provides isolated services for the local data platform, including PostgreSQL and Airflow.

---

## Streamlit Dashboard

The final analytical output is delivered through an interactive Streamlit dashboard.

![Streamlit dashboard](https://github.com/fredcodess/YouTube-ELT-Pipeline-with-Airflow/blob/main/images/dashboard.png?raw=true)

The dashboard allows the user to explore channel performance, video growth and engagement.

---

# Running the Project

## 1. Start the infrastructure

```bash
docker compose up -d
```

Check the containers:

```bash
docker compose ps
```
---

## 2. Access Airflow

Open:

```text
http://localhost:8080
```

The main DAGs are:

```text
produce_json
update_db
data_quality
youtube_data_analytics
```

---

## 3. Run the pipeline

The production workflow is designed so that the API extraction triggers the downstream processing.

The intended flow is:

```text
YouTube API
    ↓
JSON snapshot
    ↓
Staging
    ↓
Core
    ↓
Data Quality
    ↓
Analytics
```

---

## 4. Run Streamlit

Start the dashboard from the project root:

```bash
streamlit run dashboard/app.py
```

Then open:

```text
http://localhost:8501
```

---

## Orchestration with Airflow

Airflow is used to turn individual Python and SQL operations into a repeatable workflow.

The goal is not simply to run scripts, but to define dependencies between stages.

For example:

```text
Extraction
    ↓
Loading
    ↓
Transformation
    ↓
Quality
    ↓
Analytics
```

This also makes failures easier to identify and recover from.

---

# Testing and Reliability

The project uses multiple layers of validation.

### Python validation

Python modules are syntax-checked before deployment:

```bash
python -m py_compile ...
```

### Data quality

Soda validates the staging and core datasets.

### Database constraints

The warehouse uses:

```text
NOT NULL
PRIMARY KEY
```

constraints to protect the structure of the data.

---

# The Data School

I’m a Computer Science graduate and have recently completed an MSc in Artificial Intelligence. Over the last year, I’ve become increasingly interested in the engineering side of working with data and have been deliberately building my skills towards a career in data engineering. Alongside my academic and practical experience with Python, SQL and data analysis, I completed a Data Engineering course covering PostgreSQL, Python, PySpark, Spark SQL and Databricks, including hands-on data pipeline work on Udemy.  

I’m applying because I want to take that foundation further in a professional environment. I’m particularly interested in learning how experienced data engineers approach real-world problems, build reliable data platforms and work with technologies such as cloud platforms and modern data engineering tools. I also like that The Data School combines structured training with client work, as I think that would be a great environment for me to learn, contribute and develop into a well-rounded data engineer. 

I’m naturally curious and enjoy figuring things out when I come across something I don’t understand. I’m also comfortable learning independently, but I value feedback and working with people who have more experience than me. At this stage of my career, I’m looking for an environment where I can keep learning while being challenged to apply what I know to real problems.

---


# Author

**Fredick Gyan Boakye**

Computer Science graduate | MSc Artificial Intelligence

📧 fredgyancodes@gmail.com
