"""
Content Generator - AI-powered TikTok content script generation
"""

from .api import ScriptGenerator
from .models import ScriptModel, Slide, SideContent, ScriptMetadata, ErrorResponse

__version__ = "1.0.0"
__all__ = [
    "ScriptGenerator",
    "ScriptModel",
    "Slide",
    "SideContent",
    "ScriptMetadata",
    "ErrorResponse"
]