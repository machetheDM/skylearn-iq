from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from database import get_db
from models.user import User, Learner
from models.assessment import Assessment, Question, Option, QuestionType
from models.session import AssessmentSession, Answer, Score, Feedback, SessionStatus, FeedbackSource
from schemas.session import SubmitSessionIn, SessionOut, SessionStartOut, ScoreOut
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
