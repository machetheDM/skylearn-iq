"""
SKYLearn IQ — Analytics Dashboard  (Phase 6 — Power BI substitute)
===================================================================
Purpose : Interactive Streamlit dashboard replicating the Power BI report
          from Azure Gold layer data. Reads locally from SQLite (dev) or
          from pre-built Gold Parquet files when the pipeline has run.
Port    : 8501  (run: streamlit run main.py  —  from cloud-bi/)

Data flow
  SQLite → Bronze Parquet → Silver Parquet → Gold Parquet → This Dashboard
  If Gold Parquet not found, falls back to reading SQLite directly.

See CONTEXT.md at the project root for full architecture and phase progress.
"""
import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

DB_PATH  = os.getenv("DB_PATH", "../api/skylearn_iq.db")
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
GOLD     = DATA_DIR / "gold"

# ── Streamlit page config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="SKYLearn IQ Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

SKYLEARN_GREEN = "#15803D"
RISK_RED       = "#DC2626"
BLUE           = "#2563EB"


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data() -> dict[str, pd.DataFrame]:
    """Load Gold Parquet if available, else build on-the-fly from SQLite."""
    gold_files = {
        "subject":   "gold_subject_performance.parquet",
        "cohorts":   "gold_learner_cohorts.parquet",
        "trends":    "gold_monthly_trends.parquet",
        "assess":    "gold_assessment_stats.parquet",
    }

    if all((GOLD / f).exists() for f in gold_files.values()):
        return {k: pd.read_parquet(GOLD / v) for k, v in gold_files.items()}

    # Fallback: build from SQLite directly
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
        with engine.connect() as conn:
            sessions = pd.read_sql(text("""
                SELECT s.id, s.learner_id, s.assessment_id, s.status,
                       s.started_at, s.completed_at,
                       u.full_name AS learner_name, l.grade, l.track,
                       a.title AS assessment_title,
                       sub.name AS subject_name,
                       sc.percentage, sc.pass_fail,
                       sc.total_marks_awarded, sc.total_marks_possible
                FROM assessment_sessions s
                JOIN learners l      ON l.id  = s.learner_id
                JOIN users u         ON u.id  = l.user_id
                JOIN assessments a   ON a.id  = s.assessment_id
                JOIN subjects sub    ON sub.id = a.subject_id
                LEFT JOIN scores sc  ON sc.session_id = s.id
            """), conn)

            learners = pd.read_sql(text("""
                SELECT l.id AS learner_id, u.full_name AS learner_name,
                       l.grade, l.track, l.enrolled_at
                FROM learners l
                JOIN users u ON u.id = l.user_id
            """), conn)

        completed = sessions[sessions["status"] == "COMPLETED"].copy()
        completed["pass_fail"] = completed["pass_fail"].map(
            {True: "Pass", False: "Fail", 1: "Pass", 0: "Fail", None: "Fail"}
        )

        # Gold Subject Performance
        subject = (completed.groupby("subject_name")
                   .agg(total_sessions=("id","count"),
                        avg_score=("percentage","mean"),
                        pass_rate=("pass_fail", lambda x: (x=="Pass").mean()),
                        unique_learners=("learner_id","nunique"))
                   .reset_index())
        subject["avg_score"] = subject["avg_score"].round(1)
        subject["pass_rate"] = (subject["pass_rate"] * 100).round(1)
        subject["difficulty"] = pd.cut(subject["avg_score"],
                                       bins=[0,40,60,80,100],
                                       labels=["Hard","Moderate","Easy","Very Easy"])

        # Gold Learner Cohorts
        agg = (completed.groupby("learner_id")
               .agg(total_sessions=("id","count"),
                    avg_score=("percentage","mean"),
                    pass_rate=("pass_fail", lambda x: (x=="Pass").mean()))
               .reset_index())
        cohorts = learners.merge(agg, on="learner_id", how="left").fillna(0)
        cohorts["avg_score"] = cohorts["avg_score"].round(1)
        cohorts["pass_rate"] = cohorts["pass_rate"].round(3)
        cohorts["risk_flag"] = cohorts.apply(
            lambda r: "At Risk" if r["avg_score"] < 45 or r["pass_rate"] < 0.4 else "On Track", axis=1)
        cohorts["performance_band"] = pd.cut(cohorts["avg_score"],
                                             bins=[0,40,60,75,100],
                                             labels=["Below Pass","Pass","Merit","Distinction"])

        # Gold Monthly Trends
        completed["session_month"] = pd.to_datetime(
            completed["started_at"], errors="coerce", utc=True
        ).dt.to_period("M").astype(str)
        trends = (completed.groupby("session_month")
                  .agg(session_count=("id","count"),
                       avg_score=("percentage","mean"),
                       pass_rate=("pass_fail", lambda x: (x=="Pass").mean()),
                       learners_active=("learner_id","nunique"))
                  .reset_index().sort_values("session_month"))
        trends["avg_score"] = trends["avg_score"].round(1)
        trends["pass_rate"] = (trends["pass_rate"] * 100).round(1)

        # Gold Assessment Stats
        assess = (completed.groupby(["assessment_id","assessment_title","subject_name"])
                  .agg(total_attempts=("id","count"),
                       avg_score=("percentage","mean"),
                       pass_rate=("pass_fail", lambda x: (x=="Pass").mean()))
                  .reset_index())
        assess["avg_score"] = assess["avg_score"].round(1)
        assess["pass_rate"] = (assess["pass_rate"] * 100).round(1)

        return {"subject": subject, "cohorts": cohorts, "trends": trends, "assess": assess}

    except Exception as e:
        st.error(f"Could not load data: {e}")
        return {}


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/15803D/ffffff?text=SKYLearn+IQ",
             use_container_width=True)
    st.markdown("### 🧠 Analytics Dashboard")
    st.caption("SKYLearn-Innovation NPO")
    st.divider()

    page = st.radio("Navigate", [
        "📊 Overview",
        "📚 Subject Performance",
        "👥 Learner Cohorts",
        "📈 Trends",
        "📝 Assessments",
    ])
    st.divider()
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.caption("Data from: SQLite → Bronze → Silver → Gold")

