"""
SKYLearn IQ — FastAPI Backend  (Phase 1 — COMPLETE)
===================================================
Purpose : REST API serving both the Learner Mobile App and the Tutor Desktop App.
Port    : 8001  (run: python -m uvicorn main:app --reload --port 8001)
DB      : SQLite dev (skylearn_iq.db)  |  PostgreSQL prod (Docker port 5433)

Router map
  /api/auth/*          — register tutor/learner, login (JWT), /me
  /api/assessments/*   — CRUD assessments + questions, publish
  /api/sessions/*      — start, submit (auto-mark MCQ), get, learner/tutor lists,
                         add-feedback, mark short-answer
  /api/users/*         — list learners (tutor-only)

See CONTEXT.md at the project root for full architecture and phase progress.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import auth, assessments, sessions, users

app = FastAPI(
    title="SKYLearn IQ API",
    description="AI-powered assessment and learning analytics platform for SKYLearn-Innovation NPO",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(assessments.router)
app.include_router(sessions.router)
app.include_router(users.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", tags=["Health"])
def root():
    return {"service": "SKYLearn IQ API", "version": "1.0.0", "status": "running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
