"""
Logo renderer component
"""

from PIL import Image
from pathlib import Path
from typing import Optional, Tuple
from ..utils.image import resize_image_aspect
from ..logger import get_logger

logger = get_logger(__name__)


class LogoRenderer:
    """Render logo/watermark on images"""

    def __init__(self, logo_config: Optional[dict] = None):
        if logo_config:
            self.logo_path = logo_config.get('path')
            self.position = logo_config.get('position', 'top-center')
            self.size = tuple(logo_config.get('size', [200, 80]))
            self.opacity = logo_config.get('opacity', 1.0)
        else:
            self.logo_path = None
            self.position = 'top-center'
            self.size = (200, 80)
            self.opacity = 1.0

        self._logo_cache = None

    def _load_logo(self) -> Optional[Image.Image]:
        """Load and prepare logo"""
        if self._logo_cache is not None:
            return self._logo_cache

        if not self.logo_path:
            return None

        try:
            if Path(self.logo_path).exists():
                logo = Image.open(self.logo_path)
                # Resize to target size
                logo = resize_image_aspect(logo, self.size)

                # Apply opacity if needed
                if self.opacity < 1.0:
                    logo = self._apply_opacity(logo, self.opacity)

                self._logo_cache = logo
                return logo
        except Exception as e:
            logger.warning(f"Failed to load logo {self.logo_path}: {e}")

        return None

    def _apply_opacity(self, img: Image.Image, opacity: float) -> Image.Image:
        """Apply opacity to image"""
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Create a new image with adjusted alpha
        alpha = img.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        img.putalpha(alpha)

        return img

    def render(self, img: Image.Image) -> None:
        """Render logo on image"""
        logo = self._load_logo()
        if not logo:
            return

        # Calculate position
        x, y = self._calculate_position(img.size, logo.size)

        # Paste logo with transparency
        if logo.mode == 'RGBA':
            img.paste(logo, (x, y), logo)
        else:
            img.paste(logo, (x, y))

    def _calculate_position(self, canvas_size: Tuple[int, int],
                          logo_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate logo position based on configuration"""
        canvas_w, canvas_h = canvas_size
        logo_w, logo_h = logo_size
        padding = 30

        positions = {
            'top-left': (padding, padding),
            'top-center': ((canvas_w - logo_w) // 2, padding),
            'top-right': (canvas_w - logo_w - padding, padding),
            'bottom-left': (padding, canvas_h - logo_h - padding),
            'bottom-center': ((canvas_w - logo_w) // 2, canvas_h - logo_h - padding),
            'bottom-right': (canvas_w - logo_w - padding, canvas_h - logo_h - padding),
            'center': ((canvas_w - logo_w) // 2, (canvas_h - logo_h) // 2)
        }

        return positions.get(self.position, positions['top-center'])