from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://skylearn:skylearn_secret@localhost:5433/skylearn_iq"
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
