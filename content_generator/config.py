"""
Configuration management for the content generator
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """Application configuration"""

    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration from environment variables"""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.timeout_seconds = int(os.getenv("TIMEOUT_SECONDS", "30"))

        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "data/logs/generation.log")

        # Storage Configuration
        self.data_dir = Path(os.getenv("DATA_DIR", "data"))
        self.cache_enabled = os.getenv("CACHE_ENABLED", "false").lower() == "true"

        # Paths
        self.scripts_dir = self.data_dir / "scripts"
        self.logs_dir = self.data_dir / "logs"
        self.cache_dir = Path("cache")
        self.templates_dir = Path("templates")

        # Create directories if they don't exist
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories"""
        for directory in [self.scripts_dir, self.logs_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def validate(self) -> bool:
        """Validate configuration"""
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required. "
                "Please set it in your environment or .env file"
            )

        if not self.openai_api_key.startswith("sk-"):
            raise ValueError(
                "Invalid OPENAI_API_KEY format. "
                "Key should start with 'sk-'"
            )

        return True

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv("ENV", "development").lower() == "production"


# Global configuration instance
config = Config()