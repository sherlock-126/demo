"""
Text renderer component
"""

from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Dict
from ..utils.text import wrap_text, calculate_text_size
from ..utils.colors import hex_to_rgb
from ..utils.fonts import load_font


class TextRenderer:
    """Render text elements on images"""

    def __init__(self, fonts: Dict[str, Dict], colors: Dict[str, str]):
        self.fonts = fonts
        self.colors = colors
        self._font_cache = {}

    def _get_font(self, font_type: str) -> ImageFont.FreeTypeFont:
        """Get font from cache or load it"""
        if font_type not in self._font_cache:
            font_config = self.fonts.get(font_type, self.fonts.get('text'))
            font = load_font(
                font_config['path'],
                font_config['size'],
                font_config.get('fallback')
            )
            self._font_cache[font_type] = font
        return self._font_cache[font_type]

    def render_title(self, img: Image.Image, title: str, y_position: int = 100) -> None:
        """Render main title"""
        draw = ImageDraw.Draw(img)
        font = self._get_font('title')
        color = hex_to_rgb(self.colors.get('title', '#2C3E50'))

        # Center title
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img.width - text_width) // 2

        draw.text((x, y_position), title, fill=color, font=font)

    def render_subtitle(self, img: Image.Image, subtitle: str, y_position: int = 180) -> None:
        """Render subtitle"""
        draw = ImageDraw.Draw(img)
        font = self._get_font('subtitle')
        color = hex_to_rgb(self.colors.get('subtitle', '#7F8C8D'))

        # Center subtitle
        bbox = draw.textbbox((0, 0), subtitle, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img.width - text_width) // 2

        draw.text((x, y_position), subtitle, fill=color, font=font)

    def render_side_label(self, img: Image.Image, label: str, side: str, y_position: int = 350) -> None:
        """Render SAI/ĐÚNG label"""
        draw = ImageDraw.Draw(img)
        font = self._get_font('label')

        # Determine color based on label
        if label in ['SAI', 'WRONG']:
            color = hex_to_rgb(self.colors.get('label_wrong', '#E74C3C'))
        else:
            color = hex_to_rgb(self.colors.get('label_right', '#27AE60'))

        # Position based on side
        if side == 'left':
            x = img.width // 4
        else:
            x = (img.width * 3) // 4

        # Center text horizontally within side
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        x = x - text_width // 2

        draw.text((x, y_position), label, fill=color, font=font)

    def render_side_content(self, img: Image.Image, text: str, side: str,
                          y_position: int = 450, padding: int = 40) -> None:
        """Render content text for a side"""
        draw = ImageDraw.Draw(img)
        font = self._get_font('text')
        color = hex_to_rgb(self.colors.get('content', '#34495E'))

        # Calculate boundaries for side
        if side == 'left':
            x_start = padding
            x_end = img.width // 2 - padding
        else:
            x_start = img.width // 2 + padding
            x_end = img.width - padding

        max_width = x_end - x_start

        # Wrap text
        lines = wrap_text(text, max_width, font)

        # Render lines
        line_height = font.size + 15
        current_y = y_position

        for line in lines:
            # Center each line within the side
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = x_start + (max_width - text_width) // 2

            draw.text((x, current_y), line, fill=color, font=font)
            current_y += line_height

    def render_slide_number(self, img: Image.Image, current: int, total: int) -> None:
        """Render slide number indicator"""
        draw = ImageDraw.Draw(img)
        font = self._get_font('text')
        color = hex_to_rgb(self.colors.get('subtitle', '#7F8C8D'))

        text = f"{current}/{total}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        # Position at bottom center
        x = (img.width - text_width) // 2
        y = img.height - 100

        draw.text((x, y), text, fill=color, font=font)