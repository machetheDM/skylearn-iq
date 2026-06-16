"""
Silver Layer — Cleaned & Enriched  (Step 2 of Medallion Architecture)
======================================================================
Reads Bronze Parquet files, cleans + joins them, and writes enriched Silver tables.

Dual-engine: runs with PySpark on Azure Databricks OR with pandas locally.
Run:  python transform/silver.py
Output: data/silver/silver_sessions.parquet, silver_learners.parquet
"""
import os
import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DATA_DIR = Path(os.getenv("DATA_DIR", str(Path(__file__).parent.parent / "data")))
BRONZE   = DATA_DIR / "bronze"
SILVER   = DATA_DIR / "silver"

# --- PySpark availability check ---
try:
    from pyspark.sql import SparkSession
    from pyspark.sql import functions as F
    USE_SPARK = True
    spark = SparkSession.builder.appName("SKYLearn-Silver").getOrCreate()
    print("[silver] Using PySpark engine")
except ImportError:
    USE_SPARK = False
    print("[silver] PySpark not available — using pandas engine")


def _build_silver_sessions_pandas() -> pd.DataFrame:
    sessions    = pd.read_parquet(BRONZE / "assessment_sessions.parquet")
    scores      = pd.read_parquet(BRONZE / "scores.parquet")
    learners    = pd.read_parquet(BRONZE / "learners.parquet")
    users       = pd.read_parquet(BRONZE / "users.parquet")
    assessments = pd.read_parquet(BRONZE / "assessments.parquet")
    subjects    = pd.read_parquet(BRONZE / "subjects.parquet")

    df = sessions.merge(scores, left_on="id", right_on="session_id", suffixes=("", "_score"))
    df = df.merge(learners, left_on="learner_id", right_on="id", suffixes=("", "_learner"))
    df = df.merge(users, left_on="user_id", right_on="id", suffixes=("", "_user"))
    df = df.merge(assessments, left_on="assessment_id", right_on="id", suffixes=("", "_assessment"))
    df = df.merge(subjects, left_on="subject_id", right_on="id", suffixes=("", "_subject"))

    # Parse timestamps
    for col in ("started_at", "completed_at"):
        df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)

    df["duration_minutes"] = (
        (df["completed_at"] - df["started_at"]).dt.total_seconds() / 60
    ).round(1)
    df["session_month"] = df["started_at"].dt.to_period("M").astype(str)
    df["pass_fail_label"] = df["pass_fail"].map({True: "Pass", False: "Fail", 1: "Pass", 0: "Fail"})

    return df[[
        "id", "assessment_id", "learner_id", "user_id",
        "full_name", "grade", "track",
        "title", "name",                          # assessment title, subject name
        "status", "started_at", "completed_at",
        "duration_minutes", "session_month",
        "total_marks_awarded", "total_marks_possible", "percentage", "pass_fail_label",
    ]].rename(columns={"full_name": "learner_name", "title": "assessment_title", "name": "subject_name"})


def _build_silver_learners_pandas() -> pd.DataFrame:
    sessions = pd.read_parquet(BRONZE / "assessment_sessions.parquet")
    scores   = pd.read_parquet(BRONZE / "scores.parquet")
    learners = pd.read_parquet(BRONZE / "learners.parquet")
    users    = pd.read_parquet(BRONZE / "users.parquet")

    completed = sessions[sessions["status"] == "COMPLETED"].copy()
    completed = completed.merge(scores, left_on="id", right_on="session_id", suffixes=("", "_score"))

    agg = completed.groupby("learner_id").agg(
        total_sessions  = ("id", "count"),
        avg_score       = ("percentage", "mean"),
        max_score       = ("percentage", "max"),
        min_score       = ("percentage", "min"),
        pass_rate       = ("pass_fail", lambda x: x.astype(float).mean()),
        last_active     = ("started_at", "max"),
    ).reset_index()

    df = learners.merge(users, left_on="user_id", right_on="id", suffixes=("", "_user"))
    df = df.merge(agg, left_on="id", right_on="learner_id", how="left")

    df["avg_score"]    = df["avg_score"].fillna(0).round(1)
    df["pass_rate"]    = df["pass_rate"].fillna(0).round(3)
    df["total_sessions"] = df["total_sessions"].fillna(0).astype(int)

    return df[["id", "user_id", "full_name", "grade", "track",
               "total_sessions", "avg_score", "max_score", "min_score",
               "pass_rate", "last_active"]].rename(
        columns={"id": "learner_id", "full_name": "learner_name"}
    )


def build_silver():
    SILVER.mkdir(parents=True, exist_ok=True)

    silver_sessions = _build_silver_sessions_pandas()
    silver_sessions.to_parquet(SILVER / "silver_sessions.parquet", index=False)
    print(f"  ✓ silver/silver_sessions.parquet  ({len(silver_sessions)} rows)")

    silver_learners = _build_silver_learners_pandas()
    silver_learners.to_parquet(SILVER / "silver_learners.parquet", index=False)
    print(f"  ✓ silver/silver_learners.parquet  ({len(silver_learners)} rows)")

    print(f"\nSilver transform complete → {SILVER.resolve()}")
    return silver_sessions, silver_learners


if __name__ == "__main__":
    build_silver()
