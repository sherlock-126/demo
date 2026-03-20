"""
Custom exceptions for LLM providers
"""

from typing import Optional, Dict, Any


class LLMProviderError(Exception):
    """Base exception for LLM providers"""

    def __init__(
        self,
        message: str,
        provider: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.provider = provider
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(LLMProviderError):
    """Authentication/authorization failures"""
    suggestion = "Check credentials and re-authenticate"


class ProviderTimeoutError(LLMProviderError):
    """Provider took too long to respond"""
    suggestion = "Increase timeout or retry"


class ResponseParseError(LLMProviderError):
    """Failed to parse provider response"""
    suggestion = "Check response format or provider configuration"


class ProviderNotAvailable(LLMProviderError):
    """Provider is not installed/configured"""
    suggestion = "Install provider or switch to alternative"