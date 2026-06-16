from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import User, Tutor
from models.assessment import Assessment, Question, Option, Subject, Topic
from schemas.assessment import (
    AssessmentIn, AssessmentOut, AssessmentPublic,
    QuestionIn, QuestionOut, SubjectOut, TopicOut,
)
from core.auth import require_tutor, get_current_user

router = APIRouter(prefix="/api", tags=["Assessments"])


@router.get("/subjects", response_model=List[SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()


@router.get("/subjects/{subject_id}/topics", response_model=List[TopicOut])
def list_topics(subject_id: int, db: Session = Depends(get_db)):
    return db.query(Topic).filter(Topic.subject_id == subject_id).all()


@router.post("/assessments", response_model=AssessmentOut, status_code=201)
def create_assessment(
    body: AssessmentIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tutor),
):
    tutor = db.query(Tutor).filter(Tutor.user_id == current_user.id).first()
    if not tutor:
        raise HTTPException(404, "Tutor profile not found")
    if not db.query(Subject).filter(Subject.id == body.subject_id).first():
        raise HTTPException(404, "Subject not found")
    a = Assessment(
        tutor_id=tutor.id,
        subject_id=body.subject_id,
        title=body.title,
        description=body.description,
        time_limit_min=body.time_limit_min,
    )
    db.add(a); db.commit(); db.refresh(a)
    return a


@router.get("/assessments", response_model=List[AssessmentOut])
def list_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tutor),
):
    tutor = db.query(Tutor).filter(Tutor.user_id == current_user.id).first()
    return db.query(Assessment).filter(Assessment.tutor_id == tutor.id).all() if tutor else []


@router.get("/assessments/published", response_model=List[AssessmentPublic])
def list_published(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Assessment).filter(Assessment.is_published == True).all()


@router.get("/assessments/{assessment_id}", response_model=AssessmentOut)
def get_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tutor),
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(404, "Assessment not found")
    return a


@router.patch("/assessments/{assessment_id}/publish", response_model=AssessmentOut)
def publish_assessment(
    assessment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tutor),
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(404, "Assessment not found")
    a.is_published = True
    db.commit(); db.refresh(a)
    return a


@router.post("/assessments/{assessment_id}/questions", response_model=QuestionOut, status_code=201)
def add_question(
    assessment_id: int,
    body: QuestionIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tutor),
):
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not a:
        raise HTTPException(404, "Assessment not found")
    q = Question(
        assessment_id=assessment_id,
        topic_id=body.topic_id,
        text=body.text,
        q_type=body.q_type,
        marks=body.marks,
        difficulty=body.difficulty,
        concept_tag=body.concept_tag,
        order_num=body.order_num,
        correct_answer=body.correct_answer,
    )
    db.add(q); db.flush()
    for opt in body.options:
        db.add(Option(question_id=q.id, text=opt.text, is_correct=opt.is_correct, order_num=opt.order_num))
    a.total_marks = sum(qq.marks for qq in a.questions) + body.marks
    db.commit(); db.refresh(q)
    return q


@router.delete("/assessments/{assessment_id}/questions/{question_id}", status_code=204)
def delete_question(
    assessment_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_tutor),
):
    q = db.query(Question).filter(Question.id == question_id, Question.assessment_id == assessment_id).first()
    if not q:
        raise HTTPException(404, "Question not found")
    a = q.assessment
    db.delete(q)
    a.total_marks = sum(qq.marks for qq in a.questions if qq.id != question_id)
    db.commit()
