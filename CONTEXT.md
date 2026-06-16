# SKYLearn IQ — Project Context & Progress Log

> **Purpose of this file:** Quick-start reference for any session. Read this first before
> touching any code. Updated at the end of every major phase.

---

## What Is This Project?

**SKYLearn IQ** is an AI-powered digitised learning and assessment platform built for
**SKYLearn-Innovation NPO** — a South African NPO that teaches community learners STEM
and coding. The system replaces paper-based assessments with a fully digital, ML-enhanced
platform covering learner tracking, automated marking, AI feedback, and predictive analytics.

**GitHub:** https://github.com/machetheDM/skylearn-iq
**Owner:** Dingaan Machethe (MSc Data Science UEL · PGDip Regenesys · MSc Cybersecurity ECCU)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Learner Mobile App  ←→  FastAPI Backend  ←→  Tutor Desktop │
│  (Expo 52 RN)             (port 8001)       (.NET MAUI WPF)  │
│                               │                              │
│                          SQLite / PostgreSQL                 │
│                               │                              │
│                    ML Analytics Engine                       │
│                        (port 8002)                           │
│              XGBoost · K-Means · SHAP · ARIMA               │
│                               │                              │
│              AI Feedback (LangChain + Groq/Ollama)           │
│                      n8n automation                          │
│                               │                              │
│              Azure Data Lake + Power BI (Phase 6)            │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase Progress

| # | Phase | Status | Folder |
|---|-------|--------|--------|
| 1 | FastAPI Backend + PostgreSQL schema + seed data | ✅ COMPLETE | `api/` |
| 2 | Expo 52 Learner Mobile App | ✅ COMPLETE | `learner-app/` |
| 3 | .NET MAUI Tutor Desktop App | ✅ COMPLETE | `tutor-desktop/` |
| 4 | ML Analytics Engine (XGBoost, SHAP, ARIMA, K-Means) + MAUI Analytics page | ✅ COMPLETE | `ml-engine/` |
| 5 | AI Feedback (LangChain + Groq/Ollama + template fallback) | ✅ COMPLETE | `ai-feedback/` |
| 6 | Azure Data Lake + Power BI | ✅ COMPLETE | `cloud-bi/` |

---

## Phase Details

### Phase 1 — FastAPI Backend (`api/`)
- `main.py` — app entry point, CORS, router registration, init_db on startup
- `database.py` — SQLAlchemy engine (SQLite dev / PostgreSQL prod via Docker port 5433)
- `core/config.py` — env config · `core/security.py` — bcrypt hashing · `core/auth.py` — JWT
- `models/` — ORM: User/Tutor/Learner, Subject/Topic/Assessment/Question/Option, AssessmentSession/Answer/Score/Feedback
- `schemas/` — Pydantic v2 request/response schemas
- `routers/auth.py` — register, login, /me
- `routers/assessments.py` — CRUD assessments + questions, publish
- `routers/sessions.py` — start, submit (auto-mark MCQ + score), get, my-sessions, tutor-overview, add-feedback, mark-answer
- `routers/users.py` — list learners (tutor-only)
- `seed.py` — 5 subjects, 38 CAPS topics, 1 tutor, 4 learners, 1 sample assessment

### Phase 2 — Learner Mobile App (`learner-app/`)
- Expo 52 + Expo Router 4, TypeScript
- Auth: phone + password → JWT stored in AsyncStorage
- Tabs: Home (dashboard stats) · Assessments (take assessment) · My Results · Profile
- `app/assessment/[id].tsx` — MCQ + short-answer, countdown timer, auto-submit on timeout
- `app/assessment/result/[sessionId].tsx` — score hero, answer breakdown, AI feedback display
- API_URL = `http://10.0.2.2:8001` (Android emulator) — change to LAN IP for physical device

### Phase 3 — Tutor Desktop App (`tutor-desktop/`)
- .NET MAUI C#, Windows-only (net9.0-windows10.0.19041.0)
- CommunityToolkit.Mvvm 8.3.2 — ObservableObject, [ObservableProperty], [RelayCommand]
- DI via MauiProgram.cs (Singleton: AuthService, ApiService; Transient: VMs + Pages + AppShell)
- Shell: Locked flyout sidebar (always-visible on desktop), green #15803D theme
- Pages: Login · Dashboard (stats + recent sessions) · Learners · Assessments (+ publish) · Sessions · SessionDetail (mark answers + add feedback)
- Auth: token stored via Preferences, survives app restart

### Phase 4 — ML Analytics Engine (`ml-engine/`) ← CURRENTLY BUILDING
- Standalone FastAPI app on **port 8002**, reads from the same SQLite DB (`api/skylearn_iq.db`)
- `preprocess.py` — SQL feature extraction per learner (avg_score, pass_rate, completion_rate, total_sessions, days_since_last)
- `models/at_risk.py` — XGBoost binary classifier (trained on synthetic data, scored on real learners). Labels: High Risk / At Risk / Monitor / On Track
- `models/clustering.py` — K-Means K=3 (trained on synthetic, applied to real). Clusters: High Performers / Average / Struggling
- `models/shap_explain.py` — TreeExplainer SHAP values per learner → which feature drives risk most
- `models/forecasting.py` — ARIMA(1,1,1) for ≥5 sessions, linear trend extrapolation otherwise. Forecasts next 1–6 sessions
- `router.py` — endpoints: `/api/ml/at-risk`, `/api/ml/clusters`, `/api/ml/explain/{id}`, `/api/ml/forecast/{id}`, `/api/ml/summary`

**TODO for Phase 4:** Wire ml-engine results into the Tutor Desktop dashboard (call port 8002 from ApiService)

