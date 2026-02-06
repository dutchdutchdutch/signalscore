"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "SignalScore"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/signalscore.db"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://frontend:3000"]
    
    # Auth (for future JWT validation)
    AUTH_SECRET: str = "dev-secret-change-in-production"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


settings = Settings()
