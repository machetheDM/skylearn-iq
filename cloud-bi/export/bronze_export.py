"""
Bronze Layer — Raw Extract  (Step 1 of Medallion Architecture)
==============================================================
Reads directly from the SQLite source database and writes raw Parquet files
one-to-one with each source table. No transforms — just format conversion.

Run:  python export/bronze_export.py
Output: data/bronze/<table_name>.parquet
"""
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

_raw     = os.getenv("DB_PATH", "../api/skylearn_iq.db")
DB_PATH  = str((Path(__file__).parent.parent / _raw).resolve())
DATA_DIR = Path(os.getenv("DATA_DIR", str(Path(__file__).parent.parent / "data")))
BRONZE   = DATA_DIR / "bronze"


QUERIES = {
    "users": "SELECT id, full_name, phone, role, created_at FROM users",
    "learners": """
        SELECT l.id, l.user_id, l.grade, l.track, l.date_of_birth
        FROM learners l
    """,
    "subjects": "SELECT id, name, code, description FROM subjects",
    "assessments": """
        SELECT id, title, subject_id, tutor_id, total_marks, is_published, created_at
        FROM assessments
    """,
    "assessment_sessions": """
        SELECT id, assessment_id, learner_id, status, started_at, completed_at
        FROM assessment_sessions
    """,
    "answers": """
        SELECT id, session_id, question_id, selected_option_id,
               text_answer, is_correct, marks_awarded, auto_marked
        FROM answers
    """,
    "scores": """
        SELECT id, session_id, total_marks_awarded, total_marks_possible,
               percentage, pass_fail
        FROM scores
    """,
    "feedbacks": """
        SELECT id, session_id, generated_by, content,
               strength_areas, weakness_areas, recommendations, created_at
        FROM feedbacks
    """,
}


def export_bronze():
    engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
    BRONZE.mkdir(parents=True, exist_ok=True)

    for table, query in QUERIES.items():
        try:
            df = pd.read_sql(text(query), engine.connect())
            out = BRONZE / f"{table}.parquet"
            df.to_parquet(out, index=False)
            print(f"  ✓ bronze/{table}.parquet  ({len(df)} rows)")
        except Exception as e:
            print(f"  ✗ {table}: {e}", file=sys.stderr)

    print(f"\nBronze export complete → {BRONZE.resolve()}")


if __name__ == "__main__":
    export_bronze()
