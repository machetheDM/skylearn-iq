from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db, fetch_session_context, save_feedback
from feedback_chain import generate_feedback, GROQ_API_KEY, OLLAMA_URL

router = APIRouter(prefix="/api/feedback", tags=["AI Feedback"])


class GenerateRequest(BaseModel):
    session_id: int


class FeedbackResponse(BaseModel):
    feedback_id:     int
    session_id:      int
    learner_name:    str
    assessment_title: str
    score_pct:       float
    content:         str
    strength_areas:  str
    weakness_areas:  str
    recommendations: str
    provider:        str


@router.post("/generate", response_model=FeedbackResponse)
def generate(req: GenerateRequest, db: Session = Depends(get_db)):
    """
    Generate AI feedback for a completed session and persist it to the feedbacks table.
    Tries Groq → Ollama → template fallback automatically.
    """
    ctx = fetch_session_context(db, req.session_id)
    if not ctx:
        raise HTTPException(404, f"Session {req.session_id} not found or has no score yet.")

    result = generate_feedback(ctx)

    fb_id = save_feedback(
        db,
        session_id      = req.session_id,
        content         = result["content"],
        strength_areas  = result.get("strength_areas", ""),
        weakness_areas  = result.get("weakness_areas", ""),
        recommendations = result.get("recommendations", ""),
    )

    return FeedbackResponse(
        feedback_id      = fb_id,
        session_id       = req.session_id,
        learner_name     = ctx["learner_name"],
        assessment_title = ctx["assessment_title"],
        score_pct        = ctx["score_pct"],
        provider         = result.get("provider", "template"),
        **{k: result.get(k, "") for k in ["content", "strength_areas", "weakness_areas", "recommendations"]},
    )


@router.get("/health")
def health():
    """Show which LLM backend is active."""
    if GROQ_API_KEY:
        provider = "groq (llama-3.1-70b-versatile)"
    elif OLLAMA_URL:
        provider = f"ollama ({OLLAMA_URL})"
    else:
        provider = "template-fallback (no LLM key set)"

    return {
        "status":   "ok",
        "provider": provider,
        "groq_key_set":  bool(GROQ_API_KEY),
        "ollama_url_set": bool(OLLAMA_URL),
    }
