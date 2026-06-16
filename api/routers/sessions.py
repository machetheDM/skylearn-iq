from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from database import get_db
from models.user import User, Learner
from models.assessment import Assessment, Question, Option, QuestionType
from models.session import AssessmentSession, Answer, Score, Feedback, SessionStatus, FeedbackSource
from schemas.session import SubmitSessionIn, SessionOut, SessionStartOut, ScoreOut, TutorFeedbackIn, MarkAnswerIn, SessionSummaryOut
from core.auth import get_current_user, require_tutor

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.post("/{assessment_id}/start", response_model=SessionStartOut, status_code=201)
def start_session(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id, Assessment.is_published == True).first()
    if not a:
        raise HTTPException(404, "Assessment not found or not published")
    learner = db.query(Learner).filter(Learner.user_id == current_user.id).first()
    if not learner:
        raise HTTPException(403, "Only learners can start a session")
    existing = db.query(AssessmentSession).filter(
        AssessmentSession.assessment_id == assessment_id,
        AssessmentSession.learner_id == learner.id,
        AssessmentSession.status == SessionStatus.IN_PROGRESS,
    ).first()
    if existing:
        return SessionStartOut(session_id=existing.id, assessment_id=assessment_id, started_at=existing.started_at)
    session = AssessmentSession(assessment_id=assessment_id, learner_id=learner.id)
    db.add(session); db.commit(); db.refresh(session)
    return SessionStartOut(session_id=session.id, assessment_id=assessment_id, started_at=session.started_at)


@router.post("/{session_id}/submit", response_model=SessionOut)
def submit_session(
    session_id: int,
    body: SubmitSessionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(AssessmentSession).filter(AssessmentSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    if session.status != SessionStatus.IN_PROGRESS:
        raise HTTPException(400, "Session already completed")

    total_awarded = 0.0
    total_possible = 0

    for ans_in in body.answers:
        q = db.query(Question).filter(Question.id == ans_in.question_id).first()
        if not q:
            continue
        total_possible += q.marks
        is_correct = None
        marks_awarded = 0.0
        auto_marked = False

        if q.q_type == QuestionType.MCQ and ans_in.selected_option_id:
            opt = db.query(Option).filter(Option.id == ans_in.selected_option_id).first()
            is_correct = bool(opt and opt.is_correct)
            marks_awarded = float(q.marks) if is_correct else 0.0
            auto_marked = True

        elif q.q_type == QuestionType.SHORT_ANSWER and ans_in.text_answer and q.correct_answer:
            is_correct = ans_in.text_answer.strip().lower() == q.correct_answer.strip().lower()
            marks_awarded = float(q.marks) if is_correct else 0.0
            auto_marked = True

        total_awarded += marks_awarded
        answer = Answer(
            session_id=session.id,
            question_id=q.id,
            selected_option_id=ans_in.selected_option_id,
            text_answer=ans_in.text_answer,
            is_correct=is_correct,
            marks_awarded=marks_awarded,
            auto_marked=auto_marked,
        )
        db.add(answer)

    pct = round((total_awarded / total_possible * 100), 2) if total_possible > 0 else 0.0
    score = Score(
        session_id=session.id,
        total_marks_awarded=total_awarded,
        total_marks_possible=total_possible,
        percentage=pct,
        pass_fail=pct >= 40.0,
    )
    db.add(score)

    session.status = SessionStatus.COMPLETED
    session.completed_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(session)

    # Fire-and-forget: ask the AI Feedback service (port 8003) to generate feedback.
    # Runs in a background thread so the submit response is never delayed.
    import threading, requests as _req
    def _trigger_ai_feedback(sid: int):
        try:
            _req.post("http://localhost:8003/api/feedback/generate",
                      json={"session_id": sid}, timeout=60)
        except Exception:
            pass  # AI service may not be running; feedback can be generated manually
    threading.Thread(target=_trigger_ai_feedback, args=(session.id,), daemon=True).start()

    return session


@router.get("/{session_id}", response_model=SessionOut)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(AssessmentSession).filter(AssessmentSession.id == session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    return session


@router.get("/learner/my-sessions", response_model=List[SessionOut])
def my_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    learner = db.query(Learner).filter(Learner.user_id == current_user.id).first()
    if not learner:
        raise HTTPException(403, "Only learners can view sessions")
    return db.query(AssessmentSession).filter(AssessmentSession.learner_id == learner.id).all()


@router.get("/tutor/all-sessions", response_model=List[SessionOut])
def all_sessions_for_tutor(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tutor),
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(404, "Assessment not found")
    return db.query(AssessmentSession).filter(AssessmentSession.assessment_id == assessment_id).all()


@router.get("/tutor/sessions", response_model=List[SessionSummaryOut])
def all_sessions_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tutor),
):
    sessions = db.query(AssessmentSession).order_by(AssessmentSession.id.desc()).all()
    result = []
    for s in sessions:
        result.append(SessionSummaryOut(
            id=s.id,
            assessment_id=s.assessment_id,
            assessment_title=s.assessment.title if s.assessment else "",
            learner_id=s.learner_id,
            learner_name=s.learner.user.full_name if s.learner and s.learner.user else "",
            learner_phone=s.learner.user.phone if s.learner and s.learner.user else "",
            status=s.status,
            started_at=s.started_at,
            completed_at=s.completed_at,
            score=ScoreOut.model_validate(s.score) if s.score else None,
        ))
    return result


@router.post("/{session_id}/feedback", status_code=201)
def add_tutor_feedback(
    session_id: int,
    body: TutorFeedbackIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tutor),
):
    s = db.query(AssessmentSession).filter(AssessmentSession.id == session_id).first()
    if not s:
        raise HTTPException(404, "Session not found")
    fb = Feedback(
        session_id=session_id,
        generated_by=FeedbackSource.TUTOR,
        content=body.content,
        strength_areas=body.strength_areas,
        weakness_areas=body.weakness_areas,
        recommendations=body.recommendations,
    )
    db.add(fb); db.commit(); db.refresh(fb)
    return {"id": fb.id, "message": "Feedback saved"}


@router.patch("/{session_id}/answers/{answer_id}/mark")
def mark_answer(
    session_id: int,
    answer_id: int,
    body: MarkAnswerIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tutor),
):
    answer = db.query(Answer).filter(Answer.id == answer_id, Answer.session_id == session_id).first()
    if not answer:
        raise HTTPException(404, "Answer not found")
    answer.marks_awarded = body.marks_awarded
    answer.is_correct = body.is_correct
    answer.auto_marked = False
    all_answers = db.query(Answer).filter(Answer.session_id == session_id).all()
    total_awarded = sum(a.marks_awarded for a in all_answers)
    score = db.query(Score).filter(Score.session_id == session_id).first()
    if score:
        score.total_marks_awarded = total_awarded
        score.percentage = round((total_awarded / score.total_marks_possible * 100), 2) if score.total_marks_possible > 0 else 0.0
        score.pass_fail = score.percentage >= 40.0
    db.commit()
    return {"message": "Marked", "marks_awarded": body.marks_awarded}
