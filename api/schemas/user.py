from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from models.user import UserRole, LearnerTrack


class TutorRegisterIn(BaseModel):
    full_name: str
    phone: str
    email: Optional[str] = None
    password: str
    bio: Optional[str] = None
    qualification: Optional[str] = None


class LearnerRegisterIn(BaseModel):
    full_name: str
    phone: str
    password: str
    grade: Optional[str] = None
    track: LearnerTrack = LearnerTrack.CAPS_FULL_TIME
    date_of_birth: Optional[date] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None


class LoginIn(BaseModel):
    phone: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    user_id: int
    full_name: str


class UserOut(BaseModel):
    id: int
    full_name: str
    phone: str
    email: Optional[str]
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
