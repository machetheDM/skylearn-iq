import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_PATH = os.getenv("DB_PATH", "../api/skylearn_iq.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fetch_session_context(db, session_id: int) -> dict | None:
    """
    Pull everything needed to generate feedback for a given session:
    learner name, assessment title, subject, each question + the learner's answer + correct answer + marks.
    """
    row = db.execute(text("""
        SELECT
            u.full_name          AS learner_name,
            a.title              AS assessment_title,
            s.name               AS subject_name,
            sc.total_marks_awarded,
            sc.total_marks_possible,
            sc.percentage
        FROM assessment_sessions ases
        JOIN learners l      ON l.id  = ases.learner_id
        JOIN users u         ON u.id  = l.user_id
        JOIN assessments a   ON a.id  = ases.assessment_id
        JOIN subjects s      ON s.id  = a.subject_id
        LEFT JOIN scores sc  ON sc.session_id = ases.id
        WHERE ases.id = :sid
    """), {"sid": session_id}).fetchone()

    if not row:
        return None

    answers = db.execute(text("""
        SELECT
            q.text              AS question_text,
            q.question_type,
            q.marks,
            ans.text_answer,
            ans.selected_option_id,
            ans.marks_awarded,
            ans.is_correct,
            (SELECT o.text FROM options o WHERE o.id = q.correct_option_id) AS correct_answer
        FROM answers ans
        JOIN questions q ON q.id = ans.question_id
        WHERE ans.session_id = :sid
        ORDER BY q.order_index
    """), {"sid": session_id}).fetchall()

    qa_lines = []
    for a in answers:
        qa_lines.append(
            f"Q: {a.question_text}\n"
            f"  Learner answered: {a.text_answer or a.selected_option_id}\n"
            f"  Correct answer:   {a.correct_answer or 'N/A (short-answer)'}\n"
            f"  Marks: {a.marks_awarded}/{a.marks}  |  Correct: {bool(a.is_correct)}"
        )

    return {
        "learner_name":      row.learner_name,
        "assessment_title":  row.assessment_title,
        "subject_name":      row.subject_name,
        "score_pct":         round(float(row.percentage or 0), 1),
        "marks_awarded":     row.total_marks_awarded or 0,
        "marks_possible":    row.total_marks_possible or 0,
        "qa_detail":         "\n\n".join(qa_lines),
    }


def save_feedback(db, session_id: int, content: str,
                  strength_areas: str, weakness_areas: str,
                  recommendations: str) -> int:
    result = db.execute(text("""
        INSERT INTO feedbacks
            (session_id, generated_by, content, strength_areas, weakness_areas,
             recommendations, created_at)
        VALUES
            (:sid, 'AI', :content, :strengths, :weaknesses, :recs, datetime('now'))
        RETURNING id
    """), {
        "sid":       session_id,
        "content":   content,
        "strengths": strength_areas,
        "weaknesses": weakness_areas,
        "recs":      recommendations,
    })
    db.commit()
    return result.fetchone()[0]
