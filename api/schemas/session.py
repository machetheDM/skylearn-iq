from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.session import SessionStatus, FeedbackSource


class AnswerIn(BaseModel):
    question_id: int
    selected_option_id: Optional[int] = None
    text_answer: Optional[str] = None


class SubmitSessionIn(BaseModel):
    answers: List[AnswerIn]


class AnswerOut(BaseModel):
    id: int
    question_id: int
    selected_option_id: Optional[int]
    text_answer: Optional[str]
    is_correct: Optional[bool]
    marks_awarded: float
    auto_marked: bool
    model_config = {"from_attributes": True}


class ScoreOut(BaseModel):
    total_marks_awarded: float
    total_marks_possible: int
    percentage: float
    pass_fail: Optional[bool]
    model_config = {"from_attributes": True}


class FeedbackOut(BaseModel):
    id: int
    generated_by: FeedbackSource
    content: str
    strength_areas: Optional[str]
    weakness_areas: Optional[str]
    recommendations: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: int
    assessment_id: int
    learner_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    status: SessionStatus
    answers: List[AnswerOut] = []
    score: Optional[ScoreOut] = None
    feedbacks: List[FeedbackOut] = []
    model_config = {"from_attributes": True}


class SessionStartOut(BaseModel):
    session_id: int
    assessment_id: int
    started_at: datetime
    model_config = {"from_attributes": True}
