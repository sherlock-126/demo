"""
Layout Generator for TikTok content
Generates split-screen comparison images from JSON scripts
"""

from .api import LayoutGenerator
from .models import LayoutConfig, RenderResult, FontConfig, ColorConfig, IconConfig, LogoConfig

__version__ = "1.0.0"
__all__ = [
    "LayoutGenerator",
    "LayoutConfig",
    "RenderResult",
    "FontConfig",
    "ColorConfig",
    "IconConfig",
    "LogoConfig"
]