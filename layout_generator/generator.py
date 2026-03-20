"""
Main layout generator
"""

from PIL import Image
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from content_generator.models import ScriptModel
from .models import LayoutConfig, RenderResult, RenderError
from .config import ConfigLoader
from .renderer import SlideRenderer
from .logger import get_logger

logger = get_logger(__name__)


class LayoutGenerator:
    """Main class for generating layouts from scripts"""

    def __init__(self, config: Optional[LayoutConfig] = None, config_path: Optional[str] = None):
        """Initialize with configuration"""
        if config:
            self.config = config
        else:
            self.config = ConfigLoader.load(config_path)

        self.renderer = SlideRenderer(self.config)

    def generate_all(self, script: ScriptModel, output_dir: Optional[str] = None) -> RenderResult:
        """Generate all slides from a script"""
        if output_dir is None:
            # Create timestamped directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path("output") / timestamp
        else:
            output_dir = Path(output_dir)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        images = []
        thumbnails = []

        try:
            # Generate each slide
            for i, slide in enumerate(script.slides, 1):
                img = self.renderer.render(
                    slide=slide,
                    slide_number=i,
                    total_slides=len(script.slides),
                    title=script.main_title if i == 1 else None,
                    subtitle=script.subtitle if i == 1 else None
                )

                # Save image
                filename = f"slide_{i:02d}.png"
                filepath = output_dir / filename
                img.save(str(filepath), quality=95, optimize=True)
                images.append(str(filepath))

                # Create thumbnail for first slide
                if i == 1:
                    thumbnail = self._create_thumbnail(img)
                    thumb_path = output_dir / "thumbnail.png"
                    thumbnail.save(str(thumb_path), quality=85, optimize=True)
                    thumbnails.append(str(thumb_path))

                logger.info(f"Saved slide {i}/{len(script.slides)} to {filepath}")

        except Exception as e:
            raise RenderError(
                "GENERATION_ERROR",
                f"Failed to generate slides: {str(e)}",
                {"script_topic": script.topic},
                "Check script format and configuration"
            )

        # Create metadata
        metadata = {
            "topic": script.topic,
            "num_slides": len(script.slides),
            "generated_at": datetime.now().isoformat(),
            "output_dir": str(output_dir),
            "config": self.config.dict()
        }

        logger.info(f"Successfully generated {len(images)} slides")

        return RenderResult(
            images=images,
            thumbnails=thumbnails,
            metadata=metadata
        )

    def generate_slide(self, slide: 'Slide', slide_number: int = 1,
                      total_slides: int = 1, title: Optional[str] = None,
                      subtitle: Optional[str] = None) -> Image.Image:
        """Generate a single slide"""
        return self.renderer.render(
            slide=slide,
            slide_number=slide_number,
            total_slides=total_slides,
            title=title,
            subtitle=subtitle
        )

    def _create_thumbnail(self, image: Image.Image, size: tuple = (540, 960)) -> Image.Image:
        """Create thumbnail from image"""
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        return thumbnail

    def preview(self, script: ScriptModel, slide_index: int = 0) -> Image.Image:
        """Preview a specific slide without saving"""
        if slide_index >= len(script.slides):
            raise RenderError(
                "INVALID_SLIDE",
                f"Slide index {slide_index} out of range",
                {"max_index": len(script.slides) - 1},
                "Use valid slide index"
            )

        slide = script.slides[slide_index]
        return self.generate_slide(
            slide=slide,
            slide_number=slide_index + 1,
            total_slides=len(script.slides),
            title=script.main_title if slide_index == 0 else None,
            subtitle=script.subtitle if slide_index == 0 else None
        )