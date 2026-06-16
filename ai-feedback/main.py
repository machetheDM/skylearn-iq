"""
SKYLearn IQ — AI Feedback Service  (Phase 5 — COMPLETE)
=========================================================
Purpose : Generates personalised AI feedback for learner assessment sessions.
Port    : 8003  (run: python -m uvicorn main:app --reload --port 8003)
DB      : Reads from + writes to ../api/skylearn_iq.db
LLM     : Groq API (free) → Ollama local → deterministic template fallback

Setup
  1. Copy .env.example → .env
  2. Add GROQ_API_KEY from https://console.groq.com/keys  (free, no credit card)
     OR install Ollama + pull llama3.2 for fully local inference
  3. Without either, the template fallback produces structured feedback automatically

Endpoints
  POST /api/feedback/generate   { session_id: int }  → generates + saves AI feedback
  GET  /api/feedback/health     → shows which LLM backend is active

Integration
  The main backend (port 8001) calls this service after a session is COMPLETED.
  The generated feedback is saved to the feedbacks table (generated_by = 'AI').
  The Learner App then displays it on the session result screen.

See CONTEXT.md at the project root for full architecture and phase progress.
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import router

app = FastAPI(
    title="SKYLearn IQ — AI Feedback Service",
    description="LangChain · Groq (Llama-3.1-70b) · Ollama fallback · Template fallback",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["Health"])
def root():
    return {"service": "SKYLearn IQ AI Feedback", "version": "1.0.0", "status": "running"}
