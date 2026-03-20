"""
Content Generator - AI-powered TikTok content script generation
"""

from .api import ScriptGenerator
from .models import ScriptModel, Slide, SideContent, ScriptMetadata, ErrorResponse
from .llm_providers import LLMProvider, get_llm_provider

__version__ = "1.0.0"
__all__ = [
    "ScriptGenerator",
    "ScriptModel",
    "Slide",
    "SideContent",
    "ScriptMetadata",
    "ErrorResponse",
    "LLMProvider",
    "get_llm_provider"
]