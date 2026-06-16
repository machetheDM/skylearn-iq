"""
Gold Layer — Analytical Aggregates  (Step 3 of Medallion Architecture)
=======================================================================
Reads Silver Parquet and produces Power BI-ready aggregate tables.

Tables produced:
  gold_subject_performance  — avg score, pass rate, session count per subject
  gold_learner_cohorts      — per-learner KPIs (ready for scatter/rank charts)
  gold_monthly_trends       — monthly session volume + avg score over time
  gold_assessment_stats     — per-assessment difficulty + completion metrics
  gold_at_risk_flags        — learners flagged at-risk with threshold reasoning

Run:  python transform/gold.py
Output: data/gold/*.parquet
"""
import os
import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DATA_DIR = Path(os.getenv("DATA_DIR", str(Path(__file__).parent.parent / "data")))
SILVER   = DATA_DIR / "silver"
GOLD     = DATA_DIR / "gold"


def build_gold():
    GOLD.mkdir(parents=True, exist_ok=True)

    sessions = pd.read_parquet(SILVER / "silver_sessions.parquet")
    learners = pd.read_parquet(SILVER / "silver_learners.parquet")

    # ── gold_subject_performance ─────────────────────────────────────────────
    subj = (
        sessions[sessions["status"] == "COMPLETED"]
        .groupby("subject_name")
        .agg(
            total_sessions  = ("id",         "count"),
            avg_score       = ("percentage", "mean"),
            pass_rate       = ("pass_fail_label", lambda x: (x == "Pass").mean()),
            unique_learners = ("learner_id", "nunique"),
        )
        .reset_index()
    )
    subj["avg_score"]  = subj["avg_score"].round(1)
    subj["pass_rate"]  = (subj["pass_rate"] * 100).round(1)
    subj["difficulty"] = pd.cut(subj["avg_score"],
                                bins=[0, 40, 60, 80, 100],
                                labels=["Hard", "Moderate", "Easy", "Very Easy"])
    subj.to_parquet(GOLD / "gold_subject_performance.parquet", index=False)
    print(f"  ✓ gold_subject_performance.parquet  ({len(subj)} rows)")

    # ── gold_learner_cohorts ─────────────────────────────────────────────────
    cohorts = learners.copy()
    cohorts["risk_flag"] = (
        (cohorts["avg_score"] < 45) | (cohorts["pass_rate"] < 0.4)
    ).map({True: "At Risk", False: "On Track"})

    cohorts["performance_band"] = pd.cut(
        cohorts["avg_score"],
        bins=[0, 40, 60, 75, 100],
        labels=["Below Pass", "Pass", "Merit", "Distinction"]
    )
    cohorts.to_parquet(GOLD / "gold_learner_cohorts.parquet", index=False)
    print(f"  ✓ gold_learner_cohorts.parquet  ({len(cohorts)} rows)")

    # ── gold_monthly_trends ──────────────────────────────────────────────────
    completed = sessions[sessions["status"] == "COMPLETED"].copy()
    completed["session_month"] = pd.to_datetime(
        completed["session_month"], format="%Y-%m", errors="coerce"
    )
    monthly = (
        completed.groupby("session_month")
        .agg(
            session_count  = ("id",         "count"),
            avg_score      = ("percentage", "mean"),
            pass_rate      = ("pass_fail_label", lambda x: (x == "Pass").mean()),
            learners_active = ("learner_id", "nunique"),
        )
        .reset_index()
        .sort_values("session_month")
    )
    monthly["avg_score"] = monthly["avg_score"].round(1)
    monthly["pass_rate"] = (monthly["pass_rate"] * 100).round(1)
    monthly.to_parquet(GOLD / "gold_monthly_trends.parquet", index=False)
    print(f"  ✓ gold_monthly_trends.parquet  ({len(monthly)} rows)")

    # ── gold_assessment_stats ────────────────────────────────────────────────
    assess = (
        completed.groupby(["assessment_id", "assessment_title", "subject_name"])
        .agg(
            total_attempts  = ("id",         "count"),
            avg_score       = ("percentage", "mean"),
            pass_rate       = ("pass_fail_label", lambda x: (x == "Pass").mean()),
            avg_duration    = ("duration_minutes", "mean"),
        )
        .reset_index()
    )
    assess["avg_score"]    = assess["avg_score"].round(1)
    assess["pass_rate"]    = (assess["pass_rate"] * 100).round(1)
    assess["avg_duration"] = assess["avg_duration"].round(1)
    assess.to_parquet(GOLD / "gold_assessment_stats.parquet", index=False)
    print(f"  ✓ gold_assessment_stats.parquet  ({len(assess)} rows)")

    print(f"\nGold transform complete → {GOLD.resolve()}")


if __name__ == "__main__":
    build_gold()
