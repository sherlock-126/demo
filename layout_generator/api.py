"""
Public API for layout generator
"""

from typing import Optional, List, Union
from pathlib import Path
from PIL import Image
from content_generator.models import ScriptModel
from .generator import LayoutGenerator as _Generator
from .models import LayoutConfig, RenderResult
from .config import ConfigLoader


class LayoutGenerator:
    """Public API for layout generation"""

    def __init__(self, config: Optional[Union[LayoutConfig, str, dict]] = None):
        """
        Initialize layout generator

        Args:
            config: Can be:
                - LayoutConfig object
                - Path to YAML config file (str)
                - Dictionary with configuration
                - None (uses default config)
        """
        if isinstance(config, LayoutConfig):
            self._generator = _Generator(config=config)
        elif isinstance(config, str):
            self._generator = _Generator(config_path=config)
        elif isinstance(config, dict):
            layout_config = LayoutConfig.from_dict(config)
            self._generator = _Generator(config=layout_config)
        else:
            self._generator = _Generator()

    def generate_from_script(self, script: Union[ScriptModel, str, dict],
                           output_dir: Optional[str] = None) -> RenderResult:
        """
        Generate images from a script

        Args:
            script: Can be:
                - ScriptModel object
                - Path to JSON file (str)
                - Dictionary with script data
            output_dir: Output directory path (optional)

        Returns:
            RenderResult with paths to generated images
        """
        # Convert input to ScriptModel
        if isinstance(script, str):
            # Load from file
            import json
            with open(script, 'r', encoding='utf-8') as f:
                data = json.load(f)
            script_model = ScriptModel(**data)
        elif isinstance(script, dict):
            script_model = ScriptModel(**script)
        else:
            script_model = script

        return self._generator.generate_all(script_model, output_dir)

    def generate_single_slide(self, slide_data: dict, **kwargs) -> Image.Image:
        """
        Generate a single slide image

        Args:
            slide_data: Slide data dictionary
            **kwargs: Additional parameters (title, subtitle, etc.)

        Returns:
            PIL Image object
        """
        from content_generator.models import Slide
        slide = Slide(**slide_data)
        return self._generator.generate_slide(slide, **kwargs)

    def preview_slide(self, script: Union[ScriptModel, str, dict],
                     slide_index: int = 0) -> Image.Image:
        """
        Preview a specific slide without saving

        Args:
            script: Script data (same as generate_from_script)
            slide_index: Index of slide to preview (0-based)

        Returns:
            PIL Image object
        """
        # Convert input to ScriptModel
        if isinstance(script, str):
            import json
            with open(script, 'r', encoding='utf-8') as f:
                data = json.load(f)
            script_model = ScriptModel(**data)
        elif isinstance(script, dict):
            script_model = ScriptModel(**script)
        else:
            script_model = script

        return self._generator.preview(script_model, slide_index)

    @staticmethod
    def create_default_config(output_path: str = "config/default.yaml"):
        """Create a default configuration file"""
        ConfigLoader.save_default_config(output_path)
        return output_path