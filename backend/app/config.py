from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "TunisPark AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://tunispark:tunispark@localhost:5432/tunispark"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://tunispark:tunispark@localhost:5432/tunispark"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_LONG_RANDOM_STRING"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # AI
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "mistral"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    FAISS_INDEX_PATH: str = "faiss_parking_kb"
    KNOWLEDGE_BASE_DIR: str = "../knowledge_base"

    # Camera / Vision
    VISION_API_URL: str = "http://localhost:8001"
    DEBOUNCE_SECONDS: int = 30

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Storage
    SNAPSHOT_DIR: str = "snapshots"
    SNAPSHOT_RETENTION_DAYS: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
