"""
Main slide renderer
"""

from PIL import Image
from typing import Optional
from content_generator.models import Slide
from .models import LayoutConfig
from .components import BackgroundRenderer, TextRenderer, IconRenderer, LogoRenderer
from .logger import get_logger

logger = get_logger(__name__)


class SlideRenderer:
    """Render individual slides"""

    def __init__(self, config: LayoutConfig):
        self.config = config
        self.width = config.layout.width
        self.height = config.layout.height
        self.padding = config.layout.padding
        self.split_ratio = config.layout.split_ratio

        # Initialize component renderers
        self.background_renderer = BackgroundRenderer(
            self.width,
            self.height,
            config.colors.background
        )
        self.text_renderer = TextRenderer(
            {k: v.dict() for k, v in config.fonts.items()},
            config.colors.text
        )
        self.icon_renderer = IconRenderer(config.icons.dict())
        self.logo_renderer = LogoRenderer(config.logo.dict() if config.logo else None)

    def render(self, slide: Slide, slide_number: int = 1, total_slides: int = 1,
              title: Optional[str] = None, subtitle: Optional[str] = None) -> Image.Image:
        """Render a complete slide"""
        # Create background
        img = self.background_renderer.render(self.split_ratio)

        # Add title and subtitle if provided
        if title:
            self.text_renderer.render_title(img, title, y_position=80)
        if subtitle:
            self.text_renderer.render_subtitle(img, subtitle, y_position=160)

        # Render side labels (SAI/ĐÚNG)
        self.text_renderer.render_side_label(
            img,
            slide.left_side.label,
            'left',
            y_position=350
        )
        self.text_renderer.render_side_label(
            img,
            slide.right_side.label,
            'right',
            y_position=350
        )

        # Render icons
        icon_y = 450
        self.icon_renderer.render_wrong_icon(
            img,
            position=(self.width // 4 - 50, icon_y)
        )
        self.icon_renderer.render_right_icon(
            img,
            position=((self.width * 3) // 4 - 50, icon_y)
        )

        # Render content text
        content_y = 600
        self.text_renderer.render_side_content(
            img,
            slide.left_side.text,
            'left',
            y_position=content_y,
            padding=self.padding
        )
        self.text_renderer.render_side_content(
            img,
            slide.right_side.text,
            'right',
            y_position=content_y,
            padding=self.padding
        )

        # Add slide number
        if total_slides > 1:
            self.text_renderer.render_slide_number(img, slide_number, total_slides)

        # Add logo
        self.logo_renderer.render(img)

        logger.info(f"Rendered slide {slide_number}/{total_slides}")

        return img

    def render_title_slide(self, title: str, subtitle: str,
                          topic: Optional[str] = None) -> Image.Image:
        """Render a title slide (optional)"""
        # Create background with neutral color
        img = Image.new('RGB', (self.width, self.height), (255, 255, 255))

        # Center title and subtitle
        self.text_renderer.render_title(img, title, y_position=self.height // 2 - 100)
        self.text_renderer.render_subtitle(img, subtitle, y_position=self.height // 2)

        if topic:
            self.text_renderer.render_subtitle(img, f"Chủ đề: {topic}",
                                             y_position=self.height // 2 + 100)

        # Add logo
        self.logo_renderer.render(img)

        logger.info("Rendered title slide")

        return img