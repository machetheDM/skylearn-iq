from datetime import datetime, timezone
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

FEATURE_COLS = ["avg_score", "pass_rate", "completion_rate", "total_sessions", "days_since_last"]


def get_learner_features(db: Session) -> pd.DataFrame:
    """Extract ML features from session/score data for all learners."""
    from sqlalchemy import text

    rows_sql = text("""
        SELECT
            l.id          AS learner_id,
            l.user_id,
            u.full_name,
            COUNT(s.id)   AS total_sessions,
            SUM(CASE WHEN s.status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed,
            AVG(CASE WHEN sc.percentage IS NOT NULL THEN sc.percentage ELSE NULL END) AS avg_score,
            AVG(CASE WHEN sc.percentage >= 40 THEN 1.0 ELSE 0.0 END) AS pass_rate,
            MAX(s.started_at) AS last_session
        FROM learners l
        JOIN users u ON u.id = l.user_id
        LEFT JOIN assessment_sessions s ON s.learner_id = l.id
        LEFT JOIN scores sc ON sc.session_id = s.id
        GROUP BY l.id, l.user_id, u.full_name
    """)

    result = db.execute(rows_sql).fetchall()
    now = datetime.now(timezone.utc)

    records = []
    for r in result:
        total      = r.total_sessions or 0
        completed  = r.completed or 0
        avg_score  = float(r.avg_score or 0.0)
        pass_rate  = float(r.pass_rate or 0.0)
        comp_rate  = (completed / total) if total > 0 else 0.0

        if r.last_session:
            try:
                last_dt = datetime.fromisoformat(str(r.last_session)).replace(tzinfo=timezone.utc)
                days_since = max(0, (now - last_dt).days)
            except Exception:
                days_since = 999.0
        else:
            days_since = 999.0

        records.append({
            "learner_id":      int(r.learner_id),
            "user_id":         int(r.user_id),
            "full_name":       r.full_name,
            "avg_score":       avg_score,
            "pass_rate":       pass_rate,
            "completion_rate": comp_rate,
            "total_sessions":  total,
            "days_since_last": float(days_since),
        })

    return pd.DataFrame(records) if records else pd.DataFrame(
        columns=["learner_id", "user_id", "full_name"] + FEATURE_COLS
    )


def get_learner_score_series(db: Session, learner_id: int) -> list[float]:
    """Return chronological list of session percentage scores for a learner."""
    from sqlalchemy import text
    rows = db.execute(text("""
        SELECT sc.percentage
        FROM assessment_sessions s
        JOIN scores sc ON sc.session_id = s.id
        WHERE s.learner_id = :lid AND s.status = 'COMPLETED'
        ORDER BY s.started_at ASC
    """), {"lid": learner_id}).fetchall()
    return [float(r.percentage) for r in rows]
