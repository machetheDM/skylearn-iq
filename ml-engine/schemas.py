from pydantic import BaseModel
from typing import Optional


class LearnerFeatures(BaseModel):
    learner_id: int
    user_id: int
    full_name: str
    avg_score: float
    pass_rate: float
    completion_rate: float
    total_sessions: int
    days_since_last: float


class AtRiskResult(LearnerFeatures):
    risk_score: float
    is_at_risk: bool
    risk_label: str


class ClusterResult(LearnerFeatures):
    cluster_id: int
    cluster_label: str


class ShapFeature(BaseModel):
    feature: str
    value: float
    shap_value: float
    impact: str


class ShapExplanation(BaseModel):
    learner_id: int
    full_name: str
    risk_score: float
    is_at_risk: bool
    features: list[ShapFeature]
    summary: str


class ForecastPoint(BaseModel):
    period: int
    predicted_score: float
    lower_bound: float
    upper_bound: float


class ForecastResult(BaseModel):
    learner_id: int
    full_name: str
    historical_scores: list[float]
    forecast: list[ForecastPoint]
    trend: str
    message: str


class AnalyticsSummary(BaseModel):
    total_learners: int
    at_risk_count: int
    avg_score_overall: float
    cluster_distribution: dict[str, int]
    trend_direction: str
