"""
Application configuration settings
"""
import os
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TikTok Content Generator"

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3001", "http://localhost:3000"]

    # Database
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # OpenAI Settings
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai_api"

    # File paths
    DATA_DIR: str = "/app/data"
    OUTPUT_DIR: str = "/app/output"
    VIDEOS_DIR: str = "/app/videos"
    ASSETS_DIR: str = "/app/assets"
    TEMP_DIR: str = "/app/temp"

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override with environment variables if they exist
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", self.OPENAI_API_KEY)
        self.LLM_PROVIDER = os.getenv("LLM_PROVIDER", self.LLM_PROVIDER)
        self.DATABASE_URL = os.getenv("DATABASE_URL", self.DATABASE_URL)

        # Parse CORS origins from environment
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            self.CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",")]

settings = Settings()