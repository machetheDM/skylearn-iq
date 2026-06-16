import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base


class UserRole(str, enum.Enum):
    ADMIN   = "ADMIN"
    TUTOR   = "TUTOR"
    LEARNER = "LEARNER"


class LearnerTrack(str, enum.Enum):
    CAPS_FULL_TIME = "CAPS_FULL_TIME"
    MATRIC_UPGRADE = "MATRIC_UPGRADE"
    CODING         = "CODING"
    CYBER          = "CYBER"


class User(Base):
    __tablename__ = "users"

    id             = Column(Integer, primary_key=True, index=True)
    full_name      = Column(String(120), nullable=False)
    email          = Column(String(180), unique=True, index=True, nullable=True)
    phone          = Column(String(20),  unique=True, index=True, nullable=False)
    hashed_password= Column(String(255), nullable=False)
    role           = Column(Enum(UserRole), nullable=False, default=UserRole.LEARNER)
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tutor   = relationship("Tutor",   back_populates="user", uselist=False)
    learner = relationship("Learner", back_populates="user", uselist=False)


class Tutor(Base):
    __tablename__ = "tutors"

    id            = Column(Integer, primary_key=True, index=True)
    user_id       = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    bio           = Column(String(500), nullable=True)
    qualification = Column(String(200), nullable=True)

    user        = relationship("User",       back_populates="tutor")
    assessments = relationship("Assessment", back_populates="tutor")


class Learner(Base):
    __tablename__ = "learners"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    grade          = Column(String(10), nullable=True)     # e.g. "11", "12", "UPGRADE"
    track          = Column(Enum(LearnerTrack), default=LearnerTrack.CAPS_FULL_TIME)
    date_of_birth  = Column(Date, nullable=True)
    guardian_name  = Column(String(120), nullable=True)
    guardian_phone = Column(String(20),  nullable=True)

    user     = relationship("User",              back_populates="learner")
    sessions = relationship("AssessmentSession", back_populates="learner")
