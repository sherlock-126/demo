"""
Data models for LLM providers
"""

from pydantic import BaseModel
from typing import Dict, Any, Optional
from enum import Enum


class ProviderType(str, Enum):
    """Available LLM provider types"""
    OPENAI_API = "openai_api"
    CLI_CHATGPT = "cli_chatgpt"
    REVCHATGPT = "revchatgpt"
    MOCK = "mock"  # For testing


class LLMResponse(BaseModel):
    """Unified response model for all providers"""
    content: Dict[str, Any]  # Parsed JSON content
    raw_content: str  # Raw text response
    tokens_used: int  # Actual or estimated
    model: str  # Model name/identifier
    duration: float  # Processing time in seconds
    provider: str  # Provider that generated response


class ProviderConfig(BaseModel):
    """Configuration for a provider"""
    provider_type: ProviderType
    api_key: Optional[str] = None
    cli_command: Optional[str] = None
    access_token: Optional[str] = None
    session_token: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    additional_params: Dict[str, Any] = {}


class CLIExecutionResult(BaseModel):
    """Result from CLI command execution"""
    stdout: str
    stderr: str
    return_code: int
    duration: float