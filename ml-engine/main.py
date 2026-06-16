"""
SKYLearn IQ — ML Analytics Engine  (Phase 4 — IN PROGRESS)
===========================================================
Purpose : Standalone ML microservice exposing analytics endpoints consumed by the
          Tutor Desktop App and (later) Power BI / n8n.
Port    : 8002  (run: python -m uvicorn main:app --reload --port 8002)
DB      : Reads from ../api/skylearn_iq.db  (same SQLite as the backend)
          Override with DB_PATH env var for PostgreSQL or alternative path.

Endpoints
  GET /api/ml/at-risk             — XGBoost risk scores for all learners
  GET /api/ml/clusters            — K-Means (K=3) cluster per learner
  GET /api/ml/explain/{id}        — SHAP feature-importance for one learner
  GET /api/ml/forecast/{id}       — ARIMA score forecast (falls back to linear)
  GET /api/ml/summary             — Aggregated analytics overview

ML Strategy
  Models are trained on *synthetic* learner data that mirrors realistic patterns
  (2-cluster at-risk, 3-cluster performance tiers). Synthetic training means the
  system works meaningfully even when real data is sparse (early deployment).
  Models score *real* learner features extracted live from the database.

See CONTEXT.md at the project root for full architecture and phase progress.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="SKYLearn IQ — ML Analytics Engine",
    description="XGBoost at-risk detection · K-Means clustering · SHAP explainability · ARIMA forecasting",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from router import router
app.include_router(router)


@app.get("/", tags=["Health"])
def root():
    return {"service": "SKYLearn IQ ML Engine", "version": "1.0.0", "status": "running"}


@app.get("/health", tags=["Health"])
def health():
    from models.at_risk import get_model
    model = get_model()
    return {
        "status": "ok",
        "xgboost_model": "loaded",
        "n_estimators":  model.n_estimators,
    }
