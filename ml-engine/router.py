from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from preprocess import get_learner_features, get_learner_score_series, FEATURE_COLS
from schemas import AtRiskResult, ClusterResult, ShapExplanation, ForecastResult, AnalyticsSummary
import models.at_risk    as at_risk_model
import models.clustering as cluster_model
import models.shap_explain as shap_model
import models.forecasting  as forecast_model

router = APIRouter(prefix="/api/ml", tags=["ML Analytics"])


def _require_data(df):
    if df.empty:
        raise HTTPException(404, "No learner data found. Seed the database first.")
    return df


# ── At-Risk Detection ─────────────────────────────────────────────────────────
@router.get("/at-risk", response_model=List[AtRiskResult])
def get_at_risk(db: Session = Depends(get_db)):
    """XGBoost at-risk learner prediction for all learners."""
    df = _require_data(get_learner_features(db))
    df = at_risk_model.predict(df)
    df = df.sort_values("risk_score", ascending=False)
    return df.to_dict(orient="records")


# ── K-Means Clustering ────────────────────────────────────────────────────────
@router.get("/clusters", response_model=List[ClusterResult])
def get_clusters(db: Session = Depends(get_db)):
    """K-Means (K=3) learner cluster assignment."""
    df = _require_data(get_learner_features(db))
    df = cluster_model.predict(df)
    df = df.sort_values("cluster_id")
    return df.to_dict(orient="records")


# ── SHAP Explainability ───────────────────────────────────────────────────────
@router.get("/explain/{learner_id}", response_model=ShapExplanation)
def explain_learner(learner_id: int, db: Session = Depends(get_db)):
    """SHAP feature importance explanation for a specific learner."""
    df = _require_data(get_learner_features(db))
    row = df[df["learner_id"] == learner_id]
    if row.empty:
        raise HTTPException(404, f"Learner {learner_id} not found.")
    row = row.iloc[0]
    explanation = shap_model.explain_learner(row)
    return ShapExplanation(
        learner_id=int(row["learner_id"]),
        full_name=str(row["full_name"]),
        **explanation,
    )


# ── ARIMA Forecasting ─────────────────────────────────────────────────────────
@router.get("/forecast/{learner_id}", response_model=ForecastResult)
def get_forecast(learner_id: int, steps: int = 3, db: Session = Depends(get_db)):
    """ARIMA score forecast for a specific learner (falls back to linear trend)."""
    df = get_learner_features(db)
    row = df[df["learner_id"] == learner_id]
    if row.empty:
        raise HTTPException(404, f"Learner {learner_id} not found.")
    row = row.iloc[0]

    scores = get_learner_score_series(db, learner_id)
    result = forecast_model.forecast(scores, steps=min(steps, 6))

    return ForecastResult(
        learner_id=int(row["learner_id"]),
        full_name=str(row["full_name"]),
        historical_scores=scores,
        **result,
    )


# ── Summary Analytics ─────────────────────────────────────────────────────────
@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(db: Session = Depends(get_db)):
    """High-level analytics overview: counts, avg score, cluster distribution, trend."""
    df = _require_data(get_learner_features(db))
    df_risk    = at_risk_model.predict(df.copy())
    df_cluster = cluster_model.predict(df.copy())

    cluster_dist = df_cluster["cluster_label"].value_counts().to_dict()

    # Overall trend from all learners' avg_score
    scores = df["avg_score"].tolist()
    import numpy as np
    if len(scores) > 1:
        slope = float(np.polyfit(range(len(scores)), sorted(scores), 1)[0])
        trend = "improving" if slope > 0.5 else "declining" if slope < -0.5 else "stable"
    else:
        trend = "stable"

    return AnalyticsSummary(
        total_learners=len(df),
        at_risk_count=int(df_risk["is_at_risk"].sum()),
        avg_score_overall=round(float(df["avg_score"].mean()), 1),
        cluster_distribution=cluster_dist,
        trend_direction=trend,
    )
