"""
Icon renderer component
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import Optional, Tuple
from ..utils.image import resize_image_aspect
from ..logger import get_logger

logger = get_logger(__name__)


class IconRenderer:
    """Render icons on images"""

    def __init__(self, icon_config: dict):
        self.wrong_path = icon_config.get('wrong')
        self.right_path = icon_config.get('right')
        self.size = icon_config.get('size', 100)
        self._icon_cache = {}

    def _load_icon(self, path: str) -> Optional[Image.Image]:
        """Load and cache icon"""
        if path in self._icon_cache:
            return self._icon_cache[path]

        try:
            if Path(path).exists():
                icon = Image.open(path)
                # Resize to target size
                icon = resize_image_aspect(icon, (self.size, self.size))
                # Convert to RGBA for transparency
                if icon.mode != 'RGBA':
                    icon = icon.convert('RGBA')
                self._icon_cache[path] = icon
                return icon
        except Exception as e:
            logger.warning(f"Failed to load icon {path}: {e}")

        return None

    def render_wrong_icon(self, img: Image.Image, position: Optional[Tuple[int, int]] = None) -> None:
        """Render wrong/X icon"""
        icon = self._load_icon(self.wrong_path) if self.wrong_path else None

        if not icon:
            # Fallback: draw X symbol
            self._draw_x_symbol(img, position)
            return

        if position is None:
            # Default position: left side, below label
            x = img.width // 4 - icon.width // 2
            y = 500
        else:
            x, y = position

        # Paste with transparency
        img.paste(icon, (x, y), icon if icon.mode == 'RGBA' else None)

    def render_right_icon(self, img: Image.Image, position: Optional[Tuple[int, int]] = None) -> None:
        """Render right/check icon"""
        icon = self._load_icon(self.right_path) if self.right_path else None

        if not icon:
            # Fallback: draw check symbol
            self._draw_check_symbol(img, position)
            return

        if position is None:
            # Default position: right side, below label
            x = (img.width * 3) // 4 - icon.width // 2
            y = 500
        else:
            x, y = position

        # Paste with transparency
        img.paste(icon, (x, y), icon if icon.mode == 'RGBA' else None)

    def _draw_x_symbol(self, img: Image.Image, position: Optional[Tuple[int, int]] = None) -> None:
        """Draw X symbol as fallback"""
        draw = ImageDraw.Draw(img)

        if position is None:
            x = img.width // 4
            y = 500
        else:
            x, y = position

        # Draw red X
        size = self.size // 2
        color = (231, 76, 60)  # Red
        line_width = 8

        draw.line([(x - size, y - size), (x + size, y + size)], fill=color, width=line_width)
        draw.line([(x - size, y + size), (x + size, y - size)], fill=color, width=line_width)

    def _draw_check_symbol(self, img: Image.Image, position: Optional[Tuple[int, int]] = None) -> None:
        """Draw check symbol as fallback"""
        draw = ImageDraw.Draw(img)

        if position is None:
            x = (img.width * 3) // 4
            y = 500
        else:
            x, y = position

        # Draw green checkmark
        size = self.size // 2
        color = (39, 174, 96)  # Green
        line_width = 8

        # Draw checkmark shape
        points = [
            (x - size, y),
            (x - size//3, y + size//2),
            (x + size, y - size)
        ]
        draw.line(points[0:2], fill=color, width=line_width)
        draw.line(points[1:3], fill=color, width=line_width)