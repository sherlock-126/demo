"""Configuration management for FastAPI backend"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "TikTok Content Generator API"
    debug: bool = Field(default=False, env="DEBUG")

    # Server Settings
    backend_host: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    backend_port: int = Field(default=8000, env="BACKEND_PORT")

    # CORS Settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3001", "http://localhost:3000"],
        env="CORS_ORIGINS"
    )

    # OpenAI Settings
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")

    # File Paths
    data_dir: str = "/app/data"
    output_dir: str = "/app/output"
    videos_dir: str = "/app/videos"
    assets_dir: str = "/app/assets"

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()