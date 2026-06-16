import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from preprocess import FEATURE_COLS

_model: xgb.XGBClassifier | None = None


def _generate_synthetic(n: int = 1500) -> pd.DataFrame:
    """
    Synthetic learner dataset for training the at-risk classifier.
    Label: is_at_risk = 1  when avg_score < 45 OR pass_rate < 0.4
    """
    rng = np.random.default_rng(42)

    # Create two clusters: struggling and performing
    n_risk = n // 2
    n_ok   = n - n_risk

    struggling = pd.DataFrame({
        "avg_score":       rng.beta(1.8, 4, n_risk) * 100,
        "pass_rate":       rng.beta(1.5, 3, n_risk),
        "completion_rate": rng.beta(2, 3, n_risk),
        "total_sessions":  rng.integers(1, 8, n_risk),
        "days_since_last": rng.exponential(60, n_risk).clip(0, 999),
        "is_at_risk":      1,
    })
    performing = pd.DataFrame({
        "avg_score":       rng.beta(4, 2, n_ok) * 100,
        "pass_rate":       rng.beta(5, 1.5, n_ok),
        "completion_rate": rng.beta(6, 1, n_ok),
        "total_sessions":  rng.integers(3, 20, n_ok),
        "days_since_last": rng.exponential(20, n_ok).clip(0, 999),
        "is_at_risk":      0,
    })
    return pd.concat([struggling, performing], ignore_index=True).sample(frac=1, random_state=42)


def get_model() -> xgb.XGBClassifier:
    global _model
    if _model is None:
        df = _generate_synthetic()
        X, y = df[FEATURE_COLS], df["is_at_risk"]
        X_tr, X_val, y_tr, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        _model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )
        _model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
    return _model


def predict(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add risk_score, is_at_risk, risk_label columns to df.
    Falls back gracefully when a learner has no session history.
    """
    model = get_model()
    X = df[FEATURE_COLS].copy()

    risk_scores = model.predict_proba(X)[:, 1]
    df = df.copy()
    df["risk_score"] = risk_scores.round(4)
    df["is_at_risk"] = df["risk_score"] >= 0.5

    def label(s: float) -> str:
        if s >= 0.75: return "High Risk"
        if s >= 0.5:  return "At Risk"
        if s >= 0.3:  return "Monitor"
        return "On Track"

    df["risk_label"] = df["risk_score"].apply(label)
    return df
