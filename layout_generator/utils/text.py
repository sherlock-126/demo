"""
Text processing utilities
"""

import textwrap
from typing import List, Tuple
from PIL import ImageFont, ImageDraw, Image


def wrap_text(text: str, max_width: int, font: ImageFont.FreeTypeFont) -> List[str]:
    """Wrap text to fit within specified width"""
    # Create temporary image for text measurement
    img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(img)

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                # Word is too long, force break
                lines.append(word)
                current_line = []

    if current_line:
        lines.append(' '.join(current_line))

    return lines if lines else [text]


def calculate_text_size(text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    """Calculate the size of text when rendered"""
    img = Image.new('RGB', (1, 1))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def fit_text_to_box(text: str, box_width: int, box_height: int,
                    font_path: str, max_size: int = 72) -> Tuple[List[str], ImageFont.FreeTypeFont]:
    """Fit text to a box by adjusting font size and wrapping"""
    for size in range(max_size, 10, -2):
        try:
            font = ImageFont.truetype(font_path, size)
        except:
            from ..utils.fonts import get_fallback_font
            font = get_fallback_font(size)

        lines = wrap_text(text, box_width - 20, font)  # Leave some padding

        # Check if all lines fit vertically
        total_height = len(lines) * (size + 10)  # Line height with spacing
        if total_height <= box_height:
            return lines, font

    # If we get here, use minimum size
    font = ImageFont.truetype(font_path, 12) if font_path else get_fallback_font(12)
    return wrap_text(text, box_width - 20, font), font