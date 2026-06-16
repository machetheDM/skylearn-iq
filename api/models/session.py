import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Boolean, Enum, DateTime,
    ForeignKey, Text, Float
)
from sqlalchemy.orm import relationship
from database import Base


class SessionStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED   = "COMPLETED"
    ABANDONED   = "ABANDONED"


class FeedbackSource(str, enum.Enum):
    AI    = "AI"
    TUTOR = "TUTOR"


class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"

    id            = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    learner_id    = Column(Integer, ForeignKey("learners.id"),    nullable=False)
    started_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at  = Column(DateTime(timezone=True), nullable=True)
    status        = Column(Enum(SessionStatus), default=SessionStatus.IN_PROGRESS)

    assessment = relationship("Assessment", back_populates="sessions")
    learner    = relationship("Learner",    back_populates="sessions")
    answers    = relationship("Answer",     back_populates="session", cascade="all, delete-orphan")
    score      = relationship("Score",      back_populates="session", uselist=False)
    feedbacks  = relationship("Feedback",   back_populates="session", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id                 = Column(Integer, primary_key=True, index=True)
    session_id         = Column(Integer, ForeignKey("assessment_sessions.id"), nullable=False)
    question_id        = Column(Integer, ForeignKey("questions.id"),           nullable=False)
    selected_option_id = Column(Integer, ForeignKey("options.id"),             nullable=True)
    text_answer        = Column(Text,    nullable=True)
    is_correct         = Column(Boolean, nullable=True)
    marks_awarded      = Column(Float,   default=0.0)
    auto_marked        = Column(Boolean, default=False)
    answered_at        = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session  = relationship("AssessmentSession", back_populates="answers")
    question = relationship("Question",          back_populates="answers")
    option   = relationship("Option")


class Score(Base):
    __tablename__ = "scores"

    id                   = Column(Integer, primary_key=True, index=True)
    session_id           = Column(Integer, ForeignKey("assessment_sessions.id"), unique=True, nullable=False)
    total_marks_awarded  = Column(Float, default=0.0)
    total_marks_possible = Column(Integer, default=0)
    percentage           = Column(Float, default=0.0)
    pass_fail            = Column(Boolean, nullable=True)  # True=pass, False=fail
    scored_at            = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("AssessmentSession", back_populates="score")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(Integer, ForeignKey("assessment_sessions.id"), nullable=False)
    generated_by    = Column(Enum(FeedbackSource), default=FeedbackSource.AI)
    content         = Column(Text, nullable=False)
    strength_areas  = Column(Text, nullable=True)   # JSON string list
    weakness_areas  = Column(Text, nullable=True)   # JSON string list
    recommendations = Column(Text, nullable=True)
    created_at      = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("AssessmentSession", back_populates="feedbacks")
