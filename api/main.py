from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import auth, assessments, sessions

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


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", tags=["Health"])
def root():
    return {"service": "SKYLearn IQ API", "version": "1.0.0", "status": "running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
