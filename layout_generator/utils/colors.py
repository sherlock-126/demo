"""
Color utility functions
"""

from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(*rgb)


def apply_opacity(color: Tuple[int, int, int], opacity: float) -> Tuple[int, int, int, int]:
    """Apply opacity to RGB color, returning RGBA"""
    return (*color, int(255 * opacity))