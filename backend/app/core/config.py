"""Application configuration using Pydantic settings."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./ai_council.db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    # Cloud AI Provider API Keys
    GROQ_API_KEY: str = ""
    TOGETHER_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""

    # Application Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    API_V1_PREFIX: str = "/api/v1"

    # Rate Limiting
    RATE_LIMIT_AUTHENTICATED: int = 100
    RATE_LIMIT_DEMO: int = 3
    RATE_LIMIT_ADMIN: int = 1000

    # WebSocket Configuration
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    WEBSOCKET_IDLE_TIMEOUT: int = 300
    WEBSOCKET_MAX_CONNECTIONS_PER_USER: int = 5

    # Logging
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"


settings = Settings()
