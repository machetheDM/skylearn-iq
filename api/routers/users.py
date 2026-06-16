from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.user import User, Learner
from models.session import AssessmentSession
from schemas.user import LearnerOut
from core.auth import require_tutor

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/learners", response_model=List[LearnerOut])
def list_learners(
    db: Session = Depends(get_db),
    _: User = Depends(require_tutor),
):
    learners = db.query(Learner).all()
    result = []
    for learner in learners:
        total = db.query(AssessmentSession).filter(AssessmentSession.learner_id == learner.id).count()
        result.append(LearnerOut(
            user_id=learner.user_id,
            learner_id=learner.id,
            full_name=learner.user.full_name,
            phone=learner.user.phone,
            grade=learner.grade,
            track=learner.track.value if learner.track else "",
            total_sessions=total,
        ))
    return result
