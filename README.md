# SKYLearn IQ 🧠

> AI-powered digital learning and assessment platform for SKYLearn-Innovation NPO

## What It Is

SKYLearn IQ digitises the tutoring experience for underserved SA learners — replacing paper-based assessments with an AI-driven platform that gives tutors real-time insights into every learner's strengths, weaknesses, and progress across CAPS subjects.

## Platform Components

| Component | Tech | Status |
|---|---|---|
| **API Backend** | FastAPI + PostgreSQL | ✅ Phase 1 Complete |
| **Tutor Desktop App** | .NET MAUI (C#) | 🔨 Phase 3 |
| **Learner Mobile App** | Expo 52 React Native | 🔨 Phase 2 |
| **ML Analytics Engine** | Python, XGBoost, SHAP, ARIMA | 🔨 Phase 4 |
| **AI Feedback Layer** | LangChain, Ollama, Groq API | 🔨 Phase 5 |
| **Cloud BI** | Azure Data Lake + Power BI | 🔨 Phase 6 |

## Subjects Covered

- Mathematics (CAPS Gr 10–12 + Matric Upgrade)
- Mathematical Literacy (CAPS Gr 10–12)
- Physical Sciences (CAPS Gr 10–12)
- Python + Data Science Fundamentals
- Cybersecurity Awareness

## Quick Start (API)

**Prerequisites:** Docker Desktop running

```bash
# 1. Start PostgreSQL
docker compose up db -d

# 2. Install dependencies
cd api
pip install -r requirements.txt

# 3. Start API
uvicorn main:app --reload --port 8001

# 4. Seed database (new terminal)
python seed.py
```

**Docs:** http://localhost:8001/docs

## Demo Accounts

| Role | Phone | Password |
|---|---|---|
| Tutor (Dingaan) | +27838751445 | SKYLearn@2026 |
| Learner (Thabo, Gr 12) | +27710000001 | Learner@2026 |
| Learner (Lerato, Gr 11) | +27710000002 | Learner@2026 |
| Learner (Sipho, Upgrade) | +27710000003 | Learner@2026 |
| Learner (Naledi, Coding) | +27710000004 | Learner@2026 |

## API Endpoints

```
POST   /api/auth/register/tutor        Register a tutor
POST   /api/auth/register/learner      Register a learner
POST   /api/auth/login                 Login → JWT token
GET    /api/auth/me                    Current user profile

GET    /api/subjects                   List all subjects
GET    /api/subjects/{id}/topics       Topics per subject

POST   /api/assessments               Create assessment (tutor)
GET    /api/assessments               List my assessments (tutor)
GET    /api/assessments/published     Published assessments (learner)
GET    /api/assessments/{id}          Get assessment detail
PATCH  /api/assessments/{id}/publish  Publish assessment
POST   /api/assessments/{id}/questions Add question + options
DELETE /api/assessments/{id}/questions/{qid}

POST   /api/sessions/{assessment_id}/start     Start a session (learner)
POST   /api/sessions/{session_id}/submit       Submit answers → auto-mark → score
GET    /api/sessions/{session_id}              Get session result
GET    /api/sessions/learner/my-sessions       My sessions (learner)
GET    /api/sessions/tutor/all-sessions        All sessions for an assessment (tutor)
```

## Database Schema

```
users → tutors / learners
subjects → topics
assessments (tutor + subject) → questions → options
assessment_sessions (learner + assessment) → answers + score + feedbacks
```

## Architecture

```
Learner App (Expo)  ──┐
                       ├──► FastAPI (port 8001) ──► PostgreSQL (port 5433)
Tutor Desktop (.NET) ──┘         │
                                  ├──► ML Engine (XGBoost, SHAP, ARIMA)  [Phase 4]
                                  ├──► AI Feedback (LangChain + Ollama/Groq)  [Phase 5]
                                  └──► Azure Data Lake → Power BI  [Phase 6]
```

## Built By

**Dingaan Mahlatse Machethe** — Data Scientist, AI/ML Engineer, Founder SKYLearn-Innovation NPO

*MSc Data Science (UEL) | PGDip Data Science (Regenesys) | CND (EC-Council)*