# ── Load data ─────────────────────────────────────────────────────────────────
data = load_data()
if not data:
    st.warning("No data available. Ensure the backend is running: `cd api && python seed.py`")
    st.stop()

subject_df = data.get("subject", pd.DataFrame())
cohorts_df = data.get("cohorts", pd.DataFrame())
trends_df  = data.get("trends",  pd.DataFrame())
assess_df  = data.get("assess",  pd.DataFrame())

# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1: Overview
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊 Overview":
    st.title("📊 Platform Overview")
    st.caption("Key performance indicators across all learners and assessments")

    # KPI cards
    total    = len(cohorts_df)
    at_risk  = int((cohorts_df["risk_flag"] == "At Risk").sum()) if not cohorts_df.empty else 0
    avg_sc   = round(cohorts_df["avg_score"].mean(), 1) if not cohorts_df.empty else 0
    pass_rt  = round(cohorts_df["pass_rate"].mean() * 100, 1) if not cohorts_df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Learners",  total)
    c2.metric("At Risk",         f"{at_risk} / {total}",
              delta=f"{round(at_risk/total*100,1) if total else 0}% of cohort",
              delta_color="inverse")
    c3.metric("Avg Score",       f"{avg_sc}%")
    c4.metric("Pass Rate",       f"{pass_rt}%",
              delta_color="normal")

    st.divider()
    col_l, col_r = st.columns(2)

    # Performance band donut
    if not cohorts_df.empty:
        band_counts = cohorts_df["performance_band"].value_counts().reset_index()
        band_counts.columns = ["band", "count"]
        fig_donut = px.pie(band_counts, names="band", values="count",
                           hole=0.55, title="Learner Performance Bands",
                           color_discrete_sequence=px.colors.sequential.Greens_r)
        fig_donut.update_layout(margin=dict(t=40, b=0, l=0, r=0))
        col_l.plotly_chart(fig_donut, use_container_width=True)

    # Risk flag bar
    if not cohorts_df.empty:
        risk_counts = cohorts_df["risk_flag"].value_counts().reset_index()
        risk_counts.columns = ["flag", "count"]
        colours = {"At Risk": RISK_RED, "On Track": SKYLEARN_GREEN}
        fig_risk = px.bar(risk_counts, x="flag", y="count",
                          color="flag", color_discrete_map=colours,
                          title="At-Risk vs On Track",
                          text_auto=True)
        fig_risk.update_layout(showlegend=False, margin=dict(t=40, b=0))
        col_r.plotly_chart(fig_risk, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2: Subject Performance
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📚 Subject Performance":
    st.title("📚 Subject Performance")

    if subject_df.empty:
        st.info("No completed sessions yet.")
    else:
        col_l, col_r = st.columns(2)

        fig_bar = px.bar(
            subject_df.sort_values("avg_score"),
            x="avg_score", y="subject_name", orientation="h",
            color="avg_score",
            color_continuous_scale=["#DC2626", "#F59E0B", "#15803D"],
            range_color=[0, 100],
            title="Average Score by Subject",
            text_auto=".1f",
            labels={"avg_score": "Avg Score (%)", "subject_name": "Subject"},
        )
        fig_bar.add_vline(x=40, line_dash="dot", line_color="#94A3B8",
                          annotation_text="Pass threshold")
        fig_bar.update_layout(coloraxis_showscale=False, margin=dict(t=40, b=0))
        col_l.plotly_chart(fig_bar, use_container_width=True)

        fig_pr = px.bar(
            subject_df.sort_values("pass_rate"),
            x="pass_rate", y="subject_name", orientation="h",
            color="pass_rate",
            color_continuous_scale=["#DC2626", "#F59E0B", "#15803D"],
            range_color=[0, 100],
            title="Pass Rate by Subject (%)",
            text_auto=".1f",
            labels={"pass_rate": "Pass Rate (%)", "subject_name": "Subject"},
        )
        fig_pr.add_vline(x=50, line_dash="dot", line_color="#94A3B8")
        fig_pr.update_layout(coloraxis_showscale=False, margin=dict(t=40, b=0))
        col_r.plotly_chart(fig_pr, use_container_width=True)

        st.dataframe(
            subject_df[["subject_name","avg_score","pass_rate","total_sessions",
                         "unique_learners","difficulty"]]
            .sort_values("avg_score", ascending=False)
            .rename(columns={
                "subject_name":   "Subject",
                "avg_score":      "Avg Score (%)",
                "pass_rate":      "Pass Rate (%)",
                "total_sessions": "Sessions",
                "unique_learners":"Learners",
                "difficulty":     "Difficulty",
            }),
            use_container_width=True, hide_index=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3: Learner Cohorts
# ─────────────────────────────────────────────────────────────────────────────
elif page == "👥 Learner Cohorts":
    st.title("👥 Learner Cohorts")

    if cohorts_df.empty:
        st.info("No learner data.")
    else:
        col_l, col_r = st.columns(2)

        # Scatter: sessions vs avg score, colour = risk flag
        fig_scatter = px.scatter(
            cohorts_df,
            x="total_sessions", y="avg_score",
            color="risk_flag",
            color_discrete_map={"At Risk": RISK_RED, "On Track": SKYLEARN_GREEN},
            hover_name="learner_name",
            hover_data={"grade": True, "track": True, "pass_rate": ":.2f"},
            title="Learner Performance Map",
            labels={"total_sessions": "Total Sessions", "avg_score": "Avg Score (%)"},
            size_max=18,
        )
        fig_scatter.add_hline(y=40, line_dash="dot", line_color="#94A3B8",
                              annotation_text="Pass threshold")
        fig_scatter.update_layout(margin=dict(t=40, b=0))
        col_l.plotly_chart(fig_scatter, use_container_width=True)

        # Bar: avg score per learner
        fig_lbar = px.bar(
            cohorts_df.sort_values("avg_score"),
            x="avg_score", y="learner_name", orientation="h",
            color="risk_flag",
            color_discrete_map={"At Risk": RISK_RED, "On Track": SKYLEARN_GREEN},
            title="Score by Learner",
            text_auto=".1f",
            labels={"avg_score": "Avg Score (%)", "learner_name": "Learner"},
        )
        fig_lbar.add_vline(x=40, line_dash="dot", line_color="#94A3B8")
        fig_lbar.update_layout(showlegend=False, margin=dict(t=40, b=0))
        col_r.plotly_chart(fig_lbar, use_container_width=True)

        st.subheader("At-Risk Learners")
        at_risk_df = cohorts_df[cohorts_df["risk_flag"] == "At Risk"]
        if at_risk_df.empty:
            st.success("✅ No learners currently at risk.")
        else:
            st.dataframe(
                at_risk_df[["learner_name","grade","track","total_sessions",
                             "avg_score","pass_rate"]]
                .sort_values("avg_score")
                .rename(columns={
                    "learner_name":   "Learner",
                    "grade":          "Grade",
                    "track":          "Track",
                    "total_sessions": "Sessions",
                    "avg_score":      "Avg Score (%)",
                    "pass_rate":      "Pass Rate",
                }),
                use_container_width=True, hide_index=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4: Trends
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📈 Trends":
    st.title("📈 Monthly Trends")

    if trends_df.empty:
        st.info("No time-series data yet. Complete some assessments first.")
    else:
        col_l, col_r = st.columns(2)

        fig_score = px.line(
            trends_df, x="session_month", y="avg_score",
            markers=True, title="Average Score Over Time",
            labels={"session_month": "Month", "avg_score": "Avg Score (%)"},
            color_discrete_sequence=[SKYLEARN_GREEN],
        )
        fig_score.add_hline(y=40, line_dash="dot", line_color=RISK_RED,
                            annotation_text="Pass threshold")
        fig_score.update_layout(margin=dict(t=40, b=0))
        col_l.plotly_chart(fig_score, use_container_width=True)

        fig_vol = px.area(
            trends_df, x="session_month", y="session_count",
            title="Session Volume per Month",
            labels={"session_month": "Month", "session_count": "Sessions"},
            color_discrete_sequence=[BLUE],
        )
        fig_vol.update_layout(margin=dict(t=40, b=0))
        col_r.plotly_chart(fig_vol, use_container_width=True)

        fig_pr = px.bar(
            trends_df, x="session_month", y="pass_rate",
            title="Pass Rate per Month (%)",
            labels={"session_month": "Month", "pass_rate": "Pass Rate (%)"},
            color="pass_rate",
            color_continuous_scale=["#DC2626", "#F59E0B", "#15803D"],
            range_color=[0, 100],
            text_auto=".1f",
        )
        fig_pr.add_hline(y=50, line_dash="dot", line_color="#94A3B8")
        fig_pr.update_layout(coloraxis_showscale=False, margin=dict(t=40, b=0))
        st.plotly_chart(fig_pr, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 5: Assessments
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📝 Assessments":
    st.title("📝 Assessment Statistics")

    if assess_df.empty:
        st.info("No completed assessment sessions yet.")
    else:
        fig_a = px.scatter(
            assess_df,
            x="total_attempts", y="avg_score",
            size="total_attempts",
            color="pass_rate",
            color_continuous_scale=["#DC2626", "#F59E0B", "#15803D"],
            range_color=[0, 100],
            hover_name="assessment_title",
            hover_data={"subject_name": True, "pass_rate": ":.1f"},
            title="Assessment Difficulty Map  (size = attempts)",
            labels={"total_attempts": "Attempts", "avg_score": "Avg Score (%)"},
        )
        fig_a.add_hline(y=40, line_dash="dot", line_color="#94A3B8")
        st.plotly_chart(fig_a, use_container_width=True)

        st.dataframe(
            assess_df[["assessment_title","subject_name","total_attempts",
                        "avg_score","pass_rate"]]
            .sort_values("avg_score", ascending=False)
            .rename(columns={
                "assessment_title": "Assessment",
                "subject_name":     "Subject",
                "total_attempts":   "Attempts",
                "avg_score":        "Avg Score (%)",
                "pass_rate":        "Pass Rate (%)",
            }),
            use_container_width=True, hide_index=True,
        )
