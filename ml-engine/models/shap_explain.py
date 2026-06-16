import shap
import numpy as np
import pandas as pd
from models.at_risk import get_model
from preprocess import FEATURE_COLS

FEATURE_DESCRIPTIONS = {
    "avg_score":       "Average assessment score",
    "pass_rate":       "Proportion of sessions passed (≥40%)",
    "completion_rate": "Proportion of sessions completed",
    "total_sessions":  "Total assessment attempts",
    "days_since_last": "Days since last assessment",
}


def explain_learner(row: pd.Series) -> dict:
    """
    Return SHAP values for a single learner row.
    """
    model = get_model()
    X = row[FEATURE_COLS].values.reshape(1, -1)
    X_df = pd.DataFrame(X, columns=FEATURE_COLS)

    explainer   = shap.TreeExplainer(model)
    shap_vals   = explainer.shap_values(X_df)[0]  # for class 1 (at-risk)

    risk_score = float(model.predict_proba(X_df)[0, 1])

    features = []
    for feat, sv, fv in zip(FEATURE_COLS, shap_vals, X[0]):
        impact = "increases risk" if sv > 0 else "reduces risk"
        features.append({
            "feature":    feat,
            "value":      round(float(fv), 3),
            "shap_value": round(float(sv), 4),
            "impact":     impact,
        })

    # Sort by absolute SHAP value descending
    features.sort(key=lambda f: abs(f["shap_value"]), reverse=True)

    top = features[0]
    summary = (
        f"The biggest driver of {'high' if risk_score >= 0.5 else 'low'} risk "
        f"is '{FEATURE_DESCRIPTIONS.get(top['feature'], top['feature'])}' "
        f"(SHAP={top['shap_value']:+.3f})."
    )

    return {
        "risk_score": round(risk_score, 4),
        "is_at_risk": risk_score >= 0.5,
        "features":   features,
        "summary":    summary,
    }
