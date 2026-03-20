"""
Font management utilities
"""

from PIL import ImageFont
from pathlib import Path
from typing import Optional
import platform


def load_font(font_path: str, size: int, fallback_path: Optional[str] = None) -> ImageFont.FreeTypeFont:
    """Load font with fallback option"""
    try:
        if Path(font_path).exists():
            return ImageFont.truetype(font_path, size)
    except Exception as e:
        pass

    # Try fallback
    if fallback_path and Path(fallback_path).exists():
        try:
            return ImageFont.truetype(fallback_path, size)
        except:
            pass

    # Use system default
    return get_fallback_font(size)


def get_fallback_font(size: int) -> ImageFont.FreeTypeFont:
    """Get system fallback font"""
    system = platform.system()

    # Common font paths by system
    font_paths = []

    if system == "Linux":
        font_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
        ]
    elif system == "Darwin":  # macOS
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf"
        ]
    elif system == "Windows":
        font_paths = [
            "C:/Windows/Fonts/Arial.ttf",
            "C:/Windows/Fonts/calibri.ttf"
        ]

    for path in font_paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except:
                continue

    # Last resort: use default font
    return ImageFont.load_default()