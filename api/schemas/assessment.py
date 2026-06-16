from pydantic import BaseModel
from typing import Optional, List
from models.assessment import QuestionType, Difficulty


class SubjectOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    model_config = {"from_attributes": True}


class TopicOut(BaseModel):
    id: int
    name: str
    caps_section: Optional[str]
    model_config = {"from_attributes": True}


class OptionIn(BaseModel):
    text: str
    is_correct: bool = False
    order_num: int = 1


class OptionOut(BaseModel):
    id: int
    text: str
    is_correct: bool
    order_num: int
    model_config = {"from_attributes": True}


class OptionPublic(BaseModel):
    """Option without is_correct — served to learners during assessment."""
    id: int
    text: str
    order_num: int
    model_config = {"from_attributes": True}


class QuestionIn(BaseModel):
    topic_id: Optional[int] = None
    text: str
    q_type: QuestionType = QuestionType.MCQ
    marks: int = 1
    difficulty: Difficulty = Difficulty.MEDIUM
    concept_tag: Optional[str] = None
    order_num: int = 1
    correct_answer: Optional[str] = None
    options: List[OptionIn] = []


class QuestionOut(BaseModel):
    id: int
    text: str
    q_type: QuestionType
    marks: int
    difficulty: Difficulty
    concept_tag: Optional[str]
    order_num: int
    options: List[OptionOut]
    model_config = {"from_attributes": True}


class QuestionPublic(BaseModel):
    """Question served to learners — no correct_answer exposed."""
    id: int
    text: str
    q_type: QuestionType
    marks: int
    difficulty: Difficulty
    concept_tag: Optional[str]
    order_num: int
    options: List[OptionPublic]
    model_config = {"from_attributes": True}


class AssessmentIn(BaseModel):
    subject_id: int
    title: str
    description: Optional[str] = None
    time_limit_min: int = 60


class AssessmentOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    total_marks: int
    time_limit_min: int
    is_published: bool
    subject: SubjectOut
    questions: List[QuestionOut] = []
    model_config = {"from_attributes": True}


class AssessmentPublic(BaseModel):
    """Assessment served to learners."""
    id: int
    title: str
    description: Optional[str]
    total_marks: int
    time_limit_min: int
    subject: SubjectOut
    questions: List[QuestionPublic] = []
    model_config = {"from_attributes": True}
