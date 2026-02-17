import json
import os
from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> str | None:
    """
    Find .env file by searching in multiple locations:
    1. Current working directory
    2. Parent directory
    3. Backend directory (where config.py is)
    4. Project root (parent of backend)
    
    Returns the path to the first .env file found, or None if not found.
    """
    search_paths = [
        Path.cwd() / ".env",                                  # Current directory
        Path.cwd().parent / ".env",                           # Parent directory
        Path(__file__).parent.parent / ".env",                # backend/.env
        Path(__file__).parent.parent.parent / ".env",         # project_root/.env
    ]
    
    for env_path in search_paths:
        if env_path.exists():
            return str(env_path)
    
    return None


# Try to find .env file, fallback to project root if not found
ENV_FILE = find_env_file()
if ENV_FILE is None:
    # Fallback to project root
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    ENV_FILE = str(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "Lazy Rabbit AI Agent Server"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] | str = ["http://localhost:5173"]

    # Weather Provider Configuration
    WEATHER_PROVIDER: str = "gaode"  # Provider type: gaode, qweather, openweather
    WEATHER_API_KEY: str  # Provider-specific API key (required)
    WEATHER_BASE_URL: str  # Provider-specific base URL (required)
    WEATHER_CACHE_TTL: int = 3600  # Cache TTL in seconds (default 1 hour)

    # LLM API Configuration
    LLM_PROVIDER: str = "openai"  # Provider type: openai, deepseek, anthropic, ollama
    LLM_API_KEY: str  # LLM API key (required)
    LLM_BASE_URL: str = "https://api.openai.com/v1"  # Base URL for OpenAI-compatible API
    LLM_MODEL: str = "gpt-3.5-turbo"  # Model name (e.g., "deepseek-chat", "gpt-4")
    LLM_VERIFY_SSL: bool = True  # Set to False for self-hosted LLMs with self-signed certs
    LLM_TIMEOUT: float = 30.0  # Request timeout in seconds
    RECOMMENDATION_CACHE_TTL: int = 3600  # Cache TTL for recommendations (1 hour)

    # Email Configuration (SMTP)
    MAIL_SERVER: str = "smtp.163.com"  # SMTP server hostname
    MAIL_PORT: int = 465  # SMTP server port (465 for SSL, 587 for TLS)
    MAIL_USE_SSL: bool = True  # Use SSL for SMTP connection (port 465)
    MAIL_USE_TLS: bool = False  # Use STARTTLS for SMTP connection (port 587) - mutually exclusive with SSL
    MAIL_USERNAME: str = ""  # SMTP username (email address)
    MAIL_PASSWORD: str = ""  # SMTP password (app password for 163.com)
    MAIL_SENDER: str = ""  # From email address (sender)

    # PlantUML Configuration (for article mindmap rendering)
    PLANTUML_SERVER_URL: str = "http://www.plantuml.com/plantuml"  # PlantUML server URL
    PLANTUML_JAR_PATH: str = ""  # Path to local plantuml.jar (optional, faster than server)
    PLANTUML_OUTPUT_DIR: str = "static/mindmaps"  # Directory to save rendered PNGs

    # Secretary Agent Configuration
    LOG_LEVEL_SECRETARY: str = "INFO"  # Log level for secretary agent
    TRACE_DETAILED: bool = False  # Log full prompts/responses (verbose, for debugging)
    LOG_FORMAT: str = "text"  # Log format: "json" or "text"

    # Cronjob Configuration
    CRONJOB_SECRET_TOKEN: str = ""  # Secret token for cronjob authentication (optional, for production)

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str] | str:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            try:
                # Try to parse as JSON array
                return json.loads(v)
            except json.JSONDecodeError:
                # Fall back to comma-separated values
                return [origin.strip() for origin in v.split(",")]
        return v


# Global settings instance
settings = Settings()


