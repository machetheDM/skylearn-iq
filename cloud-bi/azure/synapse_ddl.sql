-- ============================================================
-- SKYLearn IQ — Synapse Analytics Serverless SQL DDL
-- ============================================================
-- Run this in Azure Synapse Studio → SQL Script (serverless pool)
-- Replace 'skylearndatalake' with your actual storage account name.
-- ============================================================

-- 1. Create database
CREATE DATABASE IF NOT EXISTS skylearn_iq;
USE skylearn_iq;

-- 2. Create data source pointing to Gold layer on ADLS Gen2
CREATE EXTERNAL DATA SOURCE gold_adls
WITH (
    LOCATION = 'https://skylearndatalake.dfs.core.windows.net/gold'
);

CREATE EXTERNAL DATA SOURCE silver_adls
WITH (
    LOCATION = 'https://skylearndatalake.dfs.core.windows.net/silver'
);

-- 3. External tables — Gold layer (used by Power BI)

CREATE EXTERNAL TABLE gold_subject_performance (
    subject_name    NVARCHAR(100),
    total_sessions  INT,
    avg_score       FLOAT,
    pass_rate       FLOAT,
    unique_learners INT,
    difficulty      NVARCHAR(20)
)
WITH (
    DATA_SOURCE = gold_adls,
    LOCATION    = 'gold_subject_performance.parquet',
    FILE_FORMAT = PARQUET
);

CREATE EXTERNAL TABLE gold_learner_cohorts (
    learner_id       INT,
    user_id          INT,
    learner_name     NVARCHAR(100),
    grade            INT,
    track            NVARCHAR(50),
    total_sessions   INT,
    avg_score        FLOAT,
    pass_rate        FLOAT,
    risk_flag        NVARCHAR(20),
    performance_band NVARCHAR(30),
    last_active      DATETIME2
)
WITH (
    DATA_SOURCE = gold_adls,
    LOCATION    = 'gold_learner_cohorts.parquet',
    FILE_FORMAT = PARQUET
);

CREATE EXTERNAL TABLE gold_monthly_trends (
    session_month    DATE,
    session_count    INT,
    avg_score        FLOAT,
    pass_rate        FLOAT,
    learners_active  INT
)
WITH (
    DATA_SOURCE = gold_adls,
    LOCATION    = 'gold_monthly_trends.parquet',
    FILE_FORMAT = PARQUET
);

CREATE EXTERNAL TABLE gold_assessment_stats (
    assessment_id    INT,
    assessment_title NVARCHAR(200),
    subject_name     NVARCHAR(100),
    total_attempts   INT,
    avg_score        FLOAT,
    pass_rate        FLOAT,
    avg_duration     FLOAT
)
WITH (
    DATA_SOURCE = gold_adls,
    LOCATION    = 'gold_assessment_stats.parquet',
    FILE_FORMAT = PARQUET
);

-- 4. Power BI–ready views

CREATE VIEW vw_at_risk_learners AS
SELECT learner_name, grade, track, total_sessions, avg_score, pass_rate, last_active
FROM gold_learner_cohorts
WHERE risk_flag = 'At Risk'
ORDER BY avg_score ASC;

CREATE VIEW vw_subject_summary AS
SELECT subject_name, avg_score, pass_rate, total_sessions, difficulty
FROM gold_subject_performance
ORDER BY avg_score DESC;

CREATE VIEW vw_cohort_overview AS
SELECT
    performance_band,
    COUNT(*)                    AS learner_count,
    AVG(avg_score)              AS band_avg_score,
    AVG(pass_rate) * 100        AS band_pass_rate_pct
FROM gold_learner_cohorts
GROUP BY performance_band;
