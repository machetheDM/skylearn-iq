from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, Tutor, Learner, UserRole
from schemas.user import TutorRegisterIn, LearnerRegisterIn, LoginIn, TokenOut, UserOut
from core.security import hash_password, verify_password, create_access_token
from core.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register/tutor", response_model=TokenOut, status_code=201)
def register_tutor(body: TutorRegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == body.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")
    user = User(
        full_name=body.full_name,
        phone=body.phone,
        email=body.email,
        hashed_password=hash_password(body.password),
        role=UserRole.TUTOR,
    )
    db.add(user)
    db.flush()
    tutor = Tutor(user_id=user.id, bio=body.bio, qualification=body.qualification)
    db.add(tutor)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenOut(access_token=token, role=user.role, user_id=user.id, full_name=user.full_name)


@router.post("/register/learner", response_model=TokenOut, status_code=201)
def register_learner(body: LearnerRegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == body.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")
    user = User(
        full_name=body.full_name,
        phone=body.phone,
        hashed_password=hash_password(body.password),
        role=UserRole.LEARNER,
    )
    db.add(user)
    db.flush()
    learner = Learner(
        user_id=user.id,
        grade=body.grade,
        track=body.track,
        date_of_birth=body.date_of_birth,
        guardian_name=body.guardian_name,
        guardian_phone=body.guardian_phone,
    )
    db.add(learner)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenOut(access_token=token, role=user.role, user_id=user.id, full_name=user.full_name)


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == body.phone, User.is_active == True).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid phone or password")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenOut(access_token=token, role=user.role, user_id=user.id, full_name=user.full_name)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
