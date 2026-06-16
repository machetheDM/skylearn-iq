import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, DateTime,
    ForeignKey, Text, Float
)
from sqlalchemy.orm import relationship
from database import Base


class QuestionType(str, enum.Enum):
    MCQ          = "MCQ"
    SHORT_ANSWER = "SHORT_ANSWER"
    CODING       = "CODING"


class Difficulty(str, enum.Enum):
    EASY   = "EASY"
    MEDIUM = "MEDIUM"
    HARD   = "HARD"


class Subject(Base):
    __tablename__ = "subjects"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), unique=True, nullable=False)
    code        = Column(String(20),  unique=True, nullable=False)
    description = Column(String(300), nullable=True)

    topics      = relationship("Topic",      back_populates="subject")
    assessments = relationship("Assessment", back_populates="subject")


class Topic(Base):
    __tablename__ = "topics"

    id           = Column(Integer, primary_key=True, index=True)
    subject_id   = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name         = Column(String(150), nullable=False)
    caps_section = Column(String(150), nullable=True)  # e.g. "Algebra", "Waves & Sound"

    subject   = relationship("Subject",    back_populates="topics")
    questions = relationship("Question",   back_populates="topic")


class Assessment(Base):
    __tablename__ = "assessments"

    id              = Column(Integer, primary_key=True, index=True)
    tutor_id        = Column(Integer, ForeignKey("tutors.id"), nullable=False)
    subject_id      = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title           = Column(String(200), nullable=False)
    description     = Column(Text, nullable=True)
    total_marks     = Column(Integer, default=0)
    time_limit_min  = Column(Integer, default=60)
    is_published    = Column(Boolean, default=False)
    created_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tutor     = relationship("Tutor",    back_populates="assessments")
    subject   = relationship("Subject",  back_populates="assessments")
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    sessions  = relationship("AssessmentSession", back_populates="assessment")


class Question(Base):
    __tablename__ = "questions"

    id            = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    topic_id      = Column(Integer, ForeignKey("topics.id"),      nullable=True)
    text          = Column(Text, nullable=False)
    q_type        = Column(Enum(QuestionType), default=QuestionType.MCQ)
    marks         = Column(Integer, default=1)
    difficulty    = Column(Enum(Difficulty),   default=Difficulty.MEDIUM)
    concept_tag   = Column(String(100), nullable=True)  # e.g. "quadratic equations"
    order_num     = Column(Integer, default=1)
    correct_answer= Column(Text, nullable=True)  # for SHORT_ANSWER / CODING

    assessment = relationship("Assessment", back_populates="questions")
    topic      = relationship("Topic",      back_populates="questions")
    options    = relationship("Option",     back_populates="question", cascade="all, delete-orphan")
    answers    = relationship("Answer",     back_populates="question")


class Option(Base):
    __tablename__ = "options"

    id          = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    text        = Column(Text, nullable=False)
    is_correct  = Column(Boolean, default=False)
    order_num   = Column(Integer, default=1)

    question = relationship("Question", back_populates="options")