### Phase 4b — MAUI Analytics Page (`tutor-desktop/`)
- `Models/Analytics.cs` — AtRiskResult, ClusterResult, AnalyticsSummary C# models
- `Services/MlApiService.cs` — HttpClient singleton for port 8002 (separate from ApiService)
- `ViewModels/AnalyticsViewModel.cs` — parallel Task.WhenAll for 3 ML endpoints
- `Views/AnalyticsPage.xaml` — summary stats row (4 cards), At-Risk list with risk%, Cluster list
- Added as 5th item in AppShell flyout sidebar
- Shows offline banner if ml-engine is not running (graceful degradation)

### Phase 5 — AI Feedback (`ai-feedback/`) ← COMPLETE
- FastAPI app on **port 8003**
- `feedback_chain.py` — LLM priority: Groq API → Ollama local → deterministic template (always works)
  - Groq model: `llama-3.1-70b-versatile` (free tier — get key at console.groq.com/keys)
  - Ollama model: configurable via `OLLAMA_MODEL` env var (default: `llama3.2`)
- `database.py` — fetch_session_context (all Q&A + score) + save_feedback to feedbacks table
- `router.py` — POST /api/feedback/generate, GET /api/feedback/health
- Backend integration: sessions.py fires a background thread after session submit → triggers AI feedback automatically
- Setup: copy `.env.example` → `.env`, add `GROQ_API_KEY`

### Phase 6 — Cloud BI (`cloud-bi/`) ← COMPLETE
- Medallion architecture: SQLite → Bronze Parquet → Silver Parquet → Gold Parquet
- `export/bronze_export.py` — raw extract from SQLite (8 tables → Parquet)
- `transform/silver.py` — joins: sessions+scores+learners+users+assessments+subjects; dual-engine (PySpark or pandas)
- `transform/gold.py` — 4 Gold tables: subject_performance, learner_cohorts, monthly_trends, assessment_stats
- `azure/provision.sh` — Azure CLI script: ADLS Gen2 + Synapse + Databricks
- `azure/upload_adls.py` — uploads Parquet to ADLS Gen2 (Bronze/Silver/Gold containers)
- `azure/synapse_ddl.sql` — Synapse serverless external tables + Power BI-ready views
- `powerbi/dax_measures.md` — DAX measures + recommended Power BI dashboard pages
- `main.py` — **Streamlit analytics dashboard** (port 8501) with 5 pages:
  - Overview (KPI cards: total learners, at-risk count, avg score, pass rate)
  - Subject Performance (score + pass rate bar charts)
  - Learner Cohorts (scatter map, risk flags, at-risk table)
  - Trends (monthly score line + session volume area + pass rate bars)
  - Assessments (difficulty scatter + stats table)
- `run_pipeline.py` — one-command pipeline runner (Bronze→Silver→Gold)

**Run dashboard:** `$env:PYTHONUTF8=1; streamlit run main.py`  (from cloud-bi/)  
**Run pipeline:** `$env:PYTHONUTF8=1; python run_pipeline.py`  (from cloud-bi/)

---

## Demo Accounts

| Role | Phone | Password |
|------|-------|----------|
| Tutor | +27838751445 | SKYLearn@2026 |
| Learner 1 | +27710000001 | Learner@2026 |
| Learner 2 | +27710000002 | Learner@2026 |
| Learner 3 | +27710000003 | Learner@2026 |
| Learner 4 | +27710000004 | Learner@2026 |

---

## Dev Setup — Start All Services

```bash
# 1. FastAPI Backend (port 8001)
cd api
python -m uvicorn main:app --reload --port 8001

# 2. ML Analytics Engine (port 8002)
cd ml-engine
python -m uvicorn main:app --reload --port 8002

# 3. Learner Mobile App
cd learner-app
npx expo start            # press 'a' for Android emulator

# 4. Tutor Desktop App
cd tutor-desktop
dotnet run -f net9.0-windows10.0.19041.0
```

> **First run only:** `cd api && python seed.py` to populate the database.

---

## Key Design Decisions

- **SQLite in dev, PostgreSQL in prod** — swap via `DATABASE_URL` env var. Docker: `docker compose up -d` (port 5433).
- **Synthetic ML training data** — XGBoost and K-Means train on generated data since real learner data starts minimal. Models score *real* learner features accurately once sessions accumulate.
- **Role enforcement** — All tutor endpoints use `require_tutor` dependency. ML engine has no auth (internal service, add API key for prod).
- **MAUI Windows-only** — Removed iOS/Android/macOS targets to keep Phase 3 focused on desktop. Can re-add targets later.
- **SHAP TreeExplainer** — Used (not KernelExplainer) for speed. Works natively with XGBoost.
- **ARIMA fallback** — When a learner has < 5 sessions, linear trend is used instead of ARIMA to avoid unstable fits.

---

## File Structure Quick Reference

```
skylearn-iq/
├── CONTEXT.md              ← YOU ARE HERE
├── api/                    ← Phase 1: FastAPI backend
│   ├── main.py
│   ├── seed.py
│   ├── models/
│   ├── schemas/
│   └── routers/
├── learner-app/            ← Phase 2: Expo React Native
│   ├── app/
│   ├── context/
│   └── constants/
├── tutor-desktop/          ← Phase 3: .NET MAUI C#
│   ├── Models/
│   ├── Services/
│   ├── ViewModels/
│   └── Views/
├── ml-engine/              ← Phase 4: ML Analytics (current)
│   ├── main.py
│   ├── preprocess.py
│   ├── router.py
│   └── models/
├── ai-feedback/            ← Phase 5: LangChain + n8n (todo)
└── cloud-bi/               ← Phase 6: Azure + Power BI (todo)
```
