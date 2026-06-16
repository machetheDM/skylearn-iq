import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from preprocess import FEATURE_COLS

_scaler: StandardScaler | None = None
_kmeans: KMeans | None = None

CLUSTER_LABELS = {
    0: "High Performers",
    1: "Average Performers",
    2: "Struggling Learners",
}

K = 3


def _generate_synthetic(n: int = 1200) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    high = pd.DataFrame({
        "avg_score": rng.normal(75, 8, n // 3).clip(0, 100),
        "pass_rate": rng.beta(8, 1, n // 3),
        "completion_rate": rng.beta(9, 1, n // 3),
        "total_sessions": rng.integers(8, 20, n // 3),
        "days_since_last": rng.exponential(10, n // 3).clip(0, 999),
    })
    avg = pd.DataFrame({
        "avg_score": rng.normal(55, 10, n // 3).clip(0, 100),
        "pass_rate": rng.beta(3, 2, n // 3),
        "completion_rate": rng.beta(5, 2, n // 3),
        "total_sessions": rng.integers(3, 12, n // 3),
        "days_since_last": rng.exponential(25, n // 3).clip(0, 999),
    })
    low = pd.DataFrame({
        "avg_score": rng.normal(30, 12, n // 3).clip(0, 100),
        "pass_rate": rng.beta(1.5, 4, n // 3),
        "completion_rate": rng.beta(2, 4, n // 3),
        "total_sessions": rng.integers(1, 6, n // 3),
        "days_since_last": rng.exponential(60, n // 3).clip(0, 999),
    })
    return pd.concat([high, avg, low], ignore_index=True).sample(frac=1, random_state=7)


def get_models():
    global _scaler, _kmeans
    if _scaler is None or _kmeans is None:
        df = _generate_synthetic()
        X = df[FEATURE_COLS]
        _scaler = StandardScaler().fit(X)
        X_scaled = _scaler.transform(X)
        _kmeans = KMeans(n_clusters=K, random_state=42, n_init=20)
        _kmeans.fit(X_scaled)
        # Re-label clusters by centroid avg_score descending
        centres = _kmeans.cluster_centers_
        order = (-_scaler.inverse_transform(centres)[:, 0]).argsort()
        _label_map = {int(order[i]): i for i in range(K)}
        _kmeans._label_map = _label_map
    return _scaler, _kmeans


def predict(df: pd.DataFrame) -> pd.DataFrame:
    scaler, kmeans = get_models()
    X = df[FEATURE_COLS].copy()
    X_scaled = scaler.transform(X)
    raw_labels = kmeans.predict(X_scaled)
    df = df.copy()
    label_map = getattr(kmeans, "_label_map", {i: i for i in range(K)})
    df["cluster_id"]    = [label_map.get(int(l), int(l)) for l in raw_labels]
    df["cluster_label"] = df["cluster_id"].map(CLUSTER_LABELS)
    return df
