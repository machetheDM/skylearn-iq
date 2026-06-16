import numpy as np
from typing import Optional

MIN_OBS_ARIMA = 5


def _linear_forecast(scores: list[float], steps: int) -> list[dict]:
    """Simple linear trend extrapolation when data < MIN_OBS_ARIMA."""
    n = len(scores)
    if n == 0:
        return [{"period": i + 1, "predicted_score": 50.0, "lower_bound": 35.0, "upper_bound": 65.0}
                for i in range(steps)]

    x = np.arange(n)
    slope, intercept = np.polyfit(x, scores, 1) if n > 1 else (0, scores[-1])
    std  = float(np.std(scores)) if n > 1 else 10.0

    result = []
    for i in range(1, steps + 1):
        pred = float(np.clip(intercept + slope * (n + i - 1), 0, 100))
        result.append({
            "period":          n + i,
            "predicted_score": round(pred, 1),
            "lower_bound":     round(max(0, pred - 1.96 * std), 1),
            "upper_bound":     round(min(100, pred + 1.96 * std), 1),
        })
    return result


def _arima_forecast(scores: list[float], steps: int) -> list[dict]:
    from statsmodels.tsa.arima.model import ARIMA
    import warnings
    warnings.filterwarnings("ignore")

    n = len(scores)
    try:
        model = ARIMA(scores, order=(1, 1, 1))
        fit   = model.fit()
        pred  = fit.get_forecast(steps=steps)
        means = pred.predicted_mean
        ci    = pred.conf_int(alpha=0.05)

        result = []
        for i in range(steps):
            result.append({
                "period":          n + i + 1,
                "predicted_score": round(float(np.clip(means.iloc[i], 0, 100)), 1),
                "lower_bound":     round(float(np.clip(ci.iloc[i, 0], 0, 100)), 1),
                "upper_bound":     round(float(np.clip(ci.iloc[i, 1], 0, 100)), 1),
            })
        return result
    except Exception:
        return _linear_forecast(scores, steps)


def forecast(scores: list[float], steps: int = 3) -> dict:
    """
    Forecast next `steps` assessment scores for a learner.
    Uses ARIMA when ≥ MIN_OBS_ARIMA observations, otherwise linear trend.
    """
    if not scores:
        trend   = "no_data"
        method  = "none"
        points  = _linear_forecast([], steps)
    elif len(scores) >= MIN_OBS_ARIMA:
        points = _arima_forecast(scores, steps)
        method = "ARIMA(1,1,1)"
        recent = scores[-3:]
        slope  = np.polyfit(range(len(recent)), recent, 1)[0] if len(recent) > 1 else 0
        trend  = "improving" if slope > 1 else "declining" if slope < -1 else "stable"
    else:
        points = _linear_forecast(scores, steps)
        method = "linear_trend"
        slope  = np.polyfit(range(len(scores)), scores, 1)[0] if len(scores) > 1 else 0
        trend  = "improving" if slope > 1 else "declining" if slope < -1 else "stable"

    msg_map = {
        "improving": f"Score trend is improving. Forecasting continued growth over next {steps} sessions.",
        "declining": f"Score trend is declining. Intervention recommended before next session.",
        "stable":    f"Score trend is stable. Consistent performance over next {steps} sessions expected.",
        "no_data":   "No assessment history. Complete at least one session for forecasting.",
    }

    return {
        "forecast": points,
        "trend":    trend,
        "message":  msg_map.get(trend, ""),
        "method":   method,
    }
